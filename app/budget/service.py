from datetime import datetime
from decimal import Decimal

from fastapi import Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app import utils
from app.database import models
from app.database.database import get_session
from app.database.enums import UserRole, TransactionType
from app.finances.serializer import Period


class BudgetService:

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_budget(
            self,
            user_id: int,
    ) -> models.Budget:
        return self._get_budget(user_id)

    def get_budget_history(
            self,
            user_id: int,
            period: Period
    ):
        budget = self._get_budget(user_id)

        return (
            self.session
            .query(models.BudgetHistory)
            .filter(
                and_(
                    models.BudgetHistory.budget_id == budget.id,
                    models.BudgetHistory.date >= period.from_date,
                    models.BudgetHistory.date < period.to_date
                )
            )
            .all()
        )

    def _get_budget(
            self,
            user_id: int,
    ) -> models.Budget:
        user = utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=[UserRole.DIRECTOR, UserRole.ADMIN]
        )
        return user.company.budget

    @classmethod
    def create_budget(
            cls,
            session: Session,
            company_id: int
    ):
        budget = models.Budget(
            income=Decimal(0.0),
            expense=Decimal(0.0),
            profit=Decimal(0.0),
            date=datetime.now(),
            company_id=company_id
        )
        utils.save_in_db(session, budget)

    @classmethod
    def change_budget(
            cls,
            budget: models.Budget,
            finance: models.Finance
    ) -> tuple[models.Budget, models.BudgetHistory]:
        budget_history = models.BudgetHistory(
            income=budget.income,
            expense=budget.expense,
            profit=budget.profit,
            date=budget.date,
            amount=finance.amount,
            transaction_type=finance.transaction_type,
            finance_id=budget.finance_id,
            budget_id=budget.id
        )
        if finance.transaction_type == TransactionType.INCOME:
            budget.income += finance.amount
            budget.profit += finance.amount
        if finance.transaction_type == TransactionType.EXPENSE:
            budget.expense += finance.amount
            budget.profit -= finance.amount

        budget.date = finance.date
        budget.finance_id = finance.id

        return budget, budget_history
