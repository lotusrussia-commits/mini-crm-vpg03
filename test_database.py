from datetime import date

from backend.database import SessionLocal
from backend.models import Client, Deal, Task


def test_database():
    db = SessionLocal()

    try:
        client = Client(
            name="Тестовый клиент",
            company="ООО Пример",
            phone="+7 900 000-00-00",
            email="test@example.com",
        )

        deal = Deal(
            title="Тестовая сделка",
            amount=150000,
            status="new",
            client=client,
        )

        task = Task(
            title="Позвонить клиенту",
            description="Обсудить условия сделки",
            due_date=date.today(),
            status="pending",
            client=client,
            deal=deal,
        )

        db.add_all([client, deal, task])
        db.flush()

        print("Клиент:", client.id, client.name)
        print("Сделка:", deal.id, deal.title, deal.amount)
        print("Связь сделки с клиентом:", deal.client.name)
        print("Задача:", task.id, task.title)
        print("Связь задачи с клиентом:", task.client.name)
        print("Связь задачи со сделкой:", task.deal.title)

        db.rollback()
        print("\nТест завершён. Временные записи отменены.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    test_database()