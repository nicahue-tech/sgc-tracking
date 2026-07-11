from bitacora import obtener_bitacora
from calculo import calcular_resultados
from reportes import generar_reporte_completo

log = obtener_bitacora("programa_listas")


def ejecutar_sistema():
    try:
        log.info("Inicio de ejecucion automatica del sistema SGC Tracking")
        resultados = calcular_resultados()
        ruta_reporte = generar_reporte_completo(resultados)
        log.info(f"Ejecucion automatica finalizada correctamente. Reporte disponible en: {ruta_reporte}")
    except Exception as error:
        log.error(f"La ejecucion automatica fallo: {error}")


if __name__ == "__main__":
    ejecutar_sistema()
