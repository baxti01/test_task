from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.products.serializer import Product, CreateProduct, SellProducts, InvoiceProduct
from app.worker.serializer import InvoiceWorker


class BaseInvoice(BaseModel):
    date: datetime = datetime.now()
    # quantity: float


class Invoice(BaseInvoice):
    id: int
    user_id: Optional[int] = None
    company_id: Optional[int] = None


class UserInvoice(Invoice):
    to_pay: Decimal
    products: Optional[List[InvoiceProduct]] = None
    worker: Optional[InvoiceWorker] = None

    class Config:
        orm_mode = True


class CompanyInvoice(Invoice):
    to_pay: Decimal

    products: Optional[List[Product]] = None

    class Config:
        orm_mode = True


class CreateCompanyInvoice(BaseInvoice):
    products: List[CreateProduct]


class CreateUserInvoice(BaseInvoice):
    user_id: Optional[int] = None
    products: Optional[List[SellProducts]] = None
