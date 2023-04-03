from decimal import Decimal
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app import utils
from app.database import models
from app.database.database import get_session
from app.database.enums import UserRole
from app.products.serializer import CreateProduct, UpdateProduct, UpdateProducts, SellProducts, InvoiceProduct


class ProductService:
    PERMISSIONS = [
        UserRole.DIRECTOR, UserRole.ADMIN,
        UserRole.WORKER_DIRECTOR, UserRole.WORKER_ADMIN,
        UserRole.WORKER_USER
    ]

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_product(
            self,
            user_id: int,
            product_id: int,
            permissions: Optional[List[UserRole]] = None
    ) -> models.Product:
        utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=permissions if permissions else self.PERMISSIONS
        )

        return utils.get_in_db(
            session=self.session,
            model=models.Product,
            ident=product_id
        )

    def get_products(
            self,
            user_id: int,
            permissions: Optional[List[UserRole]] = None
    ):
        user = utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=permissions if permissions else self.PERMISSIONS
        )

        return (
            self.session
            .query(models.Product)
            .filter(
                and_(
                    models.Product.company_id == user.company_id,
                    models.Product.quantity > 0
                )
            )
            .all()
        )

    def update_product(
            self,
            user_id: int,
            product_id: int,
            data: UpdateProduct
    ) -> models.Product:
        product = self.get_product(
            user_id=user_id,
            product_id=product_id,
            permissions=[UserRole.DIRECTOR, UserRole.ADMIN]
        )
        self._update_product(data=data, product=product)

        return product

    def update_products(
            self,
            user_id: int,
            data: List[UpdateProducts]
    ) -> List[models.Product]:
        products = []
        for item in data:
            product = self.get_product(
                user_id=user_id,
                product_id=item.product_id,
                permissions=[UserRole.DIRECTOR, UserRole.ADMIN]
            )
            self._update_product(item, product)
            products.append(product)

        return products

    def _update_product(
            self,
            data: UpdateProduct,
            product: models.Product
    ):
        for field, value in data:
            setattr(product, field, value)
        utils.update_in_db(self.session, product)

    @classmethod
    def create_products(
            cls,
            session: Session,
            data: List[CreateProduct],
            user: models.User,
    ) -> tuple[List[models.Product], models.User, Decimal]:
        user = utils.check_user_permission(
            session=session,
            user=user,
            permissions=[UserRole.DIRECTOR, UserRole.ADMIN]
        )
        products = []
        to_pay = Decimal(0.0)
        for item in data:
            product = (
                session.query(models.Product)
                .filter_by(name=item.name)
                .first()
            )

            if product:
                product = (
                    session.query(models.Product)
                    .filter_by(name=item.name)
                    .first()
                )

                for field, value in item:
                    setattr(product, field, value)

            else:
                product = models.Product(
                    **item.dict(),
                    user_id=user.id,
                    sale_quantity=0,
                    company_id=user.company_id
                )

            to_pay = product.purchase_price * Decimal(product.quantity)
            products.append(product)

        return products, user, to_pay

    @classmethod
    def sell_products(
            cls,
            session: Session,
            user_id: int,
            data: List[SellProducts]
    ) -> tuple[
        List[models.Product], List[InvoiceProduct],
        models.User, Decimal
    ]:
        user = utils.check_user_permission(
            session=session,
            user_id=user_id,
            permissions=[UserRole.WORKER_USER, UserRole.WORKER_ADMIN]
        )

        products = []
        products_data = []
        to_pay = Decimal(0.0)

        for item in data:
            product: models.Product = utils.get_in_db(
                session=session,
                model=models.Product,
                ident=item.product_id
            )

            if product.sale_quantity == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Товар с названием {product.name} нет в наличии"
                )
            if product.sale_quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Товар с названием {product.name} доступно "
                           f"в таком количестве {product.sale_quantity} а "
                           f"не {item.quantity}"
                )

            product.quantity -= item.quantity
            product.sale_quantity -= item.quantity
            to_pay = product.sale_price * Decimal(item.quantity)

            product_data = InvoiceProduct.from_orm(product)
            product_data.quantity = item.quantity
            products_data.append(product_data)

            products.append(product)

        return products, products_data, user, to_pay
