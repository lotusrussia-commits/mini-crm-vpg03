
import os

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetsManager:
    """Класс для взаимодействия с Google Sheets API."""

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, spreadsheet_id=None, credentials_file=None):
        load_dotenv()

        self.spreadsheet_id = (
            spreadsheet_id or os.getenv("GOOGLE_SPREADSHEET_ID")
        )
        self.credentials_file = (
            credentials_file or os.getenv("GOOGLE_CREDENTIALS_FILE")
        )

        if not self.spreadsheet_id:
            raise ValueError("Не указан GOOGLE_SPREADSHEET_ID")

        if not self.credentials_file:
            raise ValueError("Не указан GOOGLE_CREDENTIALS_FILE")

        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Файл credentials не найден: {self.credentials_file}"
            )

        credentials = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=self.SCOPES,
        )

        self.service = build(
            "sheets",
            "v4",
            credentials=credentials,
        )

        self.sheet = self.service.spreadsheets()

    def get_spreadsheet_info(self):
        """Возвращает информацию о таблице и её листах."""
        try:
            return self.sheet.get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
        except HttpError as error:
            raise RuntimeError(
                f"Не удалось получить информацию о таблице: {error}"
            ) from error

    def read_data(self, range_name):
        """Читает данные из указанного диапазона."""
        try:
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
            ).execute()

            return result.get("values", [])
        except HttpError as error:
            raise RuntimeError(
                f"Ошибка чтения данных: {error}"
            ) from error

    def write_data(self, range_name, values):
        """Записывает данные в указанный диапазон."""
        try:
            return self.sheet.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body={"values": values},
            ).execute()
        except HttpError as error:
            raise RuntimeError(
                f"Ошибка записи данных: {error}"
            ) from error

    def append_data(self, range_name, values):
        """Добавляет новые строки после существующих данных."""
        try:
            return self.sheet.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": values},
            ).execute()
        except HttpError as error:
            raise RuntimeError(
                f"Ошибка добавления данных: {error}"
            ) from error

    def clear_data(self, range_name):
        """Очищает содержимое указанного диапазона."""
        try:
            return self.sheet.values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                body={},
            ).execute()
        except HttpError as error:
            raise RuntimeError(
                f"Ошибка очистки диапазона: {error}"
            ) from error

    def create_sheet(self, title):
        """Создаёт новый лист в таблице."""
        try:
            return self.sheet.batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {"title": title}
                            }
                        }
                    ]
                },
            ).execute()
        except HttpError as error:
            raise RuntimeError(
                f"Ошибка создания листа: {error}"
            ) from error

    def format_range(self, sheet_id, start_row, end_row,
                     start_column, end_column, format_options):
        """Применяет форматирование к диапазону ячеек."""
        try:
            return self.sheet.batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={
                    "requests": [
                        {
                            "repeatCell": {
                                "range": {
                                    "sheetId": sheet_id,
                                    "startRowIndex": start_row,
                                    "endRowIndex": end_row,
                                    "startColumnIndex": start_column,
                                    "endColumnIndex": end_column,
                                },
                                "cell": {"userEnteredFormat": format_options},
                                "fields": "userEnteredFormat",
                            }
                        }
                    ]
                },
            ).execute()
        except HttpError as error:
            raise RuntimeError(
                f"Ошибка форматирования ячеек: {error}"
            ) from error

    def merge_cells(self, sheet_id, start_row, end_row,
                    start_column, end_column):
        """Объединяет ячейки указанного диапазона."""
        try:
            return self.sheet.batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={
                    "requests": [
                        {
                            "mergeCells": {
                                "range": {
                                    "sheetId": sheet_id,
                                    "startRowIndex": start_row,
                                    "endRowIndex": end_row,
                                    "startColumnIndex": start_column,
                                    "endColumnIndex": end_column,
                                },
                                "mergeType": "MERGE_ALL",
                            }
                        }
                    ]
                },
            ).execute()
        except HttpError as error:
            raise RuntimeError(
                f"Ошибка объединения ячеек: {error}"
            ) from error

    def unmerge_cells(self, sheet_id, start_row, end_row,
                      start_column, end_column):
        """Снимает объединение ячеек в указанном диапазоне."""
        try:
            return self.batch_update(
                [
                    {
                        "unmergeCells": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": start_row,
                                "endRowIndex": end_row,
                                "startColumnIndex": start_column,
                                "endColumnIndex": end_column,
                            }
                        }
                    }
                ]
            )
        except HttpError as error:
            raise RuntimeError(
                f"Ошибка снятия объединения ячеек: {error}"
            ) from error

    def batch_update(self, requests):
        """Выполняет пакет запросов spreadsheets.batchUpdate."""
        try:
            return self.sheet.batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={"requests": requests},
            ).execute()
        except HttpError as error:
            raise RuntimeError(
                f"Ошибка пакетного обновления таблицы: {error}"
            ) from error

    def get_sheet_properties(self, title):
        """Возвращает свойства листа по названию."""
        spreadsheet = self.get_spreadsheet_info()

        for sheet in spreadsheet.get("sheets", []):
            properties = sheet.get("properties", {})
            if properties.get("title") == title:
                return properties

        raise RuntimeError(f"Лист «{title}» не найден")

    def export_formatted_report(self, sheet_title, values):
        """Записывает отчёт на лист и применяет профессиональное оформление."""
        if not values:
            raise ValueError("Нет данных для записи в Google Sheets")

        properties = self.get_sheet_properties(sheet_title)
        sheet_id = properties["sheetId"]
        grid = properties.get("gridProperties", {})
        row_count = grid.get("rowCount", 1000)
        column_count = max(grid.get("columnCount", 6), 6)

        table_rows = len(values)
        table_columns = 6

        try:
            self._reset_sheet_layout(
                sheet_id,
                row_count,
                column_count,
            )
            self.clear_data(self._a1(sheet_title, "A:Z"))
            self.write_data(self._a1(sheet_title, "A1"), values)
            self.batch_update(
                self._build_report_format_requests(
                    sheet_id,
                    table_rows,
                    table_columns,
                )
            )
        except HttpError as error:
            raise RuntimeError(
                f"Ошибка оформления отчёта: {error}"
            ) from error

    def _reset_sheet_layout(self, sheet_id, row_count, column_count):
        """Снимает объединения, границы и форматы перед повторной выгрузкой."""
        full_range = {
            "sheetId": sheet_id,
            "startRowIndex": 0,
            "endRowIndex": row_count,
            "startColumnIndex": 0,
            "endColumnIndex": column_count,
        }

        self.batch_update(
            [
                {"unmergeCells": {"range": full_range}},
                {
                    "updateBorders": {
                        "range": full_range,
                        "top": {"style": "NONE"},
                        "bottom": {"style": "NONE"},
                        "left": {"style": "NONE"},
                        "right": {"style": "NONE"},
                        "innerHorizontal": {"style": "NONE"},
                        "innerVertical": {"style": "NONE"},
                    }
                },
                {
                    "repeatCell": {
                        "range": full_range,
                        "cell": {"userEnteredFormat": {}},
                        "fields": "userEnteredFormat",
                    }
                },
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_id,
                            "gridProperties": {"frozenRowCount": 0},
                        },
                        "fields": "gridProperties.frozenRowCount",
                    }
                },
            ]
        )

    def _build_report_format_requests(self, sheet_id, table_rows,
                                      table_columns):
        title_end = 1
        header_end = 2
        totals_row = table_rows - 1
        dark_blue = self._rgb("#0F264F")
        header_blue = self._rgb("#1D4ED8")
        totals_bg = self._rgb("#E8EEF7")
        white = self._rgb("#FFFFFF")
        border_color = self._rgb("#94A3B8")
        table_range = {
            "sheetId": sheet_id,
            "startRowIndex": 0,
            "endRowIndex": table_rows,
            "startColumnIndex": 0,
            "endColumnIndex": table_columns,
        }
        border = {
            "style": "SOLID",
            "width": 1,
            "color": border_color,
        }

        return [
            {
                "mergeCells": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": title_end,
                        "startColumnIndex": 0,
                        "endColumnIndex": table_columns,
                    },
                    "mergeType": "MERGE_ALL",
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": title_end,
                        "startColumnIndex": 0,
                        "endColumnIndex": table_columns,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": dark_blue,
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "textFormat": {
                                "foregroundColor": white,
                                "fontSize": 16,
                                "bold": True,
                                "fontFamily": "Arial",
                            },
                        }
                    },
                    "fields": (
                        "userEnteredFormat(backgroundColor,horizontalAlignment,"
                        "verticalAlignment,textFormat)"
                    ),
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": 0,
                        "endIndex": 1,
                    },
                    "properties": {"pixelSize": 36},
                    "fields": "pixelSize",
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": title_end,
                        "endRowIndex": header_end,
                        "startColumnIndex": 0,
                        "endColumnIndex": table_columns,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": header_blue,
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "textFormat": {
                                "foregroundColor": white,
                                "bold": True,
                                "fontSize": 11,
                                "fontFamily": "Arial",
                            },
                        }
                    },
                    "fields": (
                        "userEnteredFormat(backgroundColor,horizontalAlignment,"
                        "verticalAlignment,textFormat)"
                    ),
                }
            },
            self._alignment_request(
                sheet_id, header_end, totals_row, 0, 1, "CENTER"
            ),
            self._alignment_request(
                sheet_id, header_end, totals_row, 1, 3, "LEFT"
            ),
            self._alignment_request(
                sheet_id, header_end, totals_row, 3, 4, "CENTER"
            ),
            self._alignment_request(
                sheet_id, header_end, totals_row, 4, 6, "RIGHT"
            ),
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": header_end,
                        "endRowIndex": table_rows,
                        "startColumnIndex": 4,
                        "endColumnIndex": 6,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                                "type": "NUMBER",
                                "pattern": "#,##0.00",
                            },
                            "horizontalAlignment": "RIGHT",
                        }
                    },
                    "fields": (
                        "userEnteredFormat.numberFormat,"
                        "userEnteredFormat.horizontalAlignment"
                    ),
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": totals_row,
                        "endRowIndex": table_rows,
                        "startColumnIndex": 0,
                        "endColumnIndex": table_columns,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": totals_bg,
                            "textFormat": {
                                "bold": True,
                                "fontFamily": "Arial",
                            },
                            "verticalAlignment": "MIDDLE",
                        }
                    },
                    "fields": (
                        "userEnteredFormat(backgroundColor,textFormat,"
                        "verticalAlignment)"
                    ),
                }
            },
            self._alignment_request(
                sheet_id, totals_row, table_rows, 0, 1, "LEFT",
                include_font=False,
            ),
            self._alignment_request(
                sheet_id, totals_row, table_rows, 3, 4, "CENTER",
                include_font=False,
            ),
            self._alignment_request(
                sheet_id, totals_row, table_rows, 4, 6, "RIGHT",
                include_font=False,
            ),
            {
                "updateBorders": {
                    "range": table_range,
                    "top": border,
                    "bottom": border,
                    "left": border,
                    "right": border,
                    "innerHorizontal": border,
                    "innerVertical": border,
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {"frozenRowCount": 2},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            },
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": table_columns,
                    }
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 1,
                    },
                    "properties": {"pixelSize": 120},
                    "fields": "pixelSize",
                }
            },
        ]

    @staticmethod
    def _alignment_request(sheet_id, start_row, end_row,
                           start_column, end_column, alignment,
                           include_font=True):
        cell_format = {
            "horizontalAlignment": alignment,
            "verticalAlignment": "MIDDLE",
        }
        fields = (
            "userEnteredFormat.horizontalAlignment,"
            "userEnteredFormat.verticalAlignment"
        )

        if include_font:
            cell_format["textFormat"] = {"fontFamily": "Arial"}
            fields += ",userEnteredFormat.textFormat.fontFamily"

        return {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row,
                    "startColumnIndex": start_column,
                    "endColumnIndex": end_column,
                },
                "cell": {"userEnteredFormat": cell_format},
                "fields": fields,
            }
        }

    @staticmethod
    def _a1(sheet_title, range_name):
        escaped = sheet_title.replace("'", "''")
        return f"'{escaped}'!{range_name}"

    @staticmethod
    def _rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        red = int(hex_color[0:2], 16) / 255
        green = int(hex_color[2:4], 16) / 255
        blue = int(hex_color[4:6], 16) / 255
        return {"red": red, "green": green, "blue": blue}
