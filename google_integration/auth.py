import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


# Корневая папка проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные окружения
load_dotenv(BASE_DIR / ".env")

# Разрешения Google API
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_google_credentials():
    """Получает или обновляет авторизацию Google."""

    credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
    if not credentials_file:
        raise ValueError(
            "В .env не указана переменная GOOGLE_CREDENTIALS_FILE"
        )

    credentials_path = BASE_DIR / credentials_file
    token_path = BASE_DIR / "token.json"

    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Не найден файл OAuth: {credentials_path}"
        )

    credentials = None

    # Проверяем сохранённый токен
    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(
            str(token_path), SCOPES
        )

    # Обновляем токен или запускаем авторизацию
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            SCOPES,
        )

        credentials = flow.run_local_server(
            port=0,
            open_browser=True,
        )

    # Сохраняем токен локально
    token_path.write_text(
        credentials.to_json(),
        encoding="utf-8",
    )

    return credentials