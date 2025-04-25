import os
import gspread
from google.auth.transport.requests import Request
from google.auth import load_credentials_from_file
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

google_key = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
sheet_id = os.getenv('SHEET_ID')

if google_key and sheet_id:
    logger.info("[Credentials] Loaded successfully")
else:
    logger.error("[Credentials] Error loading")
    exit()

try:
    credential = load_credentials_from_file(google_key, SCOPES)[0]
    logger.info("[Credentials] Authentication successful")
except Exception as error:
    logger.error(f"[Credentials] Error loading credentials: {error}")
    exit()

client_authentication = gspread.authorize(credential)

try:
    sheet = client_authentication.open_by_key(sheet_id).sheet1
    logger.info("[Sheet] Dataset accessed")
except Exception as error:
    logger.error(f"[Sheet] Error opening dataset: {error}")

try:
    data = sheet.get_all_records()
    logger.info("[Data] Obtained and loaded, authentication done")
except Exception as error:
    logger.error(f"[Data] Error opening dataset: {error}")
