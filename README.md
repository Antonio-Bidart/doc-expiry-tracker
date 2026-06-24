# Doc Expiry Tracker

Te avisa por mail cuando algún documento o tarjeta está por vencer.
Corre solo todos los días vía GitHub Actions, sin servidor propio.

## Qué hace

Cargás tus documentos (DNI, pasaporte, tarjetas, seguros, etc.) en un Google Sheet
con su fecha de vencimiento. El sistema te avisa automáticamente:

- **30 días antes:** primer aviso (una sola vez)
- **15 días antes:** recordatorio de confirmación (una sola vez)  
- **Última semana:** aviso diario hasta que lo renueves
- **Ya vencido:** aviso diario

Una vez que renovás el documento, cambiás el Estado a "Renovado" y deja de avisar.

## Setup del Sheet

Creá un Sheet nuevo y compartilo con el email de la service account (Editor).
Agregá una pestaña llamada **Documentos** con estos headers en la fila 1:

| Nombre | Vencimiento | Estado | Notif_30_enviada | Notif_15_enviada | Ultima_notif_diaria |
|---|---|---|---|---|---|
| DNI | 15/08/2026 | Activo | | | |
| Pasaporte | 03/12/2027 | Activo | | | |

- **Vencimiento:** formato DD/MM/YYYY o YYYY-MM-DD
- **Estado:** Activo / Renovado / Inactivo
- Las últimas tres columnas las completa el script solo — no las toques a mano

## GitHub Secrets necesarios

| Secret | Valor |
|---|---|
| `DOC_EXPIRY_SHEET_ID` | ID del Sheet nuevo (distinto al de NBA Watchlist) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | El mismo JSON que ya tenés en NBA Watchlist |
| `GMAIL_ADDRESS` | El mismo mail |
| `GMAIL_APP_PASSWORD` | El mismo app password |
| `NOTIFY_TO` | A dónde llegan los avisos |

## Correrlo local

```bash
pip install -r requirements.txt
copy .env.example .env   # completar con tus datos
python run.py
```
