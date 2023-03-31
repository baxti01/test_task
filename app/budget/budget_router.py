from typing import List

from fastapi import APIRouter, Depends

from app.auth.service import get_current_user
from app.budget.serializer import Budget, BudgetHistory
from app.budget.service import BudgetService
from app.finances.serializer import Period

router = APIRouter(
    prefix='/budget',
    tags=['Бюджет']
)


@router.get('/', response_model=Budget)
def get_budget(
        user_id: int = Depends(get_current_user),
        service: BudgetService = Depends()
):
    return service.get_budget(user_id=user_id)


@router.get('/history', response_model=List[BudgetHistory])
def get_budget_history(
        period: Period = Depends(),
        user_id: int = Depends(get_current_user),
        service: BudgetService = Depends()
):
    return service.get_budget_history(
        user_id=user_id,
        period=period
    )
