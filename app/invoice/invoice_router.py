from typing import List, Union

from fastapi import APIRouter, Depends

from app.auth.service import get_current_user
from app.database.enums import BalanceType
from app.invoice.serializer import CreateCompanyInvoice, CreateUserInvoice, CompanyInvoice, UserInvoice
from app.invoice.service import InvoiceService

router = APIRouter(
    prefix='/invoices',
    tags=['Оплата и история покупок']
)


@router.get('/user/{invoice_id}', response_model=UserInvoice)
def get_user_invoice(
        invoice_id: int,
        user_id: int = Depends(get_current_user),
        service: InvoiceService = Depends()
):
    return service.get_user_invoice(
        invoice_id=invoice_id,
        user_id=user_id
    )


@router.get('/user', response_model=List[UserInvoice])
def get_user_invoices(
        user_id: int = Depends(get_current_user),
        service: InvoiceService = Depends()
):
    return service.get_user_invoices(
        user_id=user_id
    )


@router.get(
    '/company/{invoice_id}',
    response_model=CompanyInvoice,
    response_model_by_alias=False
)
def get_company_invoice(
        invoice_id: int,
        user_id: int = Depends(get_current_user),
        service: InvoiceService = Depends()
):
    return service.get_company_invoice(
        invoice_id=invoice_id,
        user_id=user_id
    )


@router.get(
    '/company/',
    response_model=List[CompanyInvoice],
    response_model_by_alias=False
)
def get_company_invoices(
        user_id: int = Depends(get_current_user),
        service: InvoiceService = Depends()
):
    return service.get_company_invoices(
        user_id=user_id
    )


@router.post(
    '/company',
    response_model=CompanyInvoice,
    response_model_by_alias=False
)
def pay_for_company(
        data: CreateCompanyInvoice,
        user_id: int = Depends(get_current_user),
        service: InvoiceService = Depends()
):
    return service.create_company_invoice(
        data=data,
        user_id=user_id
    )


@router.post('/user', response_model=UserInvoice)
def pay_for_user(
        data: CreateUserInvoice,
        user_id: int = Depends(get_current_user),
        service: InvoiceService = Depends()
):
    invoice, products_data = service.create_user_invoice(
        data=data,
        user_id=user_id
    )

    inv: UserInvoice = UserInvoice.from_orm(invoice)
    inv.products = products_data

    return inv
