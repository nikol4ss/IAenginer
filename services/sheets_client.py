import gspread
from google.auth import load_credentials_from_file

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def google_client_authentication(credentials: str, sheet_id: str):
    credentials = load_credentials_from_file(credentials, SCOPES)[0]
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(sheet_id)

    return spreadsheet
