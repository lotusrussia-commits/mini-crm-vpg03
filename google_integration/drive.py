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


def create_text_file(name: str, content: str, folder_id=None):
    """Создаёт текстовый файл на Google Диске."""
    service = get_drive_service()

    file_metadata = {
        "name": name,
        "mimeType": "text/plain",
    }
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaIoBaseUpload(
        BytesIO(content.encode("utf-8")),
        mimetype="text/plain",
        resumable=True,
    )

    return service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, mimeType, webViewLink",
    ).execute()


def create_folder(name: str, parent_id=None):
    """Создаёт папку на Google Диске."""
    service = get_drive_service()

    folder_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        folder_metadata["parents"] = [parent_id]

    return service.files().create(
        body=folder_metadata,
        fields="id, name, mimeType, webViewLink",
    ).execute()


def create_spreadsheet(name: str, folder_id=None):
    """Создаёт Google Таблицу через Drive API."""
    service = get_drive_service()

    file_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.spreadsheet",
    }
    if folder_id:
        file_metadata["parents"] = [folder_id]

    return service.files().create(
        body=file_metadata,
        fields="id, name, mimeType, webViewLink",
    ).execute()
