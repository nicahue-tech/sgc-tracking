from bitacora import obtener_bitacora
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
        log.error(f"La ejecucion automatica fallo: {error}")


if __name__ == "__main__":
    ejecutar_sistema()
