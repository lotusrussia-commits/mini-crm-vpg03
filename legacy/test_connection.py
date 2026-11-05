import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = Credentials.from_service_account_file(
    credentials_file,
    scopes=SCOPES
)

service = build("sheets", "v4", credentials=credentials)

spreadsheet = service.spreadsheets().get(
    spreadsheetId=spreadsheet_id
).execute()

print("\nПодключение успешно!")
print("Название таблицы:", spreadsheet["properties"]["title"])
print("Листы:")

for sheet in spreadsheet["sheets"]:
    print("-", sheet["properties"]["title"])
