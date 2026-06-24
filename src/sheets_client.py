import gspread
from src import config

# Columnas del Sheet (1-indexed para gspread)
COL_NOMBRE = 1
COL_VENCIMIENTO = 2
COL_ESTADO = 3
COL_NOTIF_30 = 4
COL_NOTIF_15 = 5
COL_ULTIMA_DIARIA = 6

HEADER_ROW = 1  # fila 1 es el encabezado


def _open_sheet():
    gc = gspread.service_account_from_dict(config.SERVICE_ACCOUNT_INFO)
    return gc.open_by_key(config.SHEET_ID)


def get_documentos():
    """
    Lee la pestaña Documentos y devuelve lista de dicts con:
    row_index (fila real en el sheet, empezando en 2), nombre, vencimiento,
    estado, notif_30, notif_15, ultima_diaria.
    """
    sh = _open_sheet()
    ws = sh.worksheet(config.DOCUMENTOS_TAB)
    rows = ws.get_all_records(numericise_ignore=["all"])

    documentos = []
    for i, row in enumerate(rows):
        nombre = str(row.get("Nombre", "")).strip()
        if not nombre:
            continue
        documentos.append({
            "row_index": i + 2,  # fila real (1 es header, datos desde 2)
            "nombre": nombre,
            "vencimiento": str(row.get("Vencimiento", "")).strip(),
            "estado": str(row.get("Estado", "Activo")).strip(),
            "notif_30": str(row.get("Notif_30_enviada", "")).strip(),
            "notif_15": str(row.get("Notif_15_enviada", "")).strip(),
            "ultima_diaria": str(row.get("Ultima_notif_diaria", "")).strip(),
        })
    return documentos


def marcar_notif_30(row_index: int):
    sh = _open_sheet()
    ws = sh.worksheet(config.DOCUMENTOS_TAB)
    ws.update_cell(row_index, COL_NOTIF_30, "Sí")


def marcar_notif_15(row_index: int):
    sh = _open_sheet()
    ws = sh.worksheet(config.DOCUMENTOS_TAB)
    ws.update_cell(row_index, COL_NOTIF_15, "Sí")


def marcar_ultima_diaria(row_index: int, fecha_hoy: str):
    """fecha_hoy en formato YYYY-MM-DD"""
    sh = _open_sheet()
    ws = sh.worksheet(config.DOCUMENTOS_TAB)
    ws.update_cell(row_index, COL_ULTIMA_DIARIA, fecha_hoy)
