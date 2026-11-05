# Mini CRM

Учебный прототип CRM: клиенты, сделки и задачи, REST API на FastAPI, интерфейс на Tkinter и выгрузка отчётов в Google Drive / Google Sheets через OAuth 2.0.

Репозиторий: [lotusrussia-commits/mini-crm-vpg03](https://github.com/lotusrussia-commits/mini-crm-vpg03)

## Что умеет

- Вести клиентов, сделки и задачи, связывать их между собой.
- Искать и фильтровать записи по тексту, статусу, клиенту и сделке.
- Архивировать клиента вместо физического удаления: сделки и задачи остаются.
- Смотреть и менять данные через Tkinter или через Swagger.
- Запускать API в Docker Compose с hot-reload.
- Выгружать отдельный отчёт по клиентам, сделкам или задачам: создаётся новая Google Таблица, в неё пишутся строки и блок аналитики.
- После выгрузки открыть таблицу по ссылке одной кнопкой.

## Архитектура

```text
Tkinter GUI  ──HTTP──►  FastAPI (Docker :8000)  ──SQLite──►  data/crm.db
     │
     └── OAuth в браузере ──► Google Drive ──► Google Sheets
```

Интеграция с Google вызывается из GUI, а не из контейнера: пользователь входит в свой аккаунт, сервер только отдаёт данные CRM.

## Стек

Python 3.12, FastAPI, SQLAlchemy, SQLite, Pydantic, Tkinter, Google Drive API, Google Sheets API, OAuth 2.0, Docker Compose.

## Структура проекта

```text
mini-crm-vpg03/
├── backend/
│   ├── main.py              # FastAPI, /health, создание таблиц
│   ├── database.py          # SQLite и миграция колонки status
│   ├── models.py            # Client, Deal, Task
│   ├── schemas.py
│   ├── crud.py              # поиск, архив, CRUD
│   └── routers/             # /clients, /deals, /tasks
├── gui/
│   ├── api_client.py
│   └── main_window.py
├── google_integration/
│   ├── auth.py              # OAuth Desktop
│   ├── drive.py             # создание таблицы и папки
│   ├── sheets.py            # запись и оформление
│   ├── reports.py           # аналитика по разделам
│   └── settings_store.py    # путь к JSON и ID папки Drive
├── config/                  # google_settings.json (локально)
├── data/                    # crm.db (локально)
├── fill_test_data.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Модель данных

| Сущность | Поля | Статусы |
| --- | --- | --- |
| Клиент | имя, компания, телефон, email, **status** | `active`, `archived` |
| Сделка | название, сумма, описание, `client_id` | `new`, `in_progress`, `completed`, `cancelled` |
| Задача | название, описание, срок, `client_id`, `deal_id` | `pending`, `in_progress`, `completed`, `cancelled` |

Сделка и задача могут быть без клиента. При архивации клиента `client_id` у связанных записей не обнуляется и записи не удаляются.

## Установка

```bash
git clone https://github.com/lotusrussia-commits/mini-crm-vpg03.git
cd mini-crm-vpg03

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Пример `.env`:

```dotenv
GOOGLE_CREDENTIALS_FILE=oauth_credentials.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
```

`GOOGLE_SPREADSHEET_ID` нужен только для кнопки «Экспорт всех данных» в уже существующую таблицу. Отчёты по разделам создают новые файлы на Диске.

## Google Cloud и OAuth

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/).
2. Включите **Google Drive API** и **Google Sheets API**.
3. Настройте экран согласия OAuth (External) и добавьте свой аккаунт в тестировщики.
4. Создайте OAuth Client ID типа **Desktop app**, скачайте JSON.
5. Сохраните файл как `oauth_credentials.json` в корне проекта или укажите путь в **Настройки Google**.
6. На Диске создайте папку для отчётов. ID папки — часть URL:  
   `https://drive.google.com/drive/folders/<FOLDER_ID>`

В git не попадают `.env`, `oauth_credentials.json`, `token.json`, `config/google_settings.json` и `data/crm.db`.

## Запуск API

### Docker Compose

Нужен запущенный Docker Engine.

```bash
docker compose up --build
```

Проверки:

| URL | Ожидание |
| --- | --- |
| http://127.0.0.1:8000 | `Mini CRM API работает` |
| http://127.0.0.1:8000/health | `{"status":"ok"}` |
| http://127.0.0.1:8000/docs | Swagger: клиенты, сделки, задачи |

Код `backend/` смонтирован в контейнер, uvicorn работает с `--reload`.

Остановка:

```bash
docker compose down
```

### Локально без Docker

```bash
python -m uvicorn backend.main:app --reload
```

Не запускайте локальный uvicorn и Docker на одном порту 8000 одновременно.

## Интерфейс

API должен быть доступен на `http://127.0.0.1:8000`.

```bash
python -m gui.main_window
```

1. **Настройки Google** — JSON OAuth и ID папки Drive. Кнопка **Вставить** нужна, потому что Ctrl+V в Tkinter часто не работает.
2. Добавьте данные вручную или скриптом `fill_test_data.py`.
3. В разделе нажмите **Выгрузить отчет**. Первый раз откроется браузер для OAuth, токен сохранится в `token.json`.
4. В диалоге нажмите **Открыть**.

Клиенты: **В архив** / **Восстановить**. Поиск и фильтр статуса — над таблицей.

## Тестовые данные

Пока API запущен:

```bash
python fill_test_data.py
```

Скрипт через REST создаёт около 1000 клиентов, сделок и задач. Это занимает несколько минут.

## API

| Метод | Путь | Назначение |
| --- | --- | --- |
| GET | `/` | Статус сервиса |
| GET | `/health` | Health-check |
| GET | `/clients/?q=&status=&include_archived=` | Список и поиск ILIKE |
| POST | `/clients/` | Создание |
| GET/PUT | `/clients/{id}` | Чтение и обновление |
| DELETE | `/clients/{id}` | **Архивация**, запись из базы не удаляется |
| POST | `/clients/{id}/restore` | Снять с архива |
| GET | `/deals/?q=&status=&client_id=` | Список и поиск ILIKE |
| POST/GET/PUT/DELETE | `/deals/` и `/deals/{id}` | CRUD сделок |
| GET | `/tasks/?q=&status=&client_id=&deal_id=` | Список и поиск |
| POST/GET/PUT/DELETE | `/tasks/` и `/tasks/{id}` | CRUD задач |

Поиск `q` идёт через SQL `ILIKE` (в SQLAlchemy — метод `.ilike()`).

Примеры:

```bash
curl "http://127.0.0.1:8000/clients/?q=петров"
curl "http://127.0.0.1:8000/deals/?status=in_progress&client_id=1"
curl -X DELETE "http://127.0.0.1:8000/clients/1"
```

При проверке `DELETE /clients/{id}` учитывайте: это не физическое удаление. Клиент остаётся в базе со статусом `archived`, сделки и задачи на месте. `GET /clients/{id}` вернёт 200, а в общем списке запись появится с `include_archived=true`. Вернуть клиента: `POST /clients/{id}/restore`.

## Как устроен отчёт

1. GUI запрашивает записи раздела через API.
2. `create_spreadsheet` в Drive создаёт таблицу (в указанной папке, если задан ID).
3. `write_formatted_values` записывает шапку, строки и оформляет лист.
4. Внизу — аналитика: число записей, компании, суммы, средняя сумма сделки, статусы, просроченные задачи.

Средняя сумма считается как сумма / количество сделок, а не дублирует итог.

## Безопасность

Не публикуйте OAuth JSON, токены и `.env`. Для сдачи достаточно ссылки на GitHub и скриншотов работающего GUI, Swagger и открытых таблиц.

## Автор

Курс «Профессия вайб-кодер», модуль 9, кейс VPh03: мини-CRM на базе вайбкодинга.
