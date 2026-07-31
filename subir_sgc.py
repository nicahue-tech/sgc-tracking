import os
import requests
from bitacora import obtener_bitacora

log = obtener_bitacora("subir_sgc")

RUTA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
RUTA_CONFIG = os.path.join(RUTA_PROYECTO, "config.txt")
RUTA_CONFIG_IMPORTACION = os.path.join(RUTA_PROYECTO, "config_importacion.txt")


def _leer_archivo_clave_valor(ruta):
    configuracion = {}
    with open(ruta, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            configuracion[clave.strip()] = valor.strip()
    return configuracion


def subir_csv_a_flask():
    configuracion = _leer_archivo_clave_valor(RUTA_CONFIG)
    configuracion_importacion = _leer_archivo_clave_valor(RUTA_CONFIG_IMPORTACION)

    ruta_informes = configuracion.get("ruta_informes")
    nombre_archivo = configuracion.get("nombre_archivo")
    url_importacion = configuracion_importacion.get("url_importacion")
    token = configuracion_importacion.get("token")

    if not ruta_informes or not nombre_archivo or not url_importacion or not token:
        log.error("Faltan datos en config.txt o config_importacion.txt, no se sube el archivo")
        return

    ruta_completa = os.path.join(ruta_informes, nombre_archivo)

    if not os.path.isfile(ruta_completa):
        log.error(f"No se encontro el archivo csv en la ruta esperada: {ruta_completa}")
        return

    try:
        with open(ruta_completa, "rb") as archivo_csv:
            respuesta = requests.post(
                url_importacion,
                headers={"X-Token-Importacion": token},
                files={"archivo": archivo_csv},
                timeout=60,
            )

        if respuesta.status_code == 200:
            log.info(f"Subida a Flask exitosa: {respuesta.json()}")
        else:
            log.error(f"Subida a Flask fallo con codigo {respuesta.status_code}: {respuesta.text}")
    except Exception as error:
        log.error(f"Error inesperado subiendo el csv a Flask: {error}")


if __name__ == "__main__":
    subir_csv_a_flask()
