
import os

from dotenv import load_dotenv
from googleapiclient.discovery import build

from backend.database import SessionLocal
from backend.models import Client, Deal, Task
from google_integration.auth import get_google_credentials


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def get_sheets_service():
    """Создаёт подключение к Google Sheets API."""
    credentials = get_google_credentials()

    return build(
        "sheets",
        "v4",
        credentials=credentials,
    )


def get_crm_data():
    """Получает клиентов, сделки и задачи из базы CRM."""
    db = SessionLocal()

    try:
        clients = db.query(Client).order_by(Client.id).all()
        deals = db.query(Deal).order_by(Deal.id).all()
        tasks = db.query(Task).order_by(Task.id).all()

        client_rows = [[
            "ID", "Имя", "Компания", "Телефон", "Email", "Дата создания"
        ]]

        for client in clients:
            client_rows.append([
                client.id,
                client.name,
                client.company or "",
                client.phone or "",
                client.email or "",
                client.created_at.isoformat() if client.created_at else "",
            ])

        deal_rows = [[
            "ID", "Название", "Сумма", "Статус",
            "Описание", "ID клиента", "Дата создания"
        ]]

        for deal in deals:
            deal_rows.append([
                deal.id,
                deal.title,
                deal.amount,
                deal.status,
                deal.description or "",
                deal.client_id or "",
                deal.created_at.isoformat() if deal.created_at else "",
            ])

        task_rows = [[
            "ID", "Название", "Описание", "Срок",
            "Статус", "ID клиента", "ID сделки", "Дата создания"
        ]]

        for task in tasks:
            task_rows.append([
                task.id,
                task.title,
                task.description or "",
                task.due_date.isoformat() if task.due_date else "",
                task.status,
                task.client_id or "",
                task.deal_id or "",
                task.created_at.isoformat() if task.created_at else "",
            ])

        return {
            "Клиенты": client_rows,
            "Сделки": deal_rows,
            "Задачи": task_rows,
        }

    finally:
        db.close()


def create_spreadsheet(title="Mini CRM — экспорт"):
    """Создаёт новую Google-таблицу с тремя листами."""
    service = get_sheets_service()

    spreadsheet = {
        "properties": {"title": title},
        "sheets": [
            {"properties": {"title": "Клиенты"}},
            {"properties": {"title": "Сделки"}},
            {"properties": {"title": "Задачи"}},
        ],
    }

    return service.spreadsheets().create(
        body=spreadsheet,
        fields="spreadsheetId,spreadsheetUrl",
    ).execute()


def export_crm_to_spreadsheet(spreadsheet_id):
    """Обновляет данные в трёх листах Google-таблицы."""
    service = get_sheets_service()
    crm_data = get_crm_data()

    for sheet_name, rows in crm_data.items():
        sheet_range = f"'{sheet_name}'!A:Z"

        # Удаляем старые данные, чтобы не оставались лишние строки.
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            body={},
        ).execute()

        # Записываем актуальные данные.
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!A1",
            valueInputOption="RAW",
            body={"values": rows},
        ).execute()

    return {
        "spreadsheet_id": spreadsheet_id,
        "spreadsheet_url": (
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        ),
        "exported": {
            name: len(rows) - 1
            for name, rows in crm_data.items()
        },
    }


def update_configured_spreadsheet():
    """Обновляет таблицу, ID которой указан в .env."""
    spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")

    if not spreadsheet_id:
        raise ValueError(
            "В .env не указана переменная GOOGLE_SPREADSHEET_ID"
        )

    return export_crm_to_spreadsheet(spreadsheet_id)


def create_and_export_crm(title="Mini CRM — экспорт"):
    """Создаёт новую таблицу и сразу заполняет её."""
    spreadsheet = create_spreadsheet(title)

    return export_crm_to_spreadsheet(
        spreadsheet["spreadsheetId"]
    )
