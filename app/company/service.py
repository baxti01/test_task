from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from app import utils
from app.balance.service import BalanceService
from app.budget.service import BudgetService
from app.company.serializer import CreateCompany, UpdateCompany
from app.database import models
from app.database.database import get_session
from app.database.enums import UserRole, BalanceType


class CompanyService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get_company(
            self,
            user_id: int,
            permissions: List[UserRole]
    ) -> models.User:
        user = utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=permissions
        )
        return user

    def get_company(self, user_id: int) -> models.Company:
        user = self._get_company(
            user_id=user_id,
            permissions=[UserRole.ADMIN, UserRole.DIRECTOR]
        )
        return user.company

    def create_company(
            self,
            user_id: int,
            data: CreateCompany
    ) -> models.Company:
        user = utils.check_user_company(self.session, user_id)

        company = models.Company(
            **data.dict()
        )
        utils.save_in_db(self.session, company)

        user.company_id = company.id
        user.role = UserRole.DIRECTOR
        utils.update_in_db(self.session, user)

        BalanceService.create_balance(
            session=self.session,
            ident=company.id,
            balance_type=BalanceType.COMPANY
        )

        BudgetService.create_budget(
            session=self.session,
            company_id=company.id
        )

        return company

    def update_company(
            self,
            user_id: int,
            data: UpdateCompany
    ) -> models.Company:
        user = self._get_company(user_id, [UserRole.DIRECTOR])

        for field, value in data:
            setattr(user.company, field, value)

        utils.update_in_db(self.session, user.company)

        return user.company

    def delete_company(
            self,
            user_id: int
    ):
        director = self._get_company(user_id, [UserRole.DIRECTOR])

        for user in director.company.users:
            user.role = UserRole.CUSTOMER
            user.company_id = None

        utils.delete_in_db(self.session, director.company)

    def add_user(
            self,
            new_user_id: int,
            user_id: int
    ):
        user = self._get_company(
            user_id=user_id,
            permissions=[UserRole.DIRECTOR, UserRole.ADMIN]
        )

        new_user = utils.check_user_company(
            session=self.session,
            user_id=new_user_id
        )
        new_user.company_id = user.company_id
        new_user.role = UserRole.ADMIN
        utils.update_in_db(self.session, new_user)

    def delete_user(
            self,
            deleted_user_id: int,
            user_id: int
    ):
        user = self._get_company(
            user_id=user_id,
            permissions=[UserRole.DIRECTOR, UserRole.ADMIN]
        )

        old_user: models.User = utils.get_in_db(
            session=self.session,
            model=models.User,
            ident=deleted_user_id
        )
        utils.check_delete_status(
            admin_user_id=user_id,
            company=user.company,
            old_user=old_user
        )
        old_user.company_id = None
        old_user.role = UserRole.CUSTOMER
        utils.update_in_db(self.session, old_user)
