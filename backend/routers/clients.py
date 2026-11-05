from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend import crud
from backend.database import get_db
from backend.schemas import ClientCreate, ClientRead, ClientUpdate


router = APIRouter(
    prefix="/clients",
    tags=["Клиенты"],
)


@router.get("/", response_model=list[ClientRead])
def read_clients(
    q: str | None = Query(
        default=None,
        description="Регистронезависимый поиск ILIKE по имени, компании, телефону и email",
    ),
    status_filter: str | None = Query(default=None, alias="status"),
    include_archived: bool = Query(
        default=False,
        description="По умолчанию архивные клиенты скрыты",
    ),
    db: Session = Depends(get_db),
):
    return crud.get_clients(
        db,
        q=q,
        status=status_filter,
        include_archived=include_archived,
    )


@router.get("/{client_id}", response_model=ClientRead)
def read_client(client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден",
        )
    return client


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_new_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
):
    return crud.create_client(db, client_data)


@router.put("/{client_id}", response_model=ClientRead)
def update_existing_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
):
    client = crud.update_client(db, client_id, client_data)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден",
        )
    return client


@router.post(
    "/{client_id}/restore",
    response_model=ClientRead,
    summary="Восстановить клиента из архива",
)
def restore_existing_client(client_id: int, db: Session = Depends(get_db)):
    client = crud.restore_client(db, client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден",
        )
    return client


@router.delete(
    "/{client_id}",
    response_model=ClientRead,
    summary="Архивировать клиента",
    description=(
        "Не удаляет клиента из базы. Статус становится archived, "
        "сделки и задачи сохраняются. "
        "GET /clients/{id} после этого вернёт 200. "
        "В общем списке запись появится при include_archived=true "
        "или status=archived. Восстановление: POST /clients/{id}/restore."
    ),
)
def archive_existing_client(client_id: int, db: Session = Depends(get_db)):
    client = crud.archive_client(db, client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден",
        )
    return client
