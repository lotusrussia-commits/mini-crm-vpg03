from fastapi import FastAPI

from backend.database import Base, engine
from backend import models
from backend.routers import clients, deals, tasks


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mini CRM API",
    description="API для управления клиентами, сделками и задачами",
    version="1.0.0",
)

app.include_router(clients.router)
app.include_router(deals.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    return {
        "message": "Mini CRM API работает",
        "docs": "/docs",
    }