from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import ClientCreate, ClientRead, ClientUpdate
from backend import crud


router = APIRouter(
    prefix="/clients",
    tags=["Клиенты"],
)


@router.get("/", response_model=list[ClientRead])
def read_clients(db: Session = Depends(get_db)):
    return crud.get_clients(db)


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


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_client(client_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_client(db, client_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден",
        )