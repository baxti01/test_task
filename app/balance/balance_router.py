from typing import List

from fastapi import APIRouter, Depends

from app.auth.service import get_current_user
from app.balance.serializer import Balance, BalanceHistory
from app.balance.service import BalanceService
from app.database.enums import BalanceType
from app.finances.serializer import Period

router = APIRouter(
    prefix='/balance',
    tags=['Баланс']
)


@router.get('/{balance_type}', response_model=Balance)
async def get_balance(
        balance_type: BalanceType,
        user_id: int = Depends(get_current_user),
        service: BalanceService = Depends()
):
    return service.get_balance(user_id, balance_type)


@router.get('/history/{balance_type}', response_model=List[BalanceHistory])
async def get_balance_history(
        balance_type: BalanceType,
        period: Period = Depends(),
        user_id: int = Depends(get_current_user),
        service: BalanceService = Depends()
):
    return service.get_balance_history(user_id, balance_type, period)
