# Mini CRM

Мини-CRM для учёта клиентов, сделок и задач. Данные хранятся в SQLite, REST API работает на FastAPI, интерфейс — Tkinter. Отчёты создаются на Google Диске через OAuth 2.0 и заполняются через Google Sheets API.

Репозиторий: https://github.com/lotusrussia-commits/mini-crm-vpg03

## Возможности

- CRUD по клиентам, сделкам и задачам.
- Связь сделки с клиентом, задачи — с клиентом и сделкой.
- Веб-документация API: Swagger UI.
- Запуск API в Docker Compose с `--reload` и монтированием кода.
- OAuth-авторизация пользователя (не сервисный аккаунт).
- Кнопка **Выгрузить отчет** в каждом разделе: создаётся новая Google Таблица в выбранной папке Drive, в неё пишутся строки и блок аналитики.
- После выгрузки показывается ссылка и кнопка **Открыть**.
- Скрипт `fill_test_data.py` наполняет базу реалистичными тестовыми записями через API.

## Стек

Python 3.12, FastAPI, SQLAlchemy, SQLite, Pydantic, Tkinter, Google Drive API, Google Sheets API, OAuth 2.0, Docker Compose.

## Структура

```text
mini-crm-vpg03/
├── backend/                 # FastAPI, модели, CRUD, роутеры
├── config/                  # примеры env и сохранённые настройки GUI
├── data/                    # SQLite: data/crm.db
├── google_integration/      # OAuth, Drive, Sheets, отчёты
├── gui/                     # Tkinter-клиент к API
├── fill_test_data.py        # генерация тестовых данных
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Быстрый старт

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
cp .env.example .env
```

В `.env`:

```dotenv
GOOGLE_CREDENTIALS_FILE=oauth_credentials.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
```

`GOOGLE_SPREADSHEET_ID` нужен только для кнопки «Экспорт всех данных» в уже существующую таблицу. Отчёты по разделам создают **новые** таблицы в папке Drive.

### Google Cloud

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/).
2. Включите **Google Drive API** и **Google Sheets API**.
3. Настройте экран согласия OAuth, тип пользователя — External, добавьте свой аккаунт в тестировщики.
4. Создайте OAuth Client ID типа **Desktop app**, скачайте JSON.
5. Положите файл в корень проекта (например `oauth_credentials.json`) или выберите его в **Настройки Google**.
6. На Диске создайте папку для отчётов (например `miniCRM`) и скопируйте её ID из URL:  
   `https://drive.google.com/drive/folders/<FOLDER_ID>`

Файлы `oauth_credentials.json`, `token.json`, `.env` в git не попадают.

## Запуск API

### Docker Compose (как в задании)

Нужен запущенный Docker Engine.

```bash
docker compose up --build
```

Проверки:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs — клиенты, сделки, задачи

Код `backend/` смонтирован в контейнер, uvicorn запущен с `--reload`.

Остановка: `docker compose down`.

### Локально без Docker

```bash
python -m uvicorn backend.main:app --reload
```

## Запуск интерфейса

API должен быть доступен на `http://127.0.0.1:8000`.

```bash
python -m gui.main_window
```

1. **Настройки Google** — путь к OAuth JSON и ID папки Drive.  
   Кнопка **Вставить** копирует ID из буфера (Ctrl+V в Tkinter часто не работает).
2. Добавьте клиента / сделку / задачу или запустите `fill_test_data.py`.
3. В разделе нажмите **Выгрузить отчет**. При первой выгрузке откроется браузер для OAuth.
4. В диалоге нажмите **Открыть** — таблица откроется в браузере.

## Тестовые данные

Пока API запущен:

```bash
python fill_test_data.py
```

Скрипт через REST создаёт около 1000 клиентов, 1000 сделок и 1000 задач. Это занимает несколько минут.

## API

| Метод | Путь | Назначение |
| --- | --- | --- |
| GET | `/` | Статус сервиса |
| GET | `/health` | Health-check |
| GET/POST | `/clients/` | Список и создание |
| GET/PUT/DELETE | `/clients/{id}` | Одна запись |
| GET/POST | `/deals/` | Сделки |
| GET/PUT/DELETE | `/deals/{id}` | Одна сделка |
| GET/POST | `/tasks/` | Задачи |
| GET/PUT/DELETE | `/tasks/{id}` | Одна задача |

Статусы сделок: `new`, `in_progress`, `completed`, `cancelled`.  
Статусы задач: `pending`, `in_progress`, `completed`, `cancelled`.

## Как устроена выгрузка отчёта

1. GUI собирает данные текущего раздела через API.
2. `google_integration.drive.create_spreadsheet` создаёт таблицу в папке Drive.
3. `google_integration.sheets.write_formatted_values` записывает строки и оформляет шапку.
4. Внизу листа добавляется аналитика: количество записей, суммы, средняя сумма сделки, статусы, просроченные задачи.

Интеграция вызывается из GUI, чтобы OAuth проходил в браузере пользователя, а не внутри контейнера.

## Безопасность

Не коммитьте `oauth_credentials.json`, `token.json`, `.env` и `config/google_settings.json`.

## Автор

Учебный проект курса «Профессия вайб-кодер», модуль 9, кейс VPh03.
