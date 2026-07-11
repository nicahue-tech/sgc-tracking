import os
import smtplib
from email.message import EmailMessage
from bitacora import obtener_bitacora
from calculo import calcular_resultados

log = obtener_bitacora("notificaciones")

RUTA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
RUTA_CREDENCIALES = os.path.join(RUTA_PROYECTO, "credenciales_correo.txt")
RUTA_DESTINATARIOS = os.path.join(RUTA_PROYECTO, "destinatarios.txt")
RUTA_REPORTE = os.path.join(RUTA_PROYECTO, "reportes_generados", "dashboard_sgc_tracking.xlsx")

ASUNTO_CORREO = "Informe Tracking"


def leer_credenciales():
    credenciales = {}
    with open(RUTA_CREDENCIALES, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            credenciales[clave.strip()] = valor.strip()
    return credenciales


def leer_destinatarios():
    destinatarios = []
    with open(RUTA_DESTINATARIOS, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if linea:
                destinatarios.append(linea)
    return destinatarios


def construir_cuerpo_html(resultados):
    acuerdo = resultados["global"]["acuerdo"]
    reajuste = resultados["global"]["reajuste"]

    def fila(etiqueta, valor_acuerdo, valor_reajuste):
        return f"<tr><td>{etiqueta}</td><td>{valor_acuerdo}</td><td>{valor_reajuste}</td></tr>"

    porcentaje_acuerdo = "No aplica" if acuerdo["porcentaje_avance_meta"] is None else f"{round(acuerdo['porcentaje_avance_meta'], 1)}%"
    porcentaje_reajuste = "No aplica" if reajuste["porcentaje_avance_meta"] is None else f"{round(reajuste['porcentaje_avance_meta'], 1)}%"
    meta_acuerdo_mostrada = round(acuerdo["meta"]) if acuerdo["meta"] is not None else "No aplica"
    meta_reajuste_mostrada = round(reajuste["meta"]) if reajuste["meta"] is not None else "No aplica"

    tabla = f"""
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; font-family: Arial, sans-serif;">
        <tr style="font-weight:bold; background-color:#f0f0f0;">
            <td>Indicador</td><td>Acuerdos</td><td>Reajustes</td>
        </tr>
        {fila("Monto acumulado", round(acuerdo["acumulado"]), round(reajuste["acumulado"]))}
        {fila("Proyectado a cierre", round(acuerdo["proyectado_cierre"]), round(reajuste["proyectado_cierre"]))}
        {fila("Meta", meta_acuerdo_mostrada, meta_reajuste_mostrada)}
        {fila("Porcentaje de avance", porcentaje_acuerdo, porcentaje_reajuste)}
    </table>
    """

    fecha_texto = resultados["fecha_corte"].strftime("%d-%m-%Y %H:%M")

    cuerpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <p>Estimados,</p>
        <p>Adjunto el informe de tracking del call center, actualizado al {fecha_texto}.</p>
        <p>A continuacion un resumen general del avance y la proyeccion:</p>
        {tabla}
        <p>El detalle completo por supervisor y por ejecutivo se encuentra en el archivo adjunto.</p>
        <p>Saludos.</p>
    </body>
    </html>
    """
    return cuerpo


def enviar_reporte():
    try:
        credenciales = leer_credenciales()
        destinatarios = leer_destinatarios()

        if not os.path.isfile(RUTA_REPORTE):
            log.error(f"No se encontro el archivo de reporte en: {RUTA_REPORTE}")
            raise FileNotFoundError(RUTA_REPORTE)

        resultados = calcular_resultados()
        cuerpo_html = construir_cuerpo_html(resultados)

        mensaje = EmailMessage()
        mensaje["Subject"] = ASUNTO_CORREO
        mensaje["From"] = credenciales["remitente"]
        mensaje["To"] = ", ".join(destinatarios)
        mensaje.set_content("Este correo requiere un cliente compatible con HTML para verse correctamente.")
        mensaje.add_alternative(cuerpo_html, subtype="html")

        with open(RUTA_REPORTE, "rb") as archivo_adjunto:
            datos_adjunto = archivo_adjunto.read()
        mensaje.add_attachment(
            datos_adjunto,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="dashboard_sgc_tracking.xlsx"
        )

        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(credenciales["remitente"], credenciales["clave_app"])
            servidor.send_message(mensaje)

        log.info(f"Correo enviado correctamente a: {', '.join(destinatarios)}")

    except Exception as error:
        log.error(f"Fallo el envio del correo: {error}")
        raise


if __name__ == "__main__":
    enviar_reporte()
