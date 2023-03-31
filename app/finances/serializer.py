from datetime import datetime, timedelta
from decimal import Decimal

from pydantic import BaseModel

from app.database.enums import TransactionType


class Period(BaseModel):
    from_date: datetime = datetime.now() - timedelta(days=7)
    to_date: datetime = datetime.now() + timedelta(days=7)


class BaseFinance(BaseModel):
    date: datetime = datetime.now()
    transaction_type: TransactionType
    amount: Decimal


class Finance(BaseFinance):
    id: int
    company_id: int

    class Config:
        orm_mode = True


class CreateFinance(BaseFinance):
    pass


class UpdateFinance(BaseFinance):
    pass
