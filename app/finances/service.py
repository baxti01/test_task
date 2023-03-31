from typing import List

from fastapi import Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import utils
from app.budget.service import BudgetService
from app.database import models
from app.database.database import get_session
from app.database.enums import UserRole
from app.finances.serializer import Period, CreateFinance


class FinanceService:

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_finances(
            self,
            user_id: int,
            period: Period
    ) -> List[models.Finance]:
        company, _ = self._get_company(
            user_id=user_id,
            permissions=[UserRole.ADMIN, UserRole.DIRECTOR]
        )
        finance = (
            self.session
            .query(models.Finance)
            .filter_by(company_id=company.id)
            .where(models.Finance.date >= period.from_date)
            .where(models.Finance.date < period.to_date)
            .order_by(desc(models.Finance.date))
            .all()
        )
        return finance

    def create_finances(
            self,
            user_id: int,
            data: CreateFinance
    ):
        company, _ = self._get_company(
            user_id,
            permissions=[UserRole.ADMIN, UserRole.DIRECTOR]
        )

        return self.create_finance(
            session=self.session,
            data=data,
            company=company
        )

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

    @classmethod
    def create_finance(
            cls,
            session: Session,
            data: CreateFinance,
            company: models.Company,
    ):
        finance = models.Finance(
            **data.dict(),
            company_id=company.id,
        )
        utils.save_in_db(session, finance)
        BudgetService.change_budget(
            session=session,
            budget=company.budget,
            finance=finance
        )
        return finance
