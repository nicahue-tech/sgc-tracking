codigo_anterior = '''from bitacora import obtener_bitacora
from calculo import calcular_resultados
from reportes import generar_reporte_completo
from correo_compensatorio import descargar_reporte_compensatorio

log = obtener_bitacora("programa_listas")


def ejecutar_sistema():
    try:
        log.info("Inicio de ejecucion automatica del sistema SGC Tracking")

        try:
            descargar_reporte_compensatorio()
        except Exception as error_compensatorio:
            log.error(f"No se pudo descargar el reporte de Compensatorio, se continua sin el: {error_compensatorio}")

        resultados = calcular_resultados()
        ruta_reporte = generar_reporte_completo(resultados)
        log.info(f"Ejecucion automatica finalizada correctamente. Reporte disponible en: {ruta_reporte}")
    except Exception as error:
        log.error(f"La ejecucion automatica fallo: {error}")'''

codigo_nuevo = '''from bitacora import obtener_bitacora
from calculo import calcular_resultados
from reportes import generar_reporte_completo
from correo_compensatorio import descargar_reporte_compensatorio
from subir_sgc import subir_csv_a_flask

log = obtener_bitacora("programa_listas")


def ejecutar_sistema():
    try:
        log.info("Inicio de ejecucion automatica del sistema SGC Tracking")

        try:
            descargar_reporte_compensatorio()
        except Exception as error_compensatorio:
            log.error(f"No se pudo descargar el reporte de Compensatorio, se continua sin el: {error_compensatorio}")

        resultados = calcular_resultados()
        ruta_reporte = generar_reporte_completo(resultados)
        log.info(f"Ejecucion automatica finalizada correctamente. Reporte disponible en: {ruta_reporte}")

        try:
            subir_csv_a_flask()
        except Exception as error_subida:
            log.error(f"No se pudo subir el csv al sistema web nuevo, se continua igual: {error_subida}")
    except Exception as error:
        log.error(f"La ejecucion automatica fallo: {error}")'''

with open("programa_listas.py", "r", encoding="utf-8") as archivo:
    contenido = archivo.read()

if codigo_anterior not in contenido:
    print("No se encontró el texto exacto a reemplazar. No se modificó nada, revisemos juntos.")
else:
    contenido = contenido.replace(codigo_anterior, codigo_nuevo, 1)
    with open("programa_listas.py", "w", encoding="utf-8") as archivo:
        archivo.write(contenido)
    print("subir_csv_a_flask conectado correctamente dentro de programa_listas.py.")
