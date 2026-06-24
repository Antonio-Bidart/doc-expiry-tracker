from datetime import date


def parsear_fecha(fecha_str: str):
    """Acepta DD/MM/YYYY o YYYY-MM-DD."""
    if not fecha_str:
        return None
    # YYYY-MM-DD
    if "-" in fecha_str:
        try:
            return date.fromisoformat(fecha_str.strip())
        except ValueError:
            return None
    # DD/MM/YYYY
    if "/" in fecha_str:
        try:
            partes = fecha_str.strip().split("/")
            if len(partes) != 3:
                return None
            dia, mes, anio = int(partes[0]), int(partes[1]), int(partes[2])
            return date(anio, mes, dia)
        except (ValueError, IndexError):
            return None
    return None


def evaluar_documento(doc: dict, hoy: date):
    """
    Devuelve lista de acciones a tomar para este documento.
    Cada acción es un dict: {tipo, dias_restantes, mensaje}
    """
    estado = doc["estado"].lower().strip()

    # Documentos renovados o inactivos no generan nada
    if estado in ("renovado", "inactivo"):
        return []

    fecha = parsear_fecha(doc["vencimiento"])
    if fecha is None:
        return [{
            "tipo": "error_fecha",
            "dias_restantes": None,
            "mensaje": (
                f"No pude leer la fecha de '{doc['nombre']}': '{doc['vencimiento']}'. "
                f"Usá el formato DD/MM/YYYY o YYYY-MM-DD."
            )
        }]

    dias = (fecha - hoy).days
    acciones = []

    # --- Vencido (dias <= 0) ---
    # Aviso diario. También marcamos el estado como Vencido si no lo está.
    if dias <= 0:
        hoy_str = hoy.isoformat()
        if doc["ultima_diaria"] != hoy_str:
            acciones.append({
                "tipo": "vencido_diario",
                "dias_restantes": dias,
                "actualizar_estado": estado != "vencido",  # marcar Estado=Vencido solo si no lo está ya
                "mensaje": (
                    f"⚠️ '{doc['nombre']}' venció hace {abs(dias)} día(s) "
                    f"(vencimiento: {doc['vencimiento']}). Renovalo cuanto antes."
                )
            })

    # --- Última semana (1–7 días) → aviso diario ---
    elif 1 <= dias <= 7:
        hoy_str = hoy.isoformat()
        if doc["ultima_diaria"] != hoy_str:
            acciones.append({
                "tipo": "diario",
                "dias_restantes": dias,
                "mensaje": (
                    f"🔴 '{doc['nombre']}' vence en {dias} día(s) "
                    f"({doc['vencimiento']}). ¡Renovalo ya!"
                )
            })

    # --- 15 días → una sola vez (rango 13–15 por si el cron falló un día) ---
    elif 13 <= dias <= 15:
        if doc["notif_15"] != "Sí":
            acciones.append({
                "tipo": "notif_15",
                "dias_restantes": dias,
                "mensaje": (
                    f"🟡 '{doc['nombre']}' vence en {dias} día(s) "
                    f"({doc['vencimiento']}). Quedan dos semanas — empezá a gestionarlo."
                )
            })

    # --- 30 días → una sola vez (rango 28–30) ---
    elif 28 <= dias <= 30:
        if doc["notif_30"] != "Sí":
            acciones.append({
                "tipo": "notif_30",
                "dias_restantes": dias,
                "mensaje": (
                    f"🟢 '{doc['nombre']}' vence en {dias} día(s) "
                    f"({doc['vencimiento']}). Primer aviso."
                )
            })

    return acciones
