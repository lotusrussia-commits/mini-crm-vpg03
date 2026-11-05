from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.models import Client, Deal, Task
from backend.schemas import (
    ClientCreate,
    ClientUpdate,
    DealCreate,
    DealUpdate,
    TaskCreate,
    TaskUpdate,
)


def _contains(column, query: str):
    """Регистронезависимый поиск через ILIKE.

    SQLAlchemy компилирует ``ilike`` в ILIKE. Для кириллицы в SQLite
    дополнительно ищем типичные регистры строки, потому что встроенный
    LOWER() там работает только для латиницы.
    """
    raw = query.strip()
    variants = {
        raw,
        raw.lower(),
        raw.upper(),
        raw.capitalize(),
        raw.title(),
    }
    return or_(
        *[column.ilike(f"%{variant}%") for variant in variants if variant]
    )


def get_clients(
    db: Session,
    q: str | None = None,
    status: str | None = None,
    include_archived: bool = False,
):
    statement = select(Client)

    if q:
        statement = statement.where(
            or_(
                _contains(Client.name, q),
                _contains(Client.company, q),
                _contains(Client.phone, q),
                _contains(Client.email, q),
            )
        )

    if status:
        statement = statement.where(Client.status == status)
    elif not include_archived:
        statement = statement.where(Client.status != "archived")

    return db.scalars(statement.order_by(Client.id)).all()


def get_client(db: Session, client_id: int):
    statement = select(Client).where(Client.id == client_id)
    return db.scalars(statement).first()


def create_client(db: Session, client_data: ClientCreate):
    payload = client_data.model_dump()
    payload.setdefault("status", "active")
    client = Client(**payload)

    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def update_client(db: Session, client_id: int, client_data: ClientUpdate):
    client = get_client(db, client_id)
    if client is None:
        return None

    for field, value in client_data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


def archive_client(db: Session, client_id: int):
    return update_client(
        db,
        client_id,
        ClientUpdate(status="archived"),
    )


def restore_client(db: Session, client_id: int):
    return update_client(
        db,
        client_id,
        ClientUpdate(status="active"),
    )


def get_deals(
    db: Session,
    q: str | None = None,
    status: str | None = None,
    client_id: int | None = None,
):
    statement = select(Deal)

    if q:
        statement = statement.where(
            or_(
                _contains(Deal.title, q),
                _contains(Deal.description, q),
                _contains(Deal.status, q),
            )
        )

    if status:
        statement = statement.where(Deal.status == status)

    if client_id is not None:
        statement = statement.where(Deal.client_id == client_id)

    return db.scalars(statement.order_by(Deal.id)).all()


def get_deal(db: Session, deal_id: int):
    statement = select(Deal).where(Deal.id == deal_id)
    return db.scalars(statement).first()


def create_deal(db: Session, deal_data: DealCreate):
    deal = Deal(**deal_data.model_dump())
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


def update_deal(db: Session, deal_id: int, deal_data: DealUpdate):
    deal = get_deal(db, deal_id)
    if deal is None:
        return None

    for field, value in deal_data.model_dump(exclude_unset=True).items():
        setattr(deal, field, value)

    db.commit()
    db.refresh(deal)
    return deal


def delete_deal(db: Session, deal_id: int):
    deal = get_deal(db, deal_id)
    if deal is None:
        return False

    db.delete(deal)
    db.commit()
    return True


def get_tasks(
    db: Session,
    q: str | None = None,
    status: str | None = None,
    client_id: int | None = None,
    deal_id: int | None = None,
):
    statement = select(Task)

    if q:
        statement = statement.where(
            or_(
                _contains(Task.title, q),
                _contains(Task.description, q),
                _contains(Task.status, q),
            )
        )

    if status:
        statement = statement.where(Task.status == status)

    if client_id is not None:
        statement = statement.where(Task.client_id == client_id)

    if deal_id is not None:
        statement = statement.where(Task.deal_id == deal_id)

    return db.scalars(statement.order_by(Task.id)).all()


def get_task(db: Session, task_id: int):
    statement = select(Task).where(Task.id == task_id)
    return db.scalars(statement).first()


def create_task(db: Session, task_data: TaskCreate):
    task = Task(**task_data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, task_data: TaskUpdate):
    task = get_task(db, task_id)
    if task is None:
        return None

    for field, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int):
    task = get_task(db, task_id)
    if task is None:
        return False

    db.delete(task)
    db.commit()
    return True
