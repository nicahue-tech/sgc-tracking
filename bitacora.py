import logging
import os

RUTA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
RUTA_LOG = os.path.join(RUTA_PROYECTO, "sistema.log")


def obtener_bitacora(nombre_modulo):
    logger = logging.getLogger(nombre_modulo)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        manejador_archivo = logging.FileHandler(RUTA_LOG, encoding="utf-8")
        manejador_archivo.setFormatter(formato)
        logger.addHandler(manejador_archivo)

        manejador_consola = logging.StreamHandler()
        manejador_consola.setFormatter(formato)
        logger.addHandler(manejador_consola)

    return logger


if __name__ == "__main__":
    log = obtener_bitacora("prueba_bitacora")
    log.info("Bitacora inicializada correctamente, este es un mensaje de prueba")
    log.warning("Este es un mensaje de advertencia de prueba")
    log.error("Este es un mensaje de error de prueba")
