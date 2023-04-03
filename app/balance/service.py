from datetime import datetime
from decimal import Decimal
from typing import List, Union

from fastapi import Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app import utils
from app.database import models
from app.database.database import get_session
from app.database.enums import BalanceType, UserRole, TransactionType
from app.finances.serializer import Period


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
            detail=f"У этого аккаунта пока нет баланса"
                   f"но вы можете его создать!"
        )
        owner = self._get_balance_owner(
            user_id=user_id,
            balance_type=balance_type
        )

        if owner.balance is None:
            raise exception

        return owner.balance

    def get_balance_history(
            self,
            user_id: int,
            balance_type: BalanceType,
            period: Period
    ):
        owner = self._get_balance_owner(
            user_id=user_id,
            balance_type=balance_type
        )

        return (
            self.session
            .query(models.BalanceHistory)
            .filter(
                and_(
                    models.BalanceHistory.balance_id == owner.balance.id,
                    models.BalanceHistory.date >= period.from_date,
                    models.BalanceHistory.date < period.to_date
                )
            )
            .all()
        )

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
        return user.company

    def _get_balance_owner(
            self,
            user_id: int,
            balance_type: BalanceType
    ) -> Union[models.User, models.Company]:
        if balance_type == BalanceType.USER:
            user: models.User = utils.get_in_db(
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

    @classmethod
    def create_balance(
            cls,
            session: Session,
            ident: int,
            balance_type: BalanceType
    ):
        balance = models.Balance(
            balance=Decimal(0.0)
        )
        if balance_type == BalanceType.USER:
            balance.user_id = ident
        else:
            balance.company_id = ident

        utils.save_in_db(session, balance)

    @classmethod
    def change_balance(
            cls,
            amount: Decimal,
            transaction_type: TransactionType,
            date: datetime,
            balance: models.Balance,
            invoice: models.Invoice = None,
            finance: models.Finance = None
    ) -> tuple[models.Balance, models.BalanceHistory]:
        balance_history = models.BalanceHistory(
            prev_balance=balance.balance,
            date=balance.date,
            amount=amount,
            transaction_type=transaction_type,
            invoice_id=balance.invoice_id,
            finance_id=balance.finance_id,
            balance_id=balance.id
        )

        if transaction_type == TransactionType.INCOME:
            balance.balance += amount
        else:
            balance.balance -= amount

        balance.date = date
        if invoice:
            balance.invoice_id = invoice.id
        if finance:
            balance.finance_id = finance.id

        return balance, balance_history
