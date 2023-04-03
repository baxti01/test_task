from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.database.enums import UnitOfMeasureType


class BaseProduct(BaseModel):
    name: str
    purchase_price: Decimal = Field(alias='price')
    quantity: float
    unit_of_measure: UnitOfMeasureType
    date: datetime = datetime.now()


class Product(BaseProduct):
    id: int
    user_id: Optional[int] = None
    company_id: int
    sale_quantity: float
    sale_price: Optional[Decimal] = Decimal(0.0)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class CreateProduct(BaseProduct):
    pass


class UpdateProduct(BaseModel):
    sale_price: Decimal
    sale_quantity: float


class UpdateProducts(UpdateProduct):
    product_id: int


class SellProducts(BaseModel):
    product_id: int
    quantity: float


class InvoiceProduct(BaseModel):
    id: int
    name: str
    sale_price: Optional[Decimal] = Field(Decimal(0.0), alias='price')
    unit_of_measure: UnitOfMeasureType
    date: datetime = datetime.now()
    quantity: float

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
