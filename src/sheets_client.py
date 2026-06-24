import gspread
from src import config

# Columnas del Sheet (1-indexed para gspread)
COL_NOMBRE = 1
COL_VENCIMIENTO = 2
COL_ESTADO = 3
COL_NOTIF_30 = 4
COL_NOTIF_15 = 5
COL_ULTIMA_DIARIA = 6

_sheet_cache = None


def _open_worksheet():
    """Abre el worksheet y lo cachea para evitar múltiples conexiones en la misma corrida."""
    global _sheet_cache
    if _sheet_cache is None:
        gc = gspread.service_account_from_dict(config.SERVICE_ACCOUNT_INFO)
        sh = gc.open_by_key(config.SHEET_ID)
        _sheet_cache = sh.worksheet(config.DOCUMENTOS_TAB)
    return _sheet_cache


def get_documentos():
    """
    Lee la pestaña Documentos. Devuelve lista de dicts con row_index incluido.
    numericise_ignore=["all"] evita que gspread convierta fechas o números
    automáticamente (lo que causaría problemas al comparar strings).
    """
    ws = _open_worksheet()
    rows = ws.get_all_records(numericise_ignore=["all"])

    documentos = []
    for i, row in enumerate(rows):
        nombre = str(row.get("Nombre", "")).strip()
        if not nombre:
            continue
        documentos.append({
            "row_index": i + 2,  # fila real (1 = header, datos desde fila 2)
            "nombre": nombre,
            "vencimiento": str(row.get("Vencimiento", "")).strip(),
            "estado": str(row.get("Estado", "Activo")).strip(),
            "notif_30": str(row.get("Notif_30_enviada", "")).strip(),
            "notif_15": str(row.get("Notif_15_enviada", "")).strip(),
            "ultima_diaria": str(row.get("Ultima_notif_diaria", "")).strip(),
        })
    return documentos


def marcar_notif_30(row_index: int):
    _open_worksheet().update_cell(row_index, COL_NOTIF_30, "Sí")


def marcar_notif_15(row_index: int):
    _open_worksheet().update_cell(row_index, COL_NOTIF_15, "Sí")


def marcar_ultima_diaria(row_index: int, fecha_hoy: str):
    """fecha_hoy en formato YYYY-MM-DD"""
    _open_worksheet().update_cell(row_index, COL_ULTIMA_DIARIA, fecha_hoy)


def marcar_estado_vencido(row_index: int):
    _open_worksheet().update_cell(row_index, COL_ESTADO, "Vencido")
