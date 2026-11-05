from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend import crud
from backend.database import get_db
from backend.schemas import TaskCreate, TaskRead, TaskUpdate


router = APIRouter(
    prefix="/tasks",
    tags=["Задачи"],
)


@router.get("/", response_model=list[TaskRead])
def read_tasks(
    q: str | None = Query(
        default=None,
        description="Регистронезависимый поиск ILIKE по названию, описанию и статусу",
    ),
    status_filter: str | None = Query(default=None, alias="status"),
    client_id: int | None = None,
    deal_id: int | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_tasks(
        db,
        q=q,
        status=status_filter,
        client_id=client_id,
        deal_id=deal_id,
    )


@router.get("/{task_id}", response_model=TaskRead)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    return task


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_new_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    return crud.create_task(db, task_data)


@router.put("/{task_id}", response_model=TaskRead)
def update_existing_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = crud.update_task(db, task_id, task_data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_task(task_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
