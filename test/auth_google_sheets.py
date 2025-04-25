import os
import gspread
from google.auth.transport.requests import Request
from google.auth import load_credentials_from_file
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

api_key = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
sheet_id = os.getenv('SHEET_ID')

if api_key and sheet_id:
    print("[Credentials] Loaded successfully")
else:
    print("[Credentials] Error loading")
    exit()

credential = load_credentials_from_file(api_key, SCOPES)[0]
client_authentication = gspread.authorize(credential)

try:
    sheet = client_authentication.open_by_key(sheet_id).sheet1
    print("[Sheet] Dataset accessed")
except Exception as error:
    print(f"[Sheet] Error opening dataset: {error}")

try:
    data = sheet.get_all_records()
    print("[Data] Obtained and loaded, authentication done")
except Exception as e:
    print(f"[Data] Error opening dataset: {error}")
