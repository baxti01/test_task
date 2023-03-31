from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import utils
from app.database import models
from app.database.database import get_session
from app.database.enums import UserRole
from app.products.serializer import CreateProduct, UpdateProduct, UpdateProducts


class ProductService:
    PERMISSIONS = [UserRole.DIRECTOR, UserRole.ADMIN]

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_product(
            self,
            user_id: int,
            product_id: int
    ) -> models.Product:
        utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=self.PERMISSIONS
        )

        return utils.get_in_db(
            session=self.session,
            model=models.Product,
            ident=product_id
        )

    def get_products(
            self,
            user_id: int,
    ):
        user = utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=self.PERMISSIONS
        )

        return (
            self.session
            .query(models.Product)
            .filter_by(company_id=user.company_id)
            .where(models.Product.quantity > 0)
            .all()
        )

    def update_product(
            self,
            user_id: int,
            product_id: int,
            data: UpdateProduct
    ) -> models.Product:
        product = self.get_product(user_id, product_id)
        self._update_product(data=data, product=product)

        return product

    def update_products(
            self,
            user_id: int,
            data: List[UpdateProducts]
    ) -> List[models.Product]:
        products = []
        for item in data:
            product = self.get_product(user_id, item.product_id)
            self._update_product(item, product)
            products.append(product)

        return products

    def _update_product(
            self,
            data: UpdateProduct,
            product: models.Product
    ):
        product.sale_price = data.sale_price
        utils.update_in_db(self.session, product)

    @classmethod
    def create_products(
            cls,
            session: Session,
            user_id: int,
            data: List[CreateProduct]
    ):
        user = utils.check_user_permission(
            session=session,
            user_id=user_id,
            permissions=cls.PERMISSIONS
        )

        for item in data:
            try:
                product = models.Product(
                    **item.dict(),
                    user_id=user.id,
                    company_id=user.company_id
                )
                utils.save_in_db(session=session, obj=product)

            except HTTPException as e:
                if e.status_code == status.HTTP_400_BAD_REQUEST:
                    product_ = (
                        session.query(models.Product)
                        .filter_by(name=item.name)
                        .first()
                    )

                    for field, value in item:
                        setattr(product_, field, value)
                    utils.update_in_db(session, product_)

                else:
                    raise e
