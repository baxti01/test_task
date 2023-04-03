from decimal import Decimal
from typing import List

from fastapi import Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app import utils
from app.balance.service import BalanceService
from app.budget.service import BudgetService
from app.database import models
from app.database.database import get_session
from app.database.enums import UserRole, TransactionType
from app.finances.serializer import Period, CreateFinance


class FinanceService:

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_finances(
            self,
            user_id: int,
            period: Period
    ):
        company, _ = self._get_company(
            user_id=user_id,
            permissions=[UserRole.ADMIN, UserRole.DIRECTOR]
        )
        finance = (
            self.session
            .query(models.Finance)
            .filter(
                and_(
                    models.Finance.company_id == company.id,
                    models.Finance.date >= period.from_date,
                    models.Finance.date < period.to_date
                )
            )
            # .order_by(desc(models.Finance.date))
            .all()
        )
        return finance

    def create_finances(
            self,
            user_id: int,
            data: CreateFinance
    ):
        finance, company = self._create_finance(user_id, data)
        return finance

    def replenish_balance(
            self,
            user_id: int,
            data: CreateFinance
    ):
        try:
            with self.session.begin():
                finance, company = self._create_finance(user_id, data)
                balance, balance_history = BalanceService.change_balance(
                    amount=Decimal(finance.amount),
                    transaction_type=TransactionType.INCOME,
                    date=finance.date,
                    balance=company.balance,
                    finance=finance
                )
                self.session.add(balance_history)
                return finance
        except Exception as e:
            raise e

    def _get_company(
            self,
            user_id: int,
            permissions: List[UserRole]
    ) -> tuple[models.Company, models.User]:
        user = utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=permissions
        )
        return user.company, user

    def _create_finance(
            self,
            user_id: int,
            data: CreateFinance
    ):
        try:
            with self.session.begin_nested():
                company, _ = self._get_company(
                    user_id,
                    permissions=[UserRole.ADMIN, UserRole.DIRECTOR]
                )
                finance, budget, budget_history = self.create_finance(
                    data=data,
                    company=company
                )
                self.session.add(budget_history)
                self.session.add(finance)
                return finance, company
        except Exception as e:
            raise e

    @classmethod
    def create_finance(
            cls,
            data: CreateFinance,
            company: models.Company,
    ) -> tuple[models.Finance, models.Budget, models.BudgetHistory]:
        finance = models.Finance(
            **data.dict(),
            company_id=company.id,
        )

        budget, budget_history = BudgetService.change_budget(
            budget=company.budget,
            finance=finance
        )
        return finance, budget, budget_history
