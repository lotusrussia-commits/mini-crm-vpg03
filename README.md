# Excel Factory — Google Sheets Report Generator

Автоматический генератор отчётов о продажах на Python с графическим интерфейсом Tkinter и интеграцией с Google Sheets API.

Приложение генерирует тестовые данные о продажах, рассчитывает основные показатели и экспортирует готовый отчёт в Google Таблицы с автоматическим форматированием.

## Возможности

- Генерация случайных данных о продажах.
- Выбор количества записей от 5 до 100.
- Отображение данных в графическом интерфейсе Tkinter.
- Расчёт количества продаж, проданных товаров и общей выручки.
- Интеграция с Google Sheets API v4.
- Экспорт отчётов в Google Таблицы.
- Очистка предыдущего отчёта перед новой выгрузкой.
- Автоматическое форматирование таблицы:
  - объединение ячеек заголовка;
  - цветовое оформление заголовков;
  - форматирование денежных значений;
  - выравнивание данных;
  - границы таблицы;
  - выделение итоговой строки;
  - закрепление строк заголовка;
  - автоматическая настройка ширины столбцов.

## Технологии

- Python 3.12
- Tkinter / ttk
- Google Sheets API v4
- Google Authentication
- Google API Python Client
- python-dotenv

## Структура проекта

```text
google-sheets-report-generator/
├── app/
│   ├── __init__.py
│   ├── google_sheets.py
│   ├── report_data.py
│   └── report_generator.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── main.py
└── test_connection.py
```

Локальные файлы `.env` и `credentials.json` в репозиторий не включаются. Они необходимы для настройки подключения и должны быть созданы самостоятельно.

## Установка и запуск

### 1. Клонирование проекта

```bash
git clone https://github.com/lotusrussia-commits/google-sheets-report-generator.git
cd google-sheets-report-generator
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

### 4. Настройка Google Cloud

Для работы приложения необходимо:

1. Создать проект в [Google Cloud Console](https://console.cloud.google.com/).
2. Включить Google Sheets API.
3. Создать Service Account.
4. Создать и скачать JSON-ключ сервисного аккаунта.
5. Сохранить ключ в корне проекта под именем `credentials.json`.
6. Создать Google Spreadsheet.
7. Предоставить адресу сервисного аккаунта права Editor на таблицу.

### 5. Настройка переменных окружения

Создать файл `.env` в корне проекта.

Можно скопировать пример:

```bash
cp .env.example .env
```

Затем заполнить `.env`:

```dotenv
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
```

Вместо `your_spreadsheet_id` указать ID своей Google Таблицы.

### 6. Запуск приложения

```bash
python main.py
```

После запуска откроется графическое приложение, в котором можно сгенерировать отчёт, просмотреть данные и экспортировать их в Google Таблицы.

## Проверка подключения

Для отдельной проверки доступа к Google Sheets API предусмотрен скрипт:

```bash
python test_connection.py
```

При успешном подключении скрипт выводит название таблицы и список доступных листов.

## Архитектура

Проект разделён на несколько модулей:

- `app/google_sheets.py` — класс `GoogleSheetsManager`, отвечающий за подключение к Google Sheets API, чтение, запись и форматирование данных.
- `app/report_data.py` — класс `ReportDataGenerator`, отвечающий за генерацию тестовых данных и расчёт итоговых показателей.
- `app/report_generator.py` — класс `ReportGeneratorApp`, реализующий графический интерфейс приложения.
- `main.py` — точка входа в приложение.

## Безопасность

- Секретные ключи и настройки подключения хранятся локально.
- Файлы `.env` и `credentials.json` исключены из Git через `.gitignore`.
- Для подключения используется сервисный аккаунт Google.

**Не публикуйте JSON-ключ сервисного аккаунта и содержимое файла `.env` в открытых репозиториях.**

## Автор

Проект выполнен в рамках практического обучения Python и интеграции внешних API.

GitHub: [lotusrussia-commits](https://github.com/lotusrussia-commits)