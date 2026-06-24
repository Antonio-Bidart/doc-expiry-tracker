import os
import json
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.environ["SHEET_ID"]
DOCUMENTOS_TAB = os.environ.get("DOCUMENTOS_TAB", "Documentos")
SERVICE_ACCOUNT_INFO = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
NOTIFY_TO = os.environ.get("NOTIFY_TO", GMAIL_ADDRESS)
