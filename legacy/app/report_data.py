
import random
from datetime import date, timedelta


class ReportDataGenerator:
    """Генератор случайных данных для отчёта о продажах."""

    EMPLOYEES = [
        "Александр Иванов",
        "Мария Петрова",
        "Дмитрий Смирнов",
        "Анна Кузнецова",
        "Сергей Волков",
    ]

    PRODUCTS = [
        ("Ноутбук", 65000),
        ("Смартфон", 35000),
        ("Монитор", 22000),
        ("Клавиатура", 4500),
        ("Мышь", 2500),
        ("Наушники", 8000),
        ("Планшет", 28000),
    ]

    @classmethod
    def generate_report(cls, rows_count=15):
        """Создаёт случайный отчёт с указанным количеством продаж."""
        report = []

        for _ in range(rows_count):
            employee = random.choice(cls.EMPLOYEES)
            product, base_price = random.choice(cls.PRODUCTS)

            quantity = random.randint(1, 5)
            unit_price = round(
                base_price * random.uniform(0.9, 1.1), 2
            )
            revenue = round(quantity * unit_price, 2)

            report_date = date.today() - timedelta(
                days=random.randint(0, 30)
            )

            report.append({
                "date": report_date.strftime("%d.%m.%Y"),
                "employee": employee,
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "revenue": revenue,
            })

        return report

    @staticmethod
    def calculate_totals(report):
        """Подсчитывает общую выручку и количество проданных товаров."""
        total_quantity = sum(
            item["quantity"] for item in report
        )
        total_revenue = round(
            sum(item["revenue"] for item in report), 2
        )

        return {
            "total_quantity": total_quantity,
            "total_revenue": total_revenue,
            "sales_count": len(report),
        }

    @staticmethod
    def prepare_for_sheets(report, totals=None):
        """Преобразует отчёт в формат для записи в Google Sheets."""
        title = ["ОТЧЁТ О ПРОДАЖАХ | EXCEL FACTORY"]
        headers = [
            "Дата",
            "Сотрудник",
            "Товар",
            "Количество",
            "Цена за единицу",
            "Выручка",
        ]

        rows = [
            [
                item["date"],
                item["employee"],
                item["product"],
                item["quantity"],
                item["unit_price"],
                item["revenue"],
            ]
            for item in report
        ]

        if totals is None:
            totals = ReportDataGenerator.calculate_totals(report)

        totals_row = [
            "ИТОГО",
            "",
            "",
            totals["total_quantity"],
            "",
            totals["total_revenue"],
        ]

        return [title, headers] + rows + [totals_row]
