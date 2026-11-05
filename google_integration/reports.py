from collections import Counter
from datetime import date

from google_integration.drive import create_spreadsheet
from google_integration.settings_store import load_settings
from google_integration.sheets import write_formatted_values


def _summary_block(items):
    rows = [[], ["Аналитика"], ["Показатель", "Значение"]]
    rows.extend([name, value] for name, value in items)
    return rows


def build_clients_report(clients):
    companies = [item.get("company") or "" for item in clients]
    with_company = sum(1 for company in companies if company.strip())
    counted = Counter(
        company for company in companies if company.strip()
    )
    top_company = counted.most_common(1)
    top_label = top_company[0][0] if top_company else "—"
    statuses = Counter(item.get("status") or "active" for item in clients)

    headers = ["ID", "Имя", "Компания", "Телефон", "Email", "Статус"]
    rows = [
        [
            item.get("id"),
            item.get("name"),
            item.get("company") or "",
            item.get("phone") or "",
            item.get("email") or "",
            item.get("status") or "active",
        ]
        for item in clients
    ]
    summary_items = [
        ("Всего клиентов", len(clients)),
        ("С компанией", with_company),
        ("Без компании", len(clients) - with_company),
        ("Самая частая компания", top_label),
        ("Активных", statuses.get("active", 0)),
        ("В архиве", statuses.get("archived", 0)),
    ]
    return "Клиенты", headers, rows, _summary_block(summary_items), []


def build_deals_report(deals):
    amounts = [float(item.get("amount") or 0) for item in deals]
    total = sum(amounts)
    average = round(total / len(amounts), 2) if amounts else 0
    statuses = Counter(item.get("status") or "—" for item in deals)

    headers = [
        "ID", "Название", "Сумма", "Статус", "Описание", "ID клиента"
    ]
    rows = [
        [
            item.get("id"),
            item.get("title"),
            float(item.get("amount") or 0),
            item.get("status"),
            item.get("description") or "",
            item.get("client_id") or "",
        ]
        for item in deals
    ]
    summary_items = [
        ("Всего сделок", len(deals)),
        ("Общая сумма", round(total, 2)),
        ("Средняя сумма", average),
    ]
    summary_items.extend(
        (f"Статус: {name}", count)
        for name, count in sorted(statuses.items())
    )
    return "Сделки", headers, rows, _summary_block(summary_items), [2]


def build_tasks_report(tasks):
    statuses = Counter(item.get("status") or "—" for item in tasks)
    today = date.today().isoformat()
    overdue = 0
    for item in tasks:
        due_date = item.get("due_date") or ""
        if due_date and due_date < today and item.get("status") != "completed":
            overdue += 1

    headers = [
        "ID", "Название", "Статус", "Срок", "ID клиента", "ID сделки"
    ]
    rows = [
        [
            item.get("id"),
            item.get("title"),
            item.get("status"),
            item.get("due_date") or "",
            item.get("client_id") or "",
            item.get("deal_id") or "",
        ]
        for item in tasks
    ]
    summary_items = [
        ("Всего задач", len(tasks)),
        ("Просрочено", overdue),
    ]
    summary_items.extend(
        (f"Статус: {name}", count)
        for name, count in sorted(statuses.items())
    )
    return "Задачи", headers, rows, _summary_block(summary_items), []


BUILDERS = {
    "clients": build_clients_report,
    "deals": build_deals_report,
    "tasks": build_tasks_report,
}

TITLES = {
    "clients": "Клиенты",
    "deals": "Сделки",
    "tasks": "Задачи",
}


def export_section_report(section, records):
    """Создаёт таблицу на Drive и заполняет её через Sheets API."""
    builder = BUILDERS[section]
    sheet_title, headers, rows, summary, number_columns = builder(records)
    settings = load_settings()
    folder_id = settings.get("folder_id") or None

    created = create_spreadsheet(
        f"Mini CRM — {TITLES[section]}",
        folder_id=folder_id,
    )
    values = [headers, *rows, *summary]
    result = write_formatted_values(
        created["id"],
        sheet_title,
        values,
        number_columns=number_columns,
        data_row_count=len(rows),
    )
    result["webViewLink"] = created.get("webViewLink") or result["spreadsheet_url"]
    result["title"] = created.get("name")
    result["rows"] = len(rows)
    return result
