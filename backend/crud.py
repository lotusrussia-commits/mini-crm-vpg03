from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Client, Deal
from backend.schemas import (
    ClientCreate,
    ClientUpdate,
    DealCreate,
    DealUpdate,
)


# CRUD для клиентов

def get_clients(db: Session, skip: int = 0, limit: int = 100):
    statement = select(Client).offset(skip).limit(limit)
    return db.scalars(statement).all()


def get_client(db: Session, client_id: int):
    statement = select(Client).where(Client.id == client_id)
    return db.scalars(statement).first()


def create_client(db: Session, client_data: ClientCreate):
    client = Client(**client_data.model_dump())

    db.add(client)
    db.commit()
    db.refresh(client)

    return client


def update_client(
    db: Session,
    client_id: int,
    client_data: ClientUpdate,
):
    client = get_client(db, client_id)

    if client is None:
        return None

    update_data = client_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)

    return client


def delete_client(db: Session, client_id: int):
    client = get_client(db, client_id)

    if client is None:
        return False

    db.delete(client)
    db.commit()

    return True


# CRUD для сделок

def get_deals(db: Session, skip: int = 0, limit: int = 100):
    statement = select(Deal).offset(skip).limit(limit)
    return db.scalars(statement).all()


def get_deal(db: Session, deal_id: int):
    statement = select(Deal).where(Deal.id == deal_id)
    return db.scalars(statement).first()


def create_deal(db: Session, deal_data: DealCreate):
    deal = Deal(**deal_data.model_dump())

    db.add(deal)
    db.commit()
    db.refresh(deal)

    return deal


def update_deal(
    db: Session,
    deal_id: int,
    deal_data: DealUpdate,
):
    deal = get_deal(db, deal_id)

    if deal is None:
        return None

    update_data = deal_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
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
    # CRUD для задач

from backend.models import Task
from backend.schemas import TaskCreate, TaskUpdate


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    statement = select(Task).offset(skip).limit(limit)
    return db.scalars(statement).all()


def get_task(db: Session, task_id: int):
    statement = select(Task).where(Task.id == task_id)
    return db.scalars(statement).first()


def create_task(db: Session, task_data: TaskCreate):
    task = Task(**task_data.model_dump())

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def update_task(
    db: Session,
    task_id: int,
    task_data: TaskUpdate,
):
    task = get_task(db, task_id)

    if task is None:
        return None

    update_data = task_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
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