import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from google_integration.settings_store import load_settings


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets",
]


def _resolve_credentials_path():
    settings = load_settings()
    configured = (
        settings.get("credentials_file")
        or os.getenv("GOOGLE_CREDENTIALS_FILE")
    )

    if not configured:
        raise ValueError(
            "Не указан JSON-файл OAuth. "
            "Откройте «Настройки Google» в приложении "
            "или задайте GOOGLE_CREDENTIALS_FILE в .env."
        )

    credentials_path = Path(configured)
    if not credentials_path.is_absolute():
        credentials_path = BASE_DIR / credentials_path

    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Не найден файл OAuth: {credentials_path}"
        )

    return credentials_path


def get_google_credentials():
    """Получает или обновляет авторизацию Google."""
    credentials_path = _resolve_credentials_path()
    token_path = BASE_DIR / "token.json"
    credentials = None

    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(
            str(token_path), SCOPES
        )

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

    token_path.write_text(
        credentials.to_json(),
        encoding="utf-8",
    )
    return credentials
