from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'crm.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema():
    """Добавляет новые колонки в уже существующую SQLite-базу."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "clients" not in tables:
        return

    columns = {column["name"] for column in inspector.get_columns("clients")}
    if "status" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text(
            "ALTER TABLE clients "
            "ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'active'"
        ))
        connection.execute(text(
            "UPDATE clients SET status = 'active' "
            "WHERE status IS NULL OR status = ''"
        ))
