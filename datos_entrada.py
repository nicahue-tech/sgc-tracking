import os
import pandas as pd
from bitacora import obtener_bitacora

log = obtener_bitacora("datos_entrada")

RUTA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
RUTA_CONFIG = os.path.join(RUTA_PROYECTO, "config.txt")


def leer_configuracion():
    configuracion = {}
    try:
        with open(RUTA_CONFIG, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea or "=" not in linea:
                    continue
                clave, valor = linea.split("=", 1)
                configuracion[clave.strip()] = valor.strip()
        log.info("Configuracion leida correctamente desde config.txt")
    except FileNotFoundError:
        log.error("No se encontro el archivo config.txt en la carpeta del proyecto")
        raise
    except Exception as error:
        log.error(f"Error inesperado leyendo config.txt: {error}")
        raise

    return configuracion


def cargar_datos_crudos():
    configuracion = leer_configuracion()

    ruta_informes = configuracion.get("ruta_informes")
    nombre_archivo = configuracion.get("nombre_archivo")

    if not ruta_informes or not nombre_archivo:
        log.error("Faltan claves ruta_informes o nombre_archivo dentro de config.txt")
        raise ValueError("config.txt esta incompleto")

    ruta_completa = os.path.join(ruta_informes, nombre_archivo)

    if not os.path.isfile(ruta_completa):
        log.error(f"No se encontro el archivo csv en la ruta esperada: {ruta_completa}")
        raise FileNotFoundError(f"No existe el archivo: {ruta_completa}")

    try:
        datos = pd.read_csv(ruta_completa, encoding="utf-8-sig")
        log.info(f"Archivo csv cargado correctamente, con {len(datos)} filas y {len(datos.columns)} columnas")
    except Exception as error:
        log.error(f"Error inesperado leyendo el archivo csv: {error}")
        raise

    return datos


if __name__ == "__main__":
    datos = cargar_datos_crudos()
    log.info("Prueba de datos_entrada finalizada correctamente")
