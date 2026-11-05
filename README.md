# Mini CRM — система управления клиентами и сделками

Mini CRM — настольное приложение для управления клиентами, сделками и задачами с REST API, базой данных SQLite и интеграцией с Google Workspace.

Приложение позволяет вести клиентскую базу, отслеживать сделки, управлять задачами и экспортировать данные CRM в Google Sheets.

## Возможности

- Управление клиентами: создание, просмотр, редактирование и удаление.
- Управление сделками: учёт суммы, статуса, описания и привязки к клиенту.
- Управление задачами: создание, редактирование, удаление и контроль сроков выполнения.
- Графический интерфейс на Tkinter.
- REST API на FastAPI.
- Хранение данных в SQLite с использованием SQLAlchemy.
- Интеграция с Google Drive API.
- Экспорт клиентов, сделок и задач в Google Sheets.
- Обновление существующей Google Таблицы одной кнопкой из графического интерфейса.
- Авторизация Google OAuth 2.0.
- Контейнеризация приложения с помощью Docker и Docker Compose.

## Технологии

- Python 3.12
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Tkinter / ttk
- Google Drive API
- Google Sheets API v4
- Google OAuth 2.0
- python-dotenv
- Docker
- Docker Compose
- Git / GitHub

## Структура проекта

```text
mini-crm-vpg03/
├── backend/
│   ├── routers/
│   │   ├── clients.py
│   │   ├── deals.py
│   │   └── tasks.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── config/
├── google_integration/
│   ├── auth.py
│   ├── drive.py
│   └── sheets.py
├── gui/
│   ├── api_client.py
│   └── main_window.py
├── legacy/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── test_database.py
└── README.md
```

## Установка и запуск

### 1. Клонирование проекта

```bash
git clone https://github.com/lotusrussia-commits/mini-crm-vpg03.git
cd mini-crm-vpg03
```

### 2. Создание виртуального окружения

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установка зависимостей

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Создать файл `.env` на основе шаблона:

```bash
cp .env.example .env
```

Указать настройки Google:

```dotenv
GOOGLE_CREDENTIALS_FILE=oauth_credentials.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
```

Для интеграции с Google необходимо создать проект в Google Cloud Console, включить Google Drive API и Google Sheets API, настроить OAuth 2.0 для Desktop Application и скачать JSON-файл OAuth-клиента.

Сохранить файл в корне проекта под именем `oauth_credentials.json`.

При первом обращении к Google API приложение запросит авторизацию через браузер. После успеш