from typing import Optional, List

from pydantic import BaseModel

from app.auth.serializer import User
from app.balance.serializer import Balance


class BaseCompany(BaseModel):
    name: str


class Company(BaseCompany):
    id: int

    # workers: Optional[List[Worker]] = []
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
