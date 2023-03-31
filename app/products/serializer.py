from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.database.enums import UnitOfMeasureType


class BaseProduct(BaseModel):
    name: str
    purchase_price: Decimal
    sale_price: Optional[Decimal] = Decimal(0.0)
    quantity: float
    unit_of_measure: UnitOfMeasureType
    date: datetime = datetime.now()


class Product(BaseProduct):
    id: int
    user_id: Optional[int] = None
    company_id: int

    class Config:
        orm_mode = True


class CreateProduct(BaseProduct):
    pass


class UpdateProduct(BaseModel):
    sale_price: Decimal


class UpdateProducts(UpdateProduct):
    product_id: int
