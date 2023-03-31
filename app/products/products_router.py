from typing import List

from fastapi import APIRouter, Depends

from app.auth.service import get_current_user
from app.products.serializer import Product, UpdateProduct, UpdateProducts
from app.products.service import ProductService

router = APIRouter(
    prefix='/products',
    tags=['Продукты']
)


@router.get('/', response_model=List[Product])
def get_products(
        user_id: int = Depends(get_current_user),
        service: ProductService = Depends()
):
    return service.get_products(user_id)


@router.get('/{product_id}', response_model=Product)
def get_product(
        product_id: int,
        user_id: int = Depends(get_current_user),
        service: ProductService = Depends()
):
    return service.get_product(user_id, product_id)


@router.put('/', response_model=List[Product])
def update_products(
        data: List[UpdateProducts],
        user_id: int = Depends(get_current_user),
        service: ProductService = Depends()
):
    return service.update_products(user_id, data)


@router.put('/{product_id}', response_model=Product)
def update_product(
        product_id: int,
        data: UpdateProduct,
        user_id: int = Depends(get_current_user),
        service: ProductService = Depends()
):
    return service.update_product(
        user_id=user_id,
        product_id=product_id,
        data=data
    )
