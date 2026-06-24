import logging
from datetime import date
from src import config, sheets_client, rules, notifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

ASUNTOS = {
    "notif_30":     "📅 Vencimiento en 30 días",
    "notif_15":     "⏰ Vencimiento en 15 días",
    "diario":       "🔴 Vencimiento inminente",
    "vencido_diario": "⚠️ Documento vencido",
}


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
        logger.info("No hay documentos cargados, nada que procesar.")
        return

    for doc in documentos:
        logger.info(f"Evaluando: {doc['nombre']} (vence: {doc['vencimiento']})")
        try:
            acciones = rules.evaluar_documento(doc, hoy)
        except Exception as e:
            logger.exception(f"Error evaluando '{doc['nombre']}'")
            _notificar_error(f"Error evaluando '{doc['nombre']}': {e}")
            continue

        for accion in acciones:
            tipo = accion["tipo"]

            if tipo == "error_fecha":
                logger.warning(accion["mensaje"])
                _notificar_error(accion["mensaje"])
                continue

            try:
                asunto = f"{ASUNTOS.get(tipo, 'Aviso de vencimiento')}: {doc['nombre']}"
                notifier.send_email(subject=asunto, body=accion["mensaje"])
                notificaciones += 1
                logger.info(f"Mail enviado para '{doc['nombre']}' ({tipo})")

                # Actualizar Sheet según tipo (idempotencia)
                if tipo == "notif_30":
                    sheets_client.marcar_notif_30(doc["row_index"])

                elif tipo == "notif_15":
                    sheets_client.marcar_notif_15(doc["row_index"])

                elif tipo == "diario":
                    sheets_client.marcar_ultima_diaria(doc["row_index"], hoy_str)

                elif tipo == "vencido_diario":
                    sheets_client.marcar_ultima_diaria(doc["row_index"], hoy_str)
                    # Actualizar Estado a Vencido solo si no estaba ya marcado
                    if accion.get("actualizar_estado"):
                        sheets_client.marcar_estado_vencido(doc["row_index"])
                        logger.info(f"Estado de '{doc['nombre']}' actualizado a Vencido")

            except Exception as e:
                logger.exception(f"Error procesando '{tipo}' para '{doc['nombre']}'")
                _notificar_error(f"Falló el aviso de '{doc['nombre']}' ({tipo}): {e}")

    logger.info(f"=== Corrida terminada. Notificaciones enviadas: {notificaciones} ===")


def _notificar_error(detalle: str):
    try:
        notifier.send_email(subject="⚠️ Error en Doc Expiry Tracker", body=detalle)
    except Exception:
        logger.exception("Encima falló el mail de error.")


if __name__ == "__main__":
    run()
