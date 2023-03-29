from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class BaseBalance(BaseModel):
    balance: Decimal


class Balance(BaseBalance):
    id: int
    # history: List[History]
    user_id: Optional[int]
    company_id: Optional[int]

    class Config:
        orm_mode = True


class CreateBalance(BaseBalance):
    pass


class UpdateBalance(BaseBalance):
    pass
