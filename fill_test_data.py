"""Заполняет CRM реалистичными тестовыми данными через REST API."""

import random
from datetime import date, timedelta

import requests


API_URL = "http://127.0.0.1:8000"
COUNT = 1000

FIRST_NAMES = [
    "Анна", "Иван", "Мария", "Павел", "Елена", "Сергей", "Ольга",
    "Дмитрий", "Наталья", "Алексей", "Екатерина", "Никита", "Ирина",
    "Андрей", "Татьяна", "Максим", "Юлия", "Роман", "Светлана", "Артём",
]
LAST_NAMES = [
    "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов",
    "Васильев", "Соколов", "Михайлов", "Новиков", "Фёдоров", "Морозов",
    "Волков", "Алексеев", "Лебедев", "Семёнов", "Егоров", "Павлов",
]
COMPANIES = [
    "ООО Альфа", "ООО Бета", "ИП Орлов", "АО Север", "ООО Вектор",
    "ООО Горизонт", "ИП Крылова", "ООО Нева", "АО Восток", "ООО Старт",
    None, None,
]
DEAL_TITLES = [
    "Внедрение CRM", "Сопровождение сайта", "Разработка лендинга",
    "Аудит процессов", "Интеграция Google Sheets", "Мобильное приложение",
    "Настройка аналитики", "Автоматизация отчётов", "Доработка API",
]
TASK_TITLES = [
    "Позвонить клиенту", "Подготовить КП", "Согласовать ТЗ",
    "Отправить договор", "Провести демо", "Собрать требования",
    "Проверить оплату", "Назначить встречу", "Обновить статус",
]
DEAL_STATUSES = ["new", "in_progress", "completed", "cancelled"]
TASK_STATUSES = ["pending", "in_progress", "completed", "cancelled"]


def api(method, path, json=None):
    response = requests.request(
        method,
        f"{API_URL}{path}",
        json=json,
        timeout=30,
    )
    response.raise_for_status()
    if response.status_code == 204:
        return None
    return response.json()


def random_phone():
    return f"+7 9{random.randint(10, 99)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"


def fill_clients():
    client_ids = []
    for index in range(COUNT):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        company = random.choice(COMPANIES)
        payload = {
            "name": f"{first} {last}",
            "company": company,
            "phone": random_phone(),
            "email": f"client{index + 1}@example.com",
        }
        created = api("POST", "/clients/", payload)
        client_ids.append(created["id"])
        if (index + 1) % 100 == 0:
            print(f"Клиенты: {index + 1}/{COUNT}")
    return client_ids


def fill_deals(client_ids):
    deal_ids = []
    for index in range(COUNT):
        payload = {
            "title": f"{random.choice(DEAL_TITLES)} #{index + 1}",
            "amount": random.choice([0, 25000, 48000, 79000, 120000, 180000, 250000]),
            "status": random.choice(DEAL_STATUSES),
            "description": "Тестовая сделка, сгенерированная скриптом",
            "client_id": random.choice(client_ids + [None, None]),
        }
        created = api("POST", "/deals/", payload)
        deal_ids.append(created["id"])
        if (index + 1) % 100 == 0:
            print(f"Сделки: {index + 1}/{COUNT}")
    return deal_ids


def fill_tasks(client_ids, deal_ids):
    for index in range(COUNT):
        due = date.today() + timedelta(days=random.randint(-20, 40))
        payload = {
            "title": f"{random.choice(TASK_TITLES)} #{index + 1}",
            "description": "Тестовая задача для проверки отчётов",
            "due_date": due.isoformat(),
            "status": random.choice(TASK_STATUSES),
            "client_id": random.choice(client_ids + [None]),
            "deal_id": random.choice(deal_ids + [None]),
        }
        api("POST", "/tasks/", payload)
        if (index + 1) % 100 == 0:
            print(f"Задачи: {index + 1}/{COUNT}")


def main():
    print("Проверка API...")
    root = api("GET", "/")
    print(root.get("message", "API доступен"))

    print(f"Создаю по {COUNT} записей в каждой таблице...")
    client_ids = fill_clients()
    deal_ids = fill_deals(client_ids)
    fill_tasks(client_ids, deal_ids)
    print("Готово.")


if __name__ == "__main__":
    main()
