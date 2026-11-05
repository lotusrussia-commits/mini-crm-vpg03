import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from google_integration.sheets import update_configured_spreadsheet
from gui.api_client import APIClient
from google_integration.sheets import update_configured_spreadsheet


class ClientForm(tk.Toplevel):
    def __init__(self, parent, on_save, client=None):
        super().__init__(parent)
        self.on_save = on_save
        self.client = client

        self.title("Редактирование клиента" if client else "Новый клиент")
        self.geometry("430x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        self.entries = {}

        fields = [
            ("name", "Имя"),
            ("company", "Компания"),
            ("phone", "Телефон"),
            ("email", "Email"),
        ]

        for row, (key, label) in enumerate(fields):
            ttk.Label(frame, text=label).grid(
                row=row, column=0, sticky="w", pady=8
            )
            entry = ttk.Entry(frame, width=35)
            entry.grid(row=row, column=1, padx=(12, 0), pady=8)
            self.entries[key] = entry

            if client:
                entry.insert(0, client.get(key) or "")

        frame.columnconfigure(1, weight=1)

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, columnspan=2, pady=20, sticky="e")

        ttk.Button(
            buttons, text="Отмена", command=self.destroy
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons, text="Сохранить", command=self.save
        ).pack(side="left", padx=5)

    def save(self):
        data = {
            key: entry.get().strip() or None
            for key, entry in self.entries.items()
        }

        if not data["name"]:
            messagebox.showwarning(
                "Проверка данных",
                "Введите имя клиента.",
                parent=self,
            )
            return

        try:
            self.on_save(data)
            self.destroy()
        except Exception as error:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось сохранить клиента:\n{error}",
                parent=self,
            )


class DealForm(tk.Toplevel):
    def __init__(self, parent, api, on_save, deal=None):
        super().__init__(parent)

        self.api = api
        self.on_save = on_save
        self.deal = deal
        self.clients = self.api.get_clients()

        self.title("Редактирование сделки" if deal else "Новая сделка")
        self.geometry("480x430")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.create_form()

    def create_form(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Название сделки").grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.title_entry = ttk.Entry(frame, width=38)
        self.title_entry.grid(row=0, column=1, pady=8)

        ttk.Label(frame, text="Сумма").grid(
            row=1, column=0, sticky="w", pady=8
        )
        self.amount_entry = ttk.Entry(frame, width=38)
        self.amount_entry.grid(row=1, column=1, pady=8)

        ttk.Label(frame, text="Статус").grid(
            row=2, column=0, sticky="w", pady=8
        )
        self.status_box = ttk.Combobox(
            frame,
            values=["new", "in_progress", "completed", "cancelled"],
            state="readonly",
            width=35,
        )
        self.status_box.grid(row=2, column=1, pady=8)

        ttk.Label(frame, text="Клиент").grid(
            row=3, column=0, sticky="w", pady=8
        )

        self.client_options = {"Без клиента": None}
        for client in self.clients:
            label = f'{client["name"]} (ID: {client["id"]})'
            self.client_options[label] = client["id"]

        self.client_box = ttk.Combobox(
            frame,
            values=list(self.client_options.keys()),
            state="readonly",
            width=35,
        )
        self.client_box.grid(row=3, column=1, pady=8)

        ttk.Label(frame, text="Описание").grid(
            row=4, column=0, sticky="nw", pady=8
        )
        self.description_text = tk.Text(
            frame, width=28, height=4
        )
        self.description_text.grid(row=4, column=1, pady=8)

        if self.deal:
            self.title_entry.insert(0, self.deal.get("title", ""))
            self.amount_entry.insert(0, str(self.deal.get("amount", 0)))
            self.status_box.set(self.deal.get("status", "new"))
            self.description_text.insert(
                "1.0", self.deal.get("description") or ""
            )

            current_client_id = self.deal.get("client_id")
            selected_label = "Без клиента"

            for label, client_id in self.client_options.items():
                if client_id == current_client_id:
                    selected_label = label
                    break

            self.client_box.set(selected_label)
        else:
            self.status_box.set("new")
            self.client_box.set("Без клиента")

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, columnspan=2, pady=15, sticky="e")

        ttk.Button(
            buttons, text="Отмена", command=self.destroy
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons, text="Сохранить", command=self.save
        ).pack(side="left", padx=5)

    def save(self):
        title = self.title_entry.get().strip()
        amount_text = self.amount_entry.get().strip().replace(",", ".")

        if not title:
            messagebox.showwarning(
                "Проверка данных",
                "Введите название сделки.",
                parent=self,
            )
            return

        try:
            amount = float(amount_text or "0")
            if amount < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Проверка данных",
                "Сумма должна быть неотрицательным числом.",
                parent=self,
            )
            return

        selected_client = self.client_box.get()

        data = {
            "title": title,
            "amount": amount,
            "status": self.status_box.get(),
            "description": self.description_text.get(
                "1.0", "end"
            ).strip() or None,
            "client_id": self.client_options.get(selected_client),
        }

        try:
            self.on_save(data)
            self.destroy()
        except Exception as error:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось сохранить сделку:\n{error}",
                parent=self,
            )


class TaskForm(tk.Toplevel):
    def __init__(self, parent, api, on_save, task=None):
        super().__init__(parent)

        self.api = api
        self.on_save = on_save
        self.task = task

        self.clients = self.api.get_clients()
        self.deals = self.api.get_deals()

        self.title("Редактирование задачи" if task else "Новая задача")
        self.geometry("520x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.create_form()

    def create_form(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Название задачи").grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.title_entry = ttk.Entry(frame, width=38)
        self.title_entry.grid(row=0, column=1, pady=8)

        ttk.Label(frame, text="Описание").grid(
            row=1, column=0, sticky="nw", pady=8
        )
        self.description_text = tk.Text(
            frame, width=28, height=4
        )
        self.description_text.grid(row=1, column=1, pady=8)

        ttk.Label(frame, text="Срок выполнения").grid(
            row=2, column=0, sticky="w", pady=8
        )
        self.date_entry = ttk.Entry(frame, width=38)
        self.date_entry.grid(row=2, column=1, pady=8)

        ttk.Label(frame, text="Статус").grid(
            row=3, column=0, sticky="w", pady=8
        )
        self.status_box = ttk.Combobox(
            frame,
            values=["pending", "in_progress", "completed", "cancelled"],
            state="readonly",
            width=35,
        )
        self.status_box.grid(row=3, column=1, pady=8)

        ttk.Label(frame, text="Клиент").grid(
            row=4, column=0, sticky="w", pady=8
        )

        self.client_options = {"Без клиента": None}

        for client in self.clients:
            label = f'{client["name"]} (ID: {client["id"]})'
            self.client_options[label] = client["id"]

        self.client_box = ttk.Combobox(
            frame,
            values=list(self.client_options.keys()),
            state="readonly",
            width=35,
        )
        self.client_box.grid(row=4, column=1, pady=8)

        ttk.Label(frame, text="Сделка").grid(
            row=5, column=0, sticky="w", pady=8
        )

        self.deal_options = {"Без сделки": None}

        for deal in self.deals:
            label = f'{deal["title"]} (ID: {deal["id"]})'
            self.deal_options[label] = deal["id"]

        self.deal_box = ttk.Combobox(
            frame,
            values=list(self.deal_options.keys()),
            state="readonly",
            width=35,
        )
        self.deal_box.grid(row=5, column=1, pady=8)

        if self.task:
            self.title_entry.insert(
                0, self.task.get("title", "")
            )
            self.description_text.insert(
                "1.0", self.task.get("description") or ""
            )
            self.date_entry.insert(
                0, self.task.get("due_date") or ""
            )
            self.status_box.set(
                self.task.get("status", "pending")
            )

            current_client_id = self.task.get("client_id")
            selected_client = "Без клиента"

            for label, client_id in self.client_options.items():
                if client_id == current_client_id:
                    selected_client = label
                    break

            self.client_box.set(selected_client)

            current_deal_id = self.task.get("deal_id")
            selected_deal = "Без сделки"

            for label, deal_id in self.deal_options.items():
                if deal_id == current_deal_id:
                    selected_deal = label
                    break

            self.deal_box.set(selected_deal)

        else:
            self.status_box.set("pending")
            self.client_box.set("Без клиента")
            self.deal_box.set("Без сделки")

        buttons = ttk.Frame(frame)
        buttons.grid(
            row=6, column=0, columnspan=2,
            pady=20, sticky="e"
        )

        ttk.Button(
            buttons, text="Отмена", command=self.destroy
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons, text="Сохранить", command=self.save
        ).pack(side="left", padx=5)

    def save(self):
        title = self.title_entry.get().strip()
        due_date = self.date_entry.get().strip()

        if not title:
            messagebox.showwarning(
                "Проверка данных",
                "Введите название задачи.",
                parent=self,
            )
            return

        if due_date:
            try:
                date.fromisoformat(due_date)
            except ValueError:
                messagebox.showwarning(
                    "Проверка данных",
                    "Введите дату в формате ГГГГ-ММ-ДД, например 2026-11-12.",
                    parent=self,
                )
                return

        data = {
            "title": title,
            "description": self.description_text.get(
                "1.0", "end"
            ).strip() or None,
            "due_date": due_date or None,
            "status": self.status_box.get(),
            "client_id": self.client_options.get(
                self.client_box.get()
            ),
            "deal_id": self.deal_options.get(
                self.deal_box.get()
            ),
        }

        try:
            self.on_save(data)
            self.destroy()
        except Exception as error:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось сохранить задачу:\n{error}",
                parent=self,
            )


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini CRM")
        self.root.geometry("1100x650")
        self.root.minsize(850, 500)

        self.api = APIClient()
        self.create_widgets()

    def create_widgets(self):
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="Mini CRM",
            font=("Arial", 22, "bold"),
        ).pack(side="left")

        ttk.Label(
            header,
            text="Управление клиентами, сделками и задачами",
            font=("Arial", 10),
        ).pack(side="left", padx=20)

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        sidebar = ttk.Frame(main_frame, width=200)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        sidebar.pack_propagate(False)

        ttk.Label(
            sidebar,
            text="РАЗДЕЛЫ",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=(0, 15))

        self.content = ttk.Frame(main_frame)
        self.content.pack(side="left", fill="both", expand=True)

        ttk.Button(
            sidebar, text="Клиенты", command=self.show_clients
        ).pack(fill="x", pady=5)

        ttk.Button(
            sidebar, text="Сделки", command=self.show_deals
        ).pack(fill="x", pady=5)

        ttk.Button(
            sidebar, text="Задачи", command=self.show_tasks
        ).pack(fill="x", pady=5)

        ttk.Button(
            sidebar,
            text="Экспорт в Google Sheets",
            command=self.export_to_google_sheets,
        ).pack(fill="x", pady=5)

        self.show_home()

    def export_to_google_sheets(self):
        try:
            result = update_configured_spreadsheet()
            exported = result.get("exported", {})

            messagebox.showinfo(
                "Экспорт завершён",
                "Данные успешно экспортированы!\n\n"
                f"Клиенты: {exported.get('Клиенты', 0)}\n"
                f"Сделки: {exported.get('Сделки', 0)}\n"
                f"Задачи: {exported.get('Задачи', 0)}\n\n"
                f"Ссылка:\n{result.get('spreadsheet_url', '')}",
                parent=self.root,
            )

        except Exception as error:
            messagebox.showerror(
                "Ошибка экспорта",
                str(error),
                parent=self.root,
            )

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_content()
        ttk.Label(
            self.content,
            text="Добро пожаловать в Mini CRM!",
            font=("Arial", 18, "bold"),
        ).pack(anchor="w", pady=(20, 10))

        ttk.Label(
            self.content,
            text="Выберите раздел в меню слева.",
            font=("Arial", 12),
        ).pack(anchor="w")

    # КЛИЕНТЫ

    def show_clients(self):
        self.clear_content()

        header = ttk.Frame(self.content)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header, text="Клиенты", font=("Arial", 18, "bold")
        ).pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")

        ttk.Button(
            actions, text="Добавить", command=self.add_client
        ).pack(side="left", padx=3)

        ttk.Button(
            actions, text="Редактировать", command=self.edit_client
        ).pack(side="left", padx=3)

        ttk.Button(
            actions, text="Удалить", command=self.delete_client
        ).pack(side="left", padx=3)

        ttk.Button(
            actions, text="Обновить", command=self.load_clients
        ).pack(side="left", padx=3)

        columns = ("id", "name", "company", "phone", "email")
        self.clients_table = ttk.Treeview(
            self.content, columns=columns, show="headings",
            selectmode="browse",
        )

        headings = {
            "id": "ID", "name": "Имя", "company": "Компания",
            "phone": "Телефон", "email": "Email",
        }
        widths = {
            "id": 50, "name": 170, "company": 200,
            "phone": 150, "email": 200,
        }

        for column in columns:
            self.clients_table.heading(column, text=headings[column])
            self.clients_table.column(
                column, width=widths[column], anchor="w"
            )

        self.clients_table.pack(fill="both", expand=True)
        self.load_clients()

    def load_clients(self):
        for item in self.clients_table.get_children():
            self.clients_table.delete(item)

        try:
            for client in self.api.get_clients():
                self.clients_table.insert(
                    "", "end", iid=str(client["id"]),
                    values=(
                        client["id"], client["name"],
                        client["company"] or "",
                        client["phone"] or "",
                        client["email"] or "",
                    ),
                )
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def get_selected_id(self, table, entity):
        selected = table.selection()
        if not selected:
            messagebox.showwarning(
                "Выбор записи",
                f"Сначала выберите {entity} в таблице.",
            )
            return None
        return int(selected[0])

    def add_client(self):
        ClientForm(self.root, self.save_new_client)

    def save_new_client(self, data):
        self.api.create_client(data)
        self.load_clients()
        messagebox.showinfo("Успешно", "Клиент добавлен.")

    def edit_client(self):
        client_id = self.get_selected_id(
            self.clients_table, "клиента"
        )
        if client_id is None:
            return

        try:
            client = self.api.get_client(client_id)
            ClientForm(
                self.root,
                lambda data: self.save_edited_client(client_id, data),
                client,
            )
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def save_edited_client(self, client_id, data):
        self.api.update_client(client_id, data)
        self.load_clients()
        messagebox.showinfo("Успешно", "Клиент обновлён.")

    def delete_client(self):
        client_id = self.get_selected_id(
            self.clients_table, "клиента"
        )
        if client_id is None:
            return

        if not messagebox.askyesno(
            "Подтверждение",
            f"Удалить клиента №{client_id}?",
        ):
            return

        try:
            self.api.delete_client(client_id)
            self.load_clients()
            messagebox.showinfo("Успешно", "Клиент удалён.")
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    # СДЕЛКИ

    def show_deals(self):
        self.clear_content()

        header = ttk.Frame(self.content)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header, text="Сделки", font=("Arial", 18, "bold")
        ).pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")

        ttk.Button(
            actions, text="Добавить", command=self.add_deal
        ).pack(side="left", padx=3)

        ttk.Button(
            actions, text="Редактировать", command=self.edit_deal
        ).pack(side="left", padx=3)

        ttk.Button(
            actions, text="Удалить", command=self.delete_deal
        ).pack(side="left", padx=3)

        ttk.Button(
            actions, text="Обновить", command=self.load_deals
        ).pack(side="left", padx=3)

        columns = (
            "id", "title", "amount", "status", "description", "client_id"
        )

        self.deals_table = ttk.Treeview(
            self.content, columns=columns, show="headings",
            selectmode="browse",
        )

        headings = {
            "id": "ID", "title": "Название сделки",
            "amount": "Сумма", "status": "Статус",
            "description": "Описание", "client_id": "ID клиента",
        }

        widths = {
            "id": 50, "title": 200, "amount": 100,
            "status": 120, "description": 250, "client_id": 90,
        }

        for column in columns:
            self.deals_table.heading(column, text=headings[column])
            self.deals_table.column(
                column, width=widths[column], anchor="w"
            )

        self.deals_table.pack(fill="both", expand=True)
        self.load_deals()

    def load_deals(self):
        for item in self.deals_table.get_children():
            self.deals_table.delete(item)

        try:
            for deal in self.api.get_deals():
                self.deals_table.insert(
                    "", "end", iid=str(deal["id"]),
                    values=(
                        deal["id"], deal["title"], deal["amount"],
                        deal["status"], deal["description"] or "",
                        deal["client_id"] or "",
                    ),
                )
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def add_deal(self):
        try:
            DealForm(self.root, self.api, self.save_new_deal)
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def save_new_deal(self, data):
        self.api.create_deal(data)
        self.load_deals()
        messagebox.showinfo("Успешно", "Сделка добавлена.")

    def edit_deal(self):
        deal_id = self.get_selected_id(
            self.deals_table, "сделку"
        )
        if deal_id is None:
            return

        try:
            deal = self.api.get_deal(deal_id)
            DealForm(
                self.root,
                self.api,
                lambda data: self.save_edited_deal(deal_id, data),
                deal,
            )
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def save_edited_deal(self, deal_id, data):
        self.api.update_deal(deal_id, data)
        self.load_deals()
        messagebox.showinfo("Успешно", "Сделка обновлена.")

    def delete_deal(self):
        deal_id = self.get_selected_id(
            self.deals_table, "сделку"
        )
        if deal_id is None:
            return

        if not messagebox.askyesno(
            "Подтверждение",
            f"Удалить сделку №{deal_id}?",
        ):
            return

        try:
            self.api.delete_deal(deal_id)
            self.load_deals()
            messagebox.showinfo("Успешно", "Сделка удалена.")
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    # ЗАДАЧИ

    def show_tasks(self):
        self.clear_content()

        header = ttk.Frame(self.content)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header, text="Задачи", font=("Arial", 18, "bold")
        ).pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")

        ttk.Button(
            actions, text="Добавить", command=self.add_task
        ).pack(side="left", padx=3)

        ttk.Button(
            actions, text="Редактировать", command=self.edit_task
        ).pack(side="left", padx=3)

        ttk.Button(
            actions, text="Удалить", command=self.delete_task
        ).pack(side="left", padx=3)

        ttk.Button(
            actions, text="Обновить", command=self.load_tasks
        ).pack(side="left", padx=3)

        columns = (
            "id", "title", "status", "due_date", "client_id", "deal_id"
        )

        self.tasks_table = ttk.Treeview(
            self.content,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        headings = {
            "id": "ID",
            "title": "Название задачи",
            "status": "Статус",
            "due_date": "Срок выполнения",
            "client_id": "ID клиента",
            "deal_id": "ID сделки",
        }

        widths = {
            "id": 50,
            "title": 280,
            "status": 120,
            "due_date": 150,
            "client_id": 100,
            "deal_id": 100,
        }

        for column in columns:
            self.tasks_table.heading(column, text=headings[column])
            self.tasks_table.column(
                column, width=widths[column], anchor="w"
            )

        self.tasks_table.pack(fill="both", expand=True)
        self.load_tasks()

    def load_tasks(self):
        for item in self.tasks_table.get_children():
            self.tasks_table.delete(item)

        try:
            for task in self.api.get_tasks():
                self.tasks_table.insert(
                    "",
                    "end",
                    iid=str(task["id"]),
                    values=(
                        task["id"],
                        task["title"],
                        task["status"],
                        task["due_date"] or "",
                        task["client_id"] or "",
                        task["deal_id"] or "",
                    ),
                )
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def add_task(self):
        try:
            TaskForm(
                self.root,
                self.api,
                self.save_new_task,
            )
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def save_new_task(self, data):
        self.api.create_task(data)
        self.load_tasks()
        messagebox.showinfo("Успешно", "Задача добавлена.")

    def edit_task(self):
        task_id = self.get_selected_id(
            self.tasks_table, "задачу"
        )

        if task_id is None:
            return

        try:
            task = self.api.get_task(task_id)

            TaskForm(
                self.root,
                self.api,
                lambda data: self.save_edited_task(task_id, data),
                task,
            )
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def save_edited_task(self, task_id, data):
        self.api.update_task(task_id, data)
        self.load_tasks()
        messagebox.showinfo("Успешно", "Задача обновлена.")

    def delete_task(self):
        task_id = self.get_selected_id(
            self.tasks_table, "задачу"
        )

        if task_id is None:
            return

        if not messagebox.askyesno(
            "Подтверждение",
            f"Удалить задачу №{task_id}?",
        ):
            return

        try:
            self.api.delete_task(task_id)
            self.load_tasks()
            messagebox.showinfo("Успешно", "Задача удалена.")
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))


def main():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
