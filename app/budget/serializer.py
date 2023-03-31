from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.database.enums import TransactionType


class BaseBudget(BaseModel):
    income: Decimal
    expense: Decimal
    profit: Decimal


class Budget(BaseBudget):
    id: int
    company_id: int

    # history = Optional[BudgetHistory]
    # finances = Optional[Finances]

    class Config:
        orm_mode = True


class CreateBudget(BaseBudget):
    pass


class UpdateBudget(BaseBudget):
    pass


class BaseBudgetHistory(BaseModel):
    date: datetime = datetime.now()
    transaction_type: TransactionType
    amount: Decimal


class BudgetHistory(BaseBudget, BaseBudgetHistory):
    id: int
    budget_id: int

    class Config:
        orm_mode = True


class CreateBudgetHistory(BaseBudgetHistory):
    pass
