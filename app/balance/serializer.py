from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.database.enums import TransactionType


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


class BaseBalanceHistory(BaseModel):
    date: datetime = datetime.now()
    transaction_type: TransactionType
    amount: Decimal


class BalanceHistory(BaseBalanceHistory):
    id: int
    prev_balance: Decimal
