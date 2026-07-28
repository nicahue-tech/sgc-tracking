#!/usr/bin/env python3
"""
correo_compensatorio.py

Descarga automáticamente, vía IMAP, el archivo Excel de Cumplimiento
Ejecutivo con Compensatorio que llega cada mañana como adjunto de correo.

Este archivo es solo informativo, no se relaciona ni se cruza con los
nombres de ejecutivos del resto del sistema. Se sobrescribe cada vez
que se descarga, sin guardar historial de días anteriores.
"""

import imaplib
import email
import os
import sys
from email.header import decode_header

# ----------------------------------------------------------------------
# Configuración. Ajustar estas rutas si no coinciden con las de config.txt
# ----------------------------------------------------------------------

RUTA_CREDENCIALES = os.path.expanduser(
    "~/proyectos/sgc_tracking/credenciales_correo.txt"
)

RUTA_SALIDA = os.path.expanduser(
    "~/Library/CloudStorage/OneDrive-FundacionHogardeCristo/Escritorio/informes/cumplimiento_ejecutivos.xlsx"
)

SERVIDOR_IMAP = "imap.gmail.com"
PUERTO_IMAP = 993

# Palabra clave que debe contener el nombre del archivo adjunto
PALABRA_CLAVE_ADJUNTO = "compensatorio"


def extraer_valor(linea):
    """
    Cada línea del archivo de credenciales viene con una etiqueta antes
    del signo igual, por ejemplo remitente=correo@gmail.com o
    clave_app=xxxxxxxxxxxxxxxx. Esta función devuelve solo lo que hay
    después del signo igual, sin la etiqueta.
    """
    if "=" in linea:
        return linea.split("=", 1)[1].strip()
    return linea.strip()


def leer_credenciales(ruta):
    """
    Lee el archivo de credenciales de correo.
    Primera línea: remitente=dirección de correo.
    Segunda línea: clave_app=contraseña de aplicación.
    """
    with open(ruta, "r", encoding="utf-8") as archivo:
        lineas = [linea.strip() for linea in archivo.readlines()]

    if len(lineas) < 2:
        raise ValueError(
            "El archivo de credenciales debe tener al menos dos líneas: "
            "remitente en la primera y clave_app en la segunda."
        )

    remitente = extraer_valor(lineas[0])
    clave = extraer_valor(lineas[1])
    return remitente, clave


def conectar_imap(remitente, clave):
    """
    Abre una conexión IMAP autenticada contra Gmail.
    """
    conexion = imaplib.IMAP4_SSL(SERVIDOR_IMAP, PUERTO_IMAP)
    conexion.login(remitente, clave)
    return conexion


def buscar_uid_mas_reciente(conexion):
    """
    Busca, usando la extensión de búsqueda propia de Gmail, el correo
    más reciente que tenga un adjunto cuyo nombre contenga la palabra
    clave, sin importar el asunto ni quién lo haya reenviado.
    """
    conexion.select("INBOX", readonly=True)

    criterio = '"filename:{} has:attachment"'.format(PALABRA_CLAVE_ADJUNTO)
    tipo, datos = conexion.uid("search", None, "X-GM-RAW", criterio)

    if tipo != "OK":
        raise RuntimeError("La búsqueda IMAP en Gmail falló.")

    uids = datos[0].split()

    if not uids:
        return None

    # El último UID de la lista es el correo más reciente que coincide
    return uids[-1]


def extraer_adjunto(conexion, uid):
    """
    Descarga el correo completo sin marcarlo como leído, y devuelve
    el contenido binario del adjunto que coincide con la palabra clave,
    junto con su nombre de archivo original.
    """
    tipo, datos = conexion.uid("fetch", uid, "(BODY.PEEK[])")

    if tipo != "OK" or not datos or datos[0] is None:
        raise RuntimeError("No se pudo descargar el contenido del correo.")

    mensaje_bytes = datos[0][1]
    mensaje = email.message_from_bytes(mensaje_bytes)

    for parte in mensaje.walk():
        nombre_adjunto = parte.get_filename()

        if not nombre_adjunto:
            continue

        nombre_decodificado = decode_header(nombre_adjunto)[0][0]
        if isinstance(nombre_decodificado, bytes):
            nombre_decodificado = nombre_decodificado.decode(errors="ignore")

        if PALABRA_CLAVE_ADJUNTO in nombre_decodificado.lower():
            contenido = parte.get_payload(decode=True)
            return contenido, nombre_decodificado

    return None, None


def guardar_adjunto(contenido, ruta_destino):
    """
    Guarda el adjunto en disco, sobrescribiendo cualquier versión
    anterior. No se conserva historial de días previos.
    """
    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
    with open(ruta_destino, "wb") as archivo_salida:
        archivo_salida.write(contenido)


def descargar_reporte_compensatorio():
    """
    Función principal. Devuelve True si el archivo se descargó y
    guardó correctamente, False si no había ningún correo nuevo que
    coincidiera con la búsqueda.
    """
    remitente, clave = leer_credenciales(RUTA_CREDENCIALES)
    conexion = conectar_imap(remitente, clave)

    try:
        uid = buscar_uid_mas_reciente(conexion)

        if uid is None:
            print("No se encontró ningún correo con el adjunto Compensatorio.")
            return False

        contenido, nombre_adjunto = extraer_adjunto(conexion, uid)

        if contenido is None:
            print("Se encontró el correo, pero no el adjunto esperado dentro de él.")
            return False

        guardar_adjunto(contenido, RUTA_SALIDA)
        print("Adjunto '{}' guardado en: {}".format(nombre_adjunto, RUTA_SALIDA))
        return True

    finally:
        conexion.logout()


if __name__ == "__main__":
    exito = descargar_reporte_compensatorio()
    sys.exit(0 if exito else 1)
