from fastapi import Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import utils
from app.balance.service import BalanceService
from app.database import models
from app.database.database import get_session
from app.database.enums import TransactionType, UserRole
from app.finances.serializer import CreateFinance
from app.finances.service import FinanceService
from app.invoice.serializer import CreateCompanyInvoice, CreateUserInvoice, UserInvoice
from app.products.service import ProductService


class InvoiceService:

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_user_invoice(
            self,
            invoice_id: int,
            user_id: int,
    ):
        user = utils.get_in_db(
            session=self.session,
            model=models.User,
            ident=user_id
        )
        invoice = (
            self.session.query(models.Invoice)
            .filter_by(id=invoice_id, user_id=user.id)
            .first()
        )
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Запись с идентификатором {invoice_id} нет в базе!"
            )

        return invoice

    def get_user_invoices(
            self,
            user_id: int,
    ):
        user = utils.get_in_db(
            session=self.session,
            model=models.User,
            ident=user_id
        )

        return (
            self.session.query(models.Invoice)
            .filter_by(user_id=user.id)
            .all()
        )

    def get_company_invoice(
            self,
            invoice_id: int,
            user_id: int,
    ):
        user = utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=[
                UserRole.DIRECTOR, UserRole.ADMIN,
                UserRole.WORKER_DIRECTOR, UserRole.WORKER_ADMIN
            ]
        )
        invoice = (
            self.session.query(models.Invoice)
            .filter_by(id=invoice_id)
            .filter(or_(
                models.Invoice.user_id == user.company_id,
                models.Invoice.company_id == user.company_id
            ))
            .first()
        )
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Запись с идентификатором {invoice_id} нет в базе!"
            )

        return invoice

    def get_company_invoices(
            self,
            user_id: int,
    ):
        user = utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=[
                UserRole.DIRECTOR, UserRole.ADMIN,
                UserRole.WORKER_DIRECTOR, UserRole.WORKER_ADMIN
            ]
        )

        return (
            self.session.query(models.Invoice)
            .filter(or_(
                models.Invoice.user_id == user.company_id,
                models.Invoice.company_id == user.company_id
            ))
            .all()
        )

    def create_company_invoice(
            self,
            data: CreateCompanyInvoice,
            user_id: int
    ) -> models.Invoice:
        try:
            with self.session.begin():
                user = utils.check_user_permission(
                    session=self.session,
                    user_id=user_id,
                    permissions=[UserRole.DIRECTOR, UserRole.ADMIN]
                )

                products_data = data.products
                invoice = models.Invoice(
                    **data.dict(exclude={'products'}),
                    company_id=user.company_id
                )

                if products_data:
                    products, user, to_pay = ProductService.create_products(
                        session=self.session,
                        data=products_data,
                        user=user
                    )
                    invoice.products += products

                self.session.add(invoice)

                balance, balance_history = BalanceService.change_balance(
                    amount=to_pay,
                    transaction_type=TransactionType.EXPENSE,
                    date=data.date,
                    balance=user.company.balance,
                    invoice=invoice
                )
                invoice.to_pay = to_pay
                self.session.add(balance_history)

                return invoice
        except Exception as e:
            self.session.rollback()
            raise e

    def create_user_invoice(
            self,
            data: CreateUserInvoice,
            user_id: int
    ):
        try:
            with self.session.begin():
                exclude = {'products'}
                buyer = None
                if data.user_id:
                    buyer = utils.get_in_db(
                        session=self.session,
                        model=models.User,
                        ident=data.user_id
                    )
                else:
                    exclude.update({'user_id'})

                products, products_data, user, to_pay = ProductService.sell_products(
                    session=self.session,
                    user_id=user_id,
                    data=data.products,
                )

                invoice = models.Invoice(
                    **data.dict(exclude=exclude),
                    to_pay=to_pay,
                    company_id=user.company_id,
                    worker_id=user.worker_id,
                    products=products
                )
                self.session.add(invoice)

                if buyer:
                    balance, balance_history = BalanceService.change_balance(
                        amount=to_pay,
                        transaction_type=TransactionType.EXPENSE,
                        date=data.date,
                        balance=buyer.balance,
                        invoice=invoice
                    )
                    self.session.add(balance_history)

                finance_data = CreateFinance(
                    date=data.date,
                    transaction_type=TransactionType.INCOME,
                    amount=to_pay
                )

                finance, budget, budget_history = FinanceService.create_finance(
                    data=finance_data,
                    company=user.company
                )
                self.session.add(finance)
                self.session.add(budget_history)
                return invoice, products_data
        except Exception as e:
            self.session.rollback()
            raise e
