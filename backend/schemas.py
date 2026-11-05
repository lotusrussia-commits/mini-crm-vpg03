from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# Схемы клиентов

class ClientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    company: str | None = Field(default=None, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=150)


class ClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    company: str | None = Field(default=None, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=150)


class ClientRead(BaseModel):
    id: int
    name: str
    company: str | None
    phone: str | None
    email: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Схемы сделок

class DealCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    amount: float = Field(default=0, ge=0)
    status: str = Field(default="new", max_length=50)
    description: str | None = None
    client_id: int | None = None


class DealUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    amount: float | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=50)
    description: str | None = None
    client_id: int | None = None


class DealRead(BaseModel):
    id: int
    title: str
    amount: float
    status: str
    description: str | None
    client_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    # Схемы задач

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    due_date: date | None = None
    status: str = Field(default="pending", max_length=50)
    client_id: int | None = None
    deal_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    due_date: date | None = None
    status: str | None = Field(default=None, max_length=50)
    client_id: int | None = None
    deal_id: int | None = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    due_date: date | None
    status: str
    client_id: int | None
    deal_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)