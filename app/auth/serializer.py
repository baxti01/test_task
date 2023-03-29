from typing import Optional

from pydantic import BaseModel

from app.balance.serializer import Balance
from app.database.enums import UserRole


class BaseUser(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER


class User(BaseUser):
    id: int
    company_id: Optional[int] = None
    worker_id: Optional[int] = None
    # balance: Balance

    class Config:
        orm_mode = True


class CreateUser(BaseUser):
    password: str


class UpdateUser(BaseUser):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
