import logging
from datetime import date
from src import config, sheets_client, rules, notifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run():
    logger.info("=== Arrancando corrida de Doc Expiry Tracker ===")
    hoy = date.today()
    hoy_str = hoy.isoformat()
    notificaciones = 0

    try:
        documentos = sheets_client.get_documentos()
    except Exception as e:
        logger.exception("No se pudo leer el Sheet")
        _notificar_error(f"No pude leer el Sheet de documentos: {e}")
        return

    if not documentos:
        logger.info("No hay documentos cargados.")
        return

    for doc in documentos:
        try:
            acciones = rules.evaluar_documento(doc, hoy)
        except Exception as e:
            logger.exception(f"Error evaluando '{doc['nombre']}'")
            continue

        for accion in acciones:
            tipo = accion["tipo"]
            mensaje = accion["mensaje"]

            if tipo == "error_fecha":
                _notificar_error(mensaje)
                continue

            try:
                asunto = {
                    "notif_30": f"📅 Vencimiento en 30 días: {doc['nombre']}",
                    "notif_15": f"⏰ Vencimiento en 15 días: {doc['nombre']}",
                    "diario":   f"🔴 Vencimiento en {accion['dias_restantes']} día(s): {doc['nombre']}",
                    "vencido":  f"⚠️ Documento vencido: {doc['nombre']}",
                }.get(tipo, "Aviso de vencimiento")

                notifier.send_email(subject=asunto, body=mensaje)
                notificaciones += 1

                # Actualizar Sheet según tipo (idempotencia)
                if tipo == "notif_30":
                    sheets_client.marcar_notif_30(doc["row_index"])
                elif tipo == "notif_15":
                    sheets_client.marcar_notif_15(doc["row_index"])
                elif tipo in ("diario", "vencido"):
                    sheets_client.marcar_ultima_diaria(doc["row_index"], hoy_str)

            except Exception as e:
                logger.exception(f"Error procesando acción '{tipo}' para '{doc['nombre']}'")
                _notificar_error(f"Falló el aviso de '{doc['nombre']}' ({tipo}): {e}")

    logger.info(f"=== Corrida terminada. Notificaciones enviadas: {notificaciones} ===")


def _notificar_error(detalle: str):
    try:
        notifier.send_email(subject="⚠️ Error en Doc Expiry Tracker", body=detalle)
    except Exception:
        logger.exception("Encima falló el mail de error.")


if __name__ == "__main__":
    run()
