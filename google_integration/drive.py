
from io import BytesIO

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from google_integration.auth import get_google_credentials


def get_drive_service():
    """Создаёт подключение к Google Drive API."""
    credentials = get_google_credentials()

    return build(
        "drive",
        "v3",
        credentials=credentials,
    )


def create_text_file(name: str, content: str):
    """Создаёт текстовый файл на Google Диске."""
    service = get_drive_service()

    file_metadata = {
        "name": name,
        "mimeType": "text/plain",
    }

    media = MediaIoBaseUpload(
        BytesIO(content.encode("utf-8")),
        mimetype="text/plain",
        resumable=True,
    )

    result = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, mimeType, webViewLink",
    ).execute()

    return result


def create_folder(name: str):
    """Создаёт папку на Google Диске."""
    service = get_drive_service()

    folder_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }

    result = service.files().create(
        body=folder_metadata,
        fields="id, name, mimeType, webViewLink",
    ).execute()

    return result
