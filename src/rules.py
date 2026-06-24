from datetime import date


def parsear_fecha(fecha_str: str):
    """Acepta DD/MM/YYYY o YYYY-MM-DD."""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return date.fromisoformat(fecha_str) if fmt == "%Y-%m-%d" else date(*reversed([int(x) for x in fecha_str.split("/")]))
        except Exception:
            continue
    return None


def evaluar_documento(doc: dict, hoy: date):
    """
    Devuelve lista de acciones a tomar para este documento.
    Cada acción es un dict: {tipo, dias_restantes, mensaje}
    """
    if doc["estado"].lower() in ("renovado", "inactivo"):
        return []

    fecha = parsear_fecha(doc["vencimiento"])
    if fecha is None:
        return [{"tipo": "error_fecha", "dias_restantes": None,
                 "mensaje": f"No pude leer la fecha de vencimiento de '{doc['nombre']}': '{doc['vencimiento']}'"}]

    dias = (fecha - hoy).days
    acciones = []

    # Vencido
    if dias < 0:
        acciones.append({
            "tipo": "vencido",
            "dias_restantes": dias,
            "mensaje": f"⚠️ '{doc['nombre']}' venció hace {abs(dias)} día(s) ({doc['vencimiento']}). Renovalo cuanto antes."
        })

    # Último semana → aviso diario
    elif dias <= 7:
        hoy_str = hoy.isoformat()
        if doc["ultima_diaria"] != hoy_str:
            acciones.append({
                "tipo": "diario",
                "dias_restantes": dias,
                "mensaje": f"🔴 '{doc['nombre']}' vence en {dias} día(s) ({doc['vencimiento']}). ¡Renovalo ya!"
            })

    # 15 días → confirmación (una sola vez, rango 13-15 por si el cron falló un día)
    elif 13 <= dias <= 15:
        if doc["notif_15"] != "Sí":
            acciones.append({
                "tipo": "notif_15",
                "dias_restantes": dias,
                "mensaje": f"🟡 '{doc['nombre']}' vence en {dias} día(s) ({doc['vencimiento']}). Recordatorio: quedan dos semanas."
            })

    # 30 días → primer aviso (una sola vez, rango 28-30)
    elif 28 <= dias <= 30:
        if doc["notif_30"] != "Sí":
            acciones.append({
                "tipo": "notif_30",
                "dias_restantes": dias,
                "mensaje": f"🟢 '{doc['nombre']}' vence en {dias} día(s) ({doc['vencimiento']}). Primer aviso."
            })

    return acciones
