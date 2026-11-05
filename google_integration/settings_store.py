import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = BASE_DIR / "config" / "google_settings.json"


def load_settings():
    if not SETTINGS_PATH.exists():
        return {
            "credentials_file": "",
            "folder_id": "",
        }

    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = {}

    return {
        "credentials_file": data.get("credentials_file", ""),
        "folder_id": data.get("folder_id", ""),
    }


def save_settings(credentials_file, folder_id):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "credentials_file": (credentials_file or "").strip(),
        "folder_id": (folder_id or "").strip(),
    }
    SETTINGS_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload
