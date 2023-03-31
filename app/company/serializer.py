import enum
from typing import Optional, List

from pydantic import BaseModel

from app.auth.serializer import User
from app.database.enums import UserRole
from app.worker.serializer import Worker


class BaseCompany(BaseModel):
    name: str


class Company(BaseCompany):
    id: int

    workers: Optional[List[Worker]] = []
    users: Optional[List[User]] = []

    # finance: Optional[List[Finance]] = []
    # balance: Balance
    # budget: Optional[Budget] = []

    class Config:
        orm_mode = True


class CreateCompany(BaseCompany):
    pass


class UpdateCompany(BaseCompany):
    pass
