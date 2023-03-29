from decimal import Decimal
from typing import List, Union

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import utils
from app.database import models
from app.database.database import get_session
from app.database.enums import BalanceType, UserRole, TransactionType


class BalanceService:

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_balance(
            self,
            user_id: int,
            balance_type: BalanceType
    ) -> models.Balance:
        exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"У этого аакаунта пока нет баланса"
                   f"но вы можете его создать!"
        )
        owner = self._get_balance_owner(
            user_id=user_id,
            balance_type=balance_type
        )

        if owner.balance is None:
            raise exception

        return owner.balance

    def create_balance(
            self,
            user_id: int,
            balance_type: BalanceType
    ) -> models.Balance:
        owner = self._get_balance_owner(
            user_id=user_id,
            balance_type=balance_type
        )
        if owner.balance is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"У этого аакаунта уже есть баланс."
            )
        balance = models.Balance(
            balance=0.0,
            user_id=owner.id
        )
        utils.save_in_db(self.session, balance)
        return balance

    def create_transaction(
            self,
            from_id: int,
            destination_id: int,
            amount: Decimal,
            transaction_type: TransactionType
    ):
        pass

    def _get_company(
            self,
            user_id: int,
            permissions: List[UserRole]
    ) -> models.Company:
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
        return company

    def _get_balance_owner(
            self,
            user_id: int,
            balance_type: BalanceType
    ) -> Union[models.User, models.Company]:
        if balance_type == BalanceType.user:
            user = utils.get_in_db(
                session=self.session,
                model=models.User,
                ident=user_id
            )
            return user
        else:
            company = self._get_company(
                user_id=user_id,
                permissions=[UserRole.ADMIN, UserRole.DIRECTOR]
            )
            return company
