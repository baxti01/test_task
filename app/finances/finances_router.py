from typing import List

from fastapi import APIRouter, Depends

from app.auth.service import get_current_user
from app.finances.serializer import Finance, Period, CreateFinance
from app.finances.service import FinanceService

router = APIRouter(
    prefix='/finances',
    tags=['Расхды и доходы']
)


@router.get('/', response_model=List[Finance])
def get_finances(
        period: Period = Depends(),
        user_id: int = Depends(get_current_user),
        service: FinanceService = Depends()
):
    return service.get_finances(user_id=user_id, period=period)


@router.post('/', response_model=Finance)
def create_finance(
        data: CreateFinance,
        user_id: int = Depends(get_current_user),
        service: FinanceService = Depends()
):
    return service.create_finances(
        user_id=user_id,
        data=data
    )


@router.post('/replenish_balance', response_model=Finance)
def replenish_balance(
        data: CreateFinance,
        user_id: int = Depends(get_current_user),
        service: FinanceService = Depends()
):
    return service.replenish_balance(
        user_id=user_id,
        data=data
    )
