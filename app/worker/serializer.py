from typing import Optional, List

from pydantic import BaseModel

from app.auth.serializer import User


class BaseWorker(BaseModel):
    name: str


class Worker(BaseWorker):
    id: int
    company_id: int
    users: Optional[List[User]]

    class Config:
        orm_mode = True


class CreateWorker(BaseWorker):
    pass


class UpdateWorker(BaseWorker):
    pass


class InvoiceWorker(BaseWorker):
    id: int

    class Config:
        orm_mode = True
