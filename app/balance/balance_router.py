import enum

from fastapi import APIRouter, Depends

from app.auth.service import get_current_user
from app.balance.serializer import Balance
from app.balance.service import BalanceService
from app.database.enums import BalanceType

router = APIRouter(
    prefix='/balance',
    tags=['Баланс']
)


@router.get('/{balance_type}', response_model=Balance)
def get_user_balance(
        balance_type: BalanceType,
        user_id: int = Depends(get_current_user),
        service: BalanceService = Depends()
):
    return service.get_balance(user_id, balance_type)
