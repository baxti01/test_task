from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import models
from app.database.database import get_session
from app.database.enums import UserRole
from app.company.serializer import CreateCompany, UpdateCompany
from app import utils


class CompanyService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get_company(
            self,
            user_id: int,
            permissions: List[UserRole]
    ):
        user = utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=permissions
        )
        company: models.Company = utils.get_in_db(
            session=self.session,
            model=models.Company,
            ident=user.company_id
        )
        return company, user

    def get_company(self, user_id: int) -> models.Company:
        company, _ = self._get_company(
            user_id=user_id,
            permissions=[UserRole.ADMIN, UserRole.DIRECTOR]
        )
        return company

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

        return company

    def update_company(
            self,
            user_id: int,
            data: UpdateCompany
    ) -> models.Company:
        user = utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=[UserRole.DIRECTOR]
        )
        company: models.Company = utils.get_in_db(
            session=self.session,
            model=models.Company,
            ident=user.company_id
        )

        for field, value in data:
            setattr(company, field, value)

        utils.update_in_db(self.session, company)

        return company

    def delete_company(
            self,
            user_id: int
    ):
        user, company = self._get_company(user_id, [UserRole.DIRECTOR])
        utils.delete_in_db(self.session, company)

        user.role = UserRole.CUSTOMER
        user.company_id = None
        utils.update_in_db(self.session, user)

    def add_user(
            self,
            added_user_id: int,
            user_id: int
    ):
        company, _ = self._get_company(
            user_id=user_id,
            permissions=[UserRole.DIRECTOR, UserRole.ADMIN]
        )

        new_user = utils.check_user_company(
            session=self.session,
            user_id=added_user_id
        )

        company.users.append(new_user)
        utils.update_in_db(self.session, company)

    def delete_user(
            self,
            deleted_user_id: int,
            user_id: int
    ):
        company, _ = self._get_company(
            user_id=user_id,
            permissions=[UserRole.DIRECTOR, UserRole.ADMIN]
        )

        old_user: models.User = utils.get_in_db(
            session=self.session,
            model=models.User,
            ident=deleted_user_id
        )
        self.check_delete_status(
            admin_user_id=user_id,
            company=company,
            old_user=old_user
        )
        old_user.company_id = None
        old_user.role = UserRole.CUSTOMER
        utils.update_in_db(self.session, old_user)

    def check_delete_status(
            self,
            admin_user_id: int,
            company: models.Company,
            old_user: models.User
    ):
        if old_user in company.users:
            if old_user.id == admin_user_id or \
                    old_user.role == UserRole.DIRECTOR:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Вы не сможете удалить самого себя"
                           "или директора из компании!"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь не ноходится в компании!"
            )
