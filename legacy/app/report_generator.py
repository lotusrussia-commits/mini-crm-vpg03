import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from report_data import ReportDataGenerator
    from google_sheets import GoogleSheetsManager
else:
    from .report_data import ReportDataGenerator
    from .google_sheets import GoogleSheetsManager


COLUMNS = (
    "date",
    "employee",
    "product",
    "quantity",
    "unit_price",
    "revenue",
)

COLUMN_HEADINGS = {
    "date": "Дата",
    "employee": "Сотрудник",
    "product": "Товар",
    "quantity": "Количество",
    "unit_price": "Цена за единицу",
    "revenue": "Выручка",
}

SHEET_NAME = "Лист1"


class ReportGeneratorApp:
    """Графическое приложение для генерации отчётов и выгрузки в Google Sheets."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Excel Factory — Генератор отчётов")
        self.root.minsize(920, 620)
        self.root.geometry("1080x720")

        self.report: list[dict] = []
        self.totals: dict = {
            "sales_count": 0,
            "total_quantity": 0,
            "total_revenue": 0.0,
        }

        self._configure_style()
        self._build_ui()
        self._update_totals_labels()
        self._center_window()

    def run(self):
        """Запускает главный цикл Tkinter."""
        self.root.mainloop()

    def _configure_style(self):
        self.colors = {
            "bg": "#f4f6f8",
            "card": "#ffffff",
            "text": "#1f2933",
            "muted": "#52606d",
            "accent": "#2563eb",
            "border": "#d9e2ec",
        }

        self.root.configure(bg=self.colors["bg"])

        style = ttk.Style(self.root)
        try:
            style.theme_use("aqua")
        except tk.TclError:
            style.theme_use(style.theme_use())

        style.configure("App.TFrame", background=self.colors["bg"])
        style.configure("Card.TFrame", background=self.colors["card"])
        style.configure(
            "Title.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["text"],
            font=("Helvetica Neue", 22, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["muted"],
            font=("Helvetica Neue", 13),
        )
        style.configure(
            "Card.TLabel",
            background=self.colors["card"],
            foreground=self.colors["text"],
            font=("Helvetica Neue", 13),
        )
        style.configure(
            "Muted.TLabel",
            background=self.colors["card"],
            foreground=self.colors["muted"],
            font=("Helvetica Neue", 12),
        )
        style.configure(
            "TotalValue.TLabel",
            background=self.colors["card"],
            foreground=self.colors["text"],
            font=("Helvetica Neue", 16, "bold"),
        )
        style.configure("Toolbar.TSpinbox", font=("Helvetica Neue", 13))
        style.configure(
            "Treeview",
            font=("Helvetica Neue", 12),
            rowheight=28,
        )
        style.configure(
            "Treeview.Heading",
            font=("Helvetica Neue", 12, "bold"),
        )

    def _build_ui(self):
        container = ttk.Frame(self.root, style="App.TFrame", padding=24)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(container, style="App.TFrame")
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Excel Factory — Генератор отчётов",
            style="Title.TLabel",
        ).pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Сформируйте отчёт о продажах и выгрузите его в Google Sheets",
            style="Subtitle.TLabel",
        ).pack(anchor=tk.W, pady=(6, 0))

        toolbar = ttk.Frame(container, style="Card.TFrame", padding=16)
        toolbar.pack(fill=tk.X, pady=(20, 0))

        ttk.Label(
            toolbar,
            text="Количество записей",
            style="Card.TLabel",
        ).pack(side=tk.LEFT)

        self.rows_count_var = tk.IntVar(value=15)
        self.rows_spinbox = ttk.Spinbox(
            toolbar,
            from_=5,
            to=100,
            increment=1,
            width=6,
            textvariable=self.rows_count_var,
            justify=tk.CENTER,
            style="Toolbar.TSpinbox",
        )
        self.rows_spinbox.pack(side=tk.LEFT, padx=(12, 16))

        ttk.Button(
            toolbar,
            text="Сгенерировать отчёт",
            command=self._generate_report,
        ).pack(side=tk.LEFT)

        ttk.Button(
            toolbar,
            text="Выгрузить в Google Sheets",
            command=self._export_to_sheets,
        ).pack(side=tk.RIGHT)

        table_card = ttk.Frame(container, style="Card.TFrame", padding=12)
        table_card.pack(fill=tk.BOTH, expand=True, pady=(16, 0))

        table_frame = ttk.Frame(table_card, style="Card.TFrame")
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            table_frame,
            columns=COLUMNS,
            show="headings",
            selectmode="browse",
        )

        column_widths = {
            "date": 120,
            "employee": 200,
            "product": 160,
            "quantity": 120,
            "unit_price": 160,
            "revenue": 140,
        }

        for column in COLUMNS:
            self.tree.heading(column, text=COLUMN_HEADINGS[column])
            anchor = tk.CENTER if column in {"date", "quantity"} else tk.W
            if column in {"unit_price", "revenue"}:
                anchor = tk.E
            self.tree.column(
                column,
                width=column_widths[column],
                minwidth=90,
                anchor=anchor,
                stretch=True,
            )

        y_scroll = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview,
        )
        x_scroll = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL,
            command=self.tree.xview,
        )
        self.tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        totals_card = ttk.Frame(container, style="Card.TFrame", padding=16)
        totals_card.pack(fill=tk.X, pady=(16, 0))

        self.sales_count_var = tk.StringVar()
        self.total_quantity_var = tk.StringVar()
        self.total_revenue_var = tk.StringVar()

        self._add_total_block(
            totals_card,
            "Количество продаж",
            self.sales_count_var,
        ).pack(side=tk.LEFT, expand=True, fill=tk.X)
        self._add_total_block(
            totals_card,
            "Проданное количество товаров",
            self.total_quantity_var,
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=24)
        self._add_total_block(
            totals_card,
            "Общая выручка",
            self.total_revenue_var,
        ).pack(side=tk.LEFT, expand=True, fill=tk.X)

    def _add_total_block(self, parent, caption, value_var):
        block = ttk.Frame(parent, style="Card.TFrame")
        ttk.Label(block, text=caption, style="Muted.TLabel").pack(anchor=tk.W)
        ttk.Label(
            block,
            textvariable=value_var,
            style="TotalValue.TLabel",
        ).pack(anchor=tk.W, pady=(4, 0))
        return block

    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 3, 0)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _get_rows_count(self):
        try:
            rows_count = int(self.rows_spinbox.get())
        except (TypeError, ValueError):
            raise ValueError("Количество записей должно быть целым числом.")

        if not 5 <= rows_count <= 100:
            raise ValueError("Количество записей должно быть от 5 до 100.")

        return rows_count

    def _generate_report(self):
        try:
            rows_count = self._get_rows_count()
        except ValueError as error:
            messagebox.showerror("Ошибка", str(error), parent=self.root)
            return

        self.report = ReportDataGenerator.generate_report(rows_count)
        self.totals = ReportDataGenerator.calculate_totals(self.report)
        self._fill_table()
        self._update_totals_labels()

    def _fill_table(self):
        self.tree.delete(*self.tree.get_children())

        for index, item in enumerate(self.report):
            self.tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    item["date"],
                    item["employee"],
                    item["product"],
                    item["quantity"],
                    self._format_money(item["unit_price"]),
                    self._format_money(item["revenue"]),
                ),
            )

    def _update_totals_labels(self):
        self.sales_count_var.set(str(self.totals["sales_count"]))
        self.total_quantity_var.set(str(self.totals["total_quantity"]))
        self.total_revenue_var.set(
            self._format_money(self.totals["total_revenue"])
        )

    def _export_to_sheets(self):
        if not self.report:
            messagebox.showwarning(
                "Нет данных",
                "Сначала сгенерируйте отчёт.",
                parent=self.root,
            )
            return

        values = ReportDataGenerator.prepare_for_sheets(
            self.report,
            self.totals,
        )

        try:
            manager = GoogleSheetsManager()
            manager.export_formatted_report(SHEET_NAME, values)
        except FileNotFoundError as error:
            messagebox.showerror(
                "Ошибка подключения",
                str(error),
                parent=self.root,
            )
        except ValueError as error:
            messagebox.showerror(
                "Ошибка подключения",
                str(error),
                parent=self.root,
            )
        except RuntimeError as error:
            messagebox.showerror(
                "Ошибка записи",
                str(error),
                parent=self.root,
            )
        except Exception as error:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось выгрузить отчёт: {error}",
                parent=self.root,
            )
        else:
            messagebox.showinfo(
                "Готово",
                "Отчёт успешно выгружен в Google Sheets.",
                parent=self.root,
            )

    @staticmethod
    def _format_money(value):
        return f"{value:,.2f}".replace(",", " ")


if __name__ == "__main__":
    ReportGeneratorApp().run()
