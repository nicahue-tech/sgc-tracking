import os
from datetime import datetime
import pandas as pd
from bitacora import obtener_bitacora
from datos_entrada import cargar_datos_crudos

log = obtener_bitacora("calculo")

RUTA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
RUTA_NOMINA = os.path.join(RUTA_PROYECTO, "nomina.txt")
RUTA_METAS = os.path.join(RUTA_PROYECTO, "metas.txt")
RUTA_DIAS_HABILES = os.path.join(RUTA_PROYECTO, "dias_habiles.txt")

COL_FECHA = "Fecha de creación"
COL_EJECUTIVO = "Ejecutivo de Venta Movimiento"
COL_TIPO_TRANSACCION = "Tipo transacción"
COL_ESTADO = "Estado"
COL_PRODUCTO_ACUERDO = "Producto (Acuerdo) (Acuerdo)"
COL_ESTADO_ACUERDO = "Estado del acuerdo (Acuerdo) (Acuerdo)"
COL_TIPO_TRANS_ACUERDO = "Tipo Transacción (Acuerdo) (Acuerdo)"
COL_MONTO_ACUERDO = "Monto Final (base)"
COL_MONTO_REAJUSTE = "Variación monto"

ESTADOS_ACUERDO_VALIDOS = ["Nuevo", "Vigente", "Vigente - Nuevo Medio de Pago"]

MESES_ESPANOL = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
}


def cargar_nomina():
    nomina = {}
    with open(RUTA_NOMINA, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split(";")
            if len(partes) != 3:
                continue
            nombre, supervisor, tipo = partes
            nomina[nombre.strip().upper()] = {
                "supervisor": supervisor.strip(),
                "tipo": tipo.strip().upper()
            }
    return nomina


def cargar_metas():
    metas = {}
    with open(RUTA_METAS, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split(";")
            if len(partes) != 3:
                continue
            entidad, tipo_meta, monto = partes
            metas[(entidad.strip(), tipo_meta.strip().upper())] = float(monto)
    return metas


def cargar_dias_habiles_mes():
    dias_por_mes = {}
    with open(RUTA_DIAS_HABILES, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea:
                continue
            mes, dias = linea.split(";")
            dias_por_mes[mes.strip().upper()] = int(dias)
    return dias_por_mes


def calcular_dias_habiles_transcurridos(fecha_referencia):
    primer_dia_mes = fecha_referencia.replace(day=1)
    dias_transcurridos = 0
    dia_actual = primer_dia_mes
    while dia_actual.date() <= fecha_referencia.date():
        if dia_actual.weekday() < 5:
            dias_transcurridos += 1
        dia_actual = dia_actual + pd.Timedelta(days=1)
    return dias_transcurridos


def filtrar_acuerdos(datos):
    filtro = (
        (datos[COL_PRODUCTO_ACUERDO] == "Membresía") &
        (datos[COL_TIPO_TRANSACCION] == "Nuevo acuerdo") &
        (datos[COL_ESTADO_ACUERDO].isin(ESTADOS_ACUERDO_VALIDOS))
    )
    return datos[filtro].copy()


def filtrar_reajustes(datos):
    filtro = (
        (datos[COL_TIPO_TRANSACCION] == "Aumento de aporte") &
        (datos[COL_ESTADO] == "Activo") &
        (datos[COL_PRODUCTO_ACUERDO] == "Membresía") &
        (datos[COL_ESTADO_ACUERDO].isin(ESTADOS_ACUERDO_VALIDOS))
    )
    return datos[filtro].copy()


def calcular_indicadores(monto_acumulado, cantidad_operaciones, dias_transcurridos, dias_totales_mes, meta):
    dias_transcurridos = max(dias_transcurridos, 1)
    promedio_diario_real = monto_acumulado / dias_transcurridos
    proyectado_cierre = promedio_diario_real * dias_totales_mes
    cuota_promedio = monto_acumulado / cantidad_operaciones if cantidad_operaciones > 0 else 0

    indicadores = {
        "acumulado": monto_acumulado,
        "cantidad_operaciones": cantidad_operaciones,
        "cuota_promedio": cuota_promedio,
        "promedio_diario_real": promedio_diario_real,
        "proyectado_cierre": proyectado_cierre,
        "meta": None,
        "porcentaje_avance_meta": None,
        "monto_diario_requerido": None
    }

    if meta is not None:
        dias_restantes = max(dias_totales_mes - dias_transcurridos, 1)
        monto_diario_requerido = (meta - monto_acumulado) / dias_restantes
        porcentaje_avance_meta = (monto_acumulado / meta) * 100 if meta != 0 else 0
        indicadores["meta"] = meta
        indicadores["porcentaje_avance_meta"] = porcentaje_avance_meta
        indicadores["monto_diario_requerido"] = monto_diario_requerido

    return indicadores


def calcular_avance_diario(acuerdos, reajustes, fecha_referencia):
    primer_dia_mes = fecha_referencia.replace(day=1)

    acuerdos_monto_por_dia = acuerdos.groupby(acuerdos[COL_FECHA].dt.date)[COL_MONTO_ACUERDO].sum()
    acuerdos_cantidad_por_dia = acuerdos.groupby(acuerdos[COL_FECHA].dt.date)[COL_MONTO_ACUERDO].count()
    reajustes_monto_por_dia = reajustes.groupby(reajustes[COL_FECHA].dt.date)[COL_MONTO_REAJUSTE].sum()
    reajustes_cantidad_por_dia = reajustes.groupby(reajustes[COL_FECHA].dt.date)[COL_MONTO_REAJUSTE].count()

    avance = []
    dia_actual = primer_dia_mes
    while dia_actual.date() <= fecha_referencia.date():
        fecha_dia = dia_actual.date()

        monto_acuerdo_dia = float(acuerdos_monto_por_dia.get(fecha_dia, 0))
        cantidad_acuerdo_dia = int(acuerdos_cantidad_por_dia.get(fecha_dia, 0))
        cuota_promedio_acuerdo_dia = monto_acuerdo_dia / cantidad_acuerdo_dia if cantidad_acuerdo_dia > 0 else 0

        monto_reajuste_dia = float(reajustes_monto_por_dia.get(fecha_dia, 0))
        cantidad_reajuste_dia = int(reajustes_cantidad_por_dia.get(fecha_dia, 0))
        cuota_promedio_reajuste_dia = monto_reajuste_dia / cantidad_reajuste_dia if cantidad_reajuste_dia > 0 else 0

        avance.append({
            "fecha": fecha_dia,
            "cantidad_acuerdo": cantidad_acuerdo_dia,
            "monto_acuerdo": monto_acuerdo_dia,
            "cuota_promedio_acuerdo": cuota_promedio_acuerdo_dia,
            "cantidad_reajuste": cantidad_reajuste_dia,
            "monto_reajuste": monto_reajuste_dia,
            "cuota_promedio_reajuste": cuota_promedio_reajuste_dia
        })
        dia_actual = dia_actual + pd.Timedelta(days=1)

    return avance


def calcular_resultados(fecha_referencia=None):
    if fecha_referencia is None:
        fecha_referencia = datetime.now()

    nomina = cargar_nomina()
    metas = cargar_metas()
    dias_por_mes = cargar_dias_habiles_mes()

    mes_actual_nombre = MESES_ESPANOL[fecha_referencia.month]
    dias_totales_mes = dias_por_mes.get(mes_actual_nombre, 0)

    dias_transcurridos = calcular_dias_habiles_transcurridos(fecha_referencia)

    datos = cargar_datos_crudos()
    datos[COL_FECHA] = pd.to_datetime(datos[COL_FECHA])
    datos[COL_EJECUTIVO] = datos[COL_EJECUTIVO].astype(str).str.strip().str.upper()

    acuerdos = filtrar_acuerdos(datos)
    reajustes = filtrar_reajustes(datos)

    resultados = {
        "fecha_corte": fecha_referencia,
        "dias_habiles_transcurridos": dias_transcurridos,
        "dias_habiles_totales_mes": dias_totales_mes,
        "dias_habiles_restantes": max(dias_totales_mes - dias_transcurridos, 0),
        "ejecutivos": {},
        "supervisores": {},
        "global": {},
        "avance_diario": calcular_avance_diario(acuerdos, reajustes, fecha_referencia)
    }

    for nombre_ejecutivo, info in nomina.items():
        monto_acuerdo = acuerdos.loc[acuerdos[COL_EJECUTIVO] == nombre_ejecutivo, COL_MONTO_ACUERDO].sum()
        monto_reajuste = reajustes.loc[reajustes[COL_EJECUTIVO] == nombre_ejecutivo, COL_MONTO_REAJUSTE].sum()

        if info["tipo"] == "OUTBOUND":
            meta_acuerdo = metas.get(("Ejecutivo Outbound", "ACUERDO"))
            meta_reajuste = metas.get(("Ejecutivo Outbound", "REAJUSTE"))
        else:
            meta_acuerdo = None
            meta_reajuste = None

        cantidad_acuerdo = int(acuerdos.loc[acuerdos[COL_EJECUTIVO] == nombre_ejecutivo, COL_MONTO_ACUERDO].count())
        cantidad_reajuste = int(reajustes.loc[reajustes[COL_EJECUTIVO] == nombre_ejecutivo, COL_MONTO_REAJUSTE].count())

        resultados["ejecutivos"][nombre_ejecutivo] = {
            "supervisor": info["supervisor"],
            "tipo": info["tipo"],
            "acuerdo": calcular_indicadores(monto_acuerdo, cantidad_acuerdo, dias_transcurridos, dias_totales_mes, meta_acuerdo),
            "reajuste": calcular_indicadores(monto_reajuste, cantidad_reajuste, dias_transcurridos, dias_totales_mes, meta_reajuste)
        }

    supervisores_unicos = set(info["supervisor"] for info in nomina.values())
    for supervisor in supervisores_unicos:
        ejecutivos_del_supervisor = [n for n, i in nomina.items() if i["supervisor"] == supervisor]
        monto_acuerdo = acuerdos.loc[acuerdos[COL_EJECUTIVO].isin(ejecutivos_del_supervisor), COL_MONTO_ACUERDO].sum()
        monto_reajuste = reajustes.loc[reajustes[COL_EJECUTIVO].isin(ejecutivos_del_supervisor), COL_MONTO_REAJUSTE].sum()

        clave_meta = f"Supervisor {supervisor}"
        meta_acuerdo = metas.get((clave_meta, "ACUERDO"))
        meta_reajuste = metas.get((clave_meta, "REAJUSTE"))

        cantidad_acuerdo = int(acuerdos.loc[acuerdos[COL_EJECUTIVO].isin(ejecutivos_del_supervisor), COL_MONTO_ACUERDO].count())
        cantidad_reajuste = int(reajustes.loc[reajustes[COL_EJECUTIVO].isin(ejecutivos_del_supervisor), COL_MONTO_REAJUSTE].count())

        resultados["supervisores"][supervisor] = {
            "acuerdo": calcular_indicadores(monto_acuerdo, cantidad_acuerdo, dias_transcurridos, dias_totales_mes, meta_acuerdo),
            "reajuste": calcular_indicadores(monto_reajuste, cantidad_reajuste, dias_transcurridos, dias_totales_mes, meta_reajuste)
        }

    monto_acuerdo_global = acuerdos[COL_MONTO_ACUERDO].sum()
    cantidad_acuerdo_global = int(acuerdos[COL_MONTO_ACUERDO].count())
    monto_reajuste_global = reajustes[COL_MONTO_REAJUSTE].sum()
    cantidad_reajuste_global = int(reajustes[COL_MONTO_REAJUSTE].count())
    meta_acuerdo_global = metas.get(("Global", "ACUERDO"))
    meta_reajuste_global = metas.get(("Global", "REAJUSTE"))

    resultados["global"] = {
        "acuerdo": calcular_indicadores(monto_acuerdo_global, cantidad_acuerdo_global, dias_transcurridos, dias_totales_mes, meta_acuerdo_global),
        "reajuste": calcular_indicadores(monto_reajuste_global, cantidad_reajuste_global, dias_transcurridos, dias_totales_mes, meta_reajuste_global)
    }

    return resultados
