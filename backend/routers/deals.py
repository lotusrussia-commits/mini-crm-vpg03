from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend import crud
from backend.database import get_db
from backend.schemas import DealCreate, DealRead, DealUpdate


router = APIRouter(
    prefix="/deals",
    tags=["Сделки"],
)


@router.get("/", response_model=list[DealRead])
def read_deals(
    q: str | None = Query(
        default=None,
        description="Регистронезависимый поиск ILIKE по названию, описанию и статусу",
    ),
    status_filter: str | None = Query(default=None, alias="status"),
    client_id: int | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_deals(
        db,
        q=q,
        status=status_filter,
        client_id=client_id,
    )


@router.get("/{deal_id}", response_model=DealRead)
def read_deal(deal_id: int, db: Session = Depends(get_db)):
    deal = crud.get_deal(db, deal_id)
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сделка не найдена",
        )
    return deal


@router.post("/", response_model=DealRead, status_code=status.HTTP_201_CREATED)
def create_new_deal(
    deal_data: DealCreate,
    db: Session = Depends(get_db),
):
    return crud.create_deal(db, deal_data)


@router.put("/{deal_id}", response_model=DealRead)
def update_existing_deal(
    deal_id: int,
    deal_data: DealUpdate,
    db: Session = Depends(get_db),
):
    deal = crud.update_deal(db, deal_id, deal_data)
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сделка не найдена",
        )
    return deal


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_deal(deal_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_deal(db, deal_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сделка не найдена",
        )
