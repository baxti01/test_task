from fastapi import APIRouter

from app.balance import balance_router
from app.budget import budget_router
from app.company import company_router
from app.auth import auth_router
from app.finances import finances_router
from app.products import products_router
from app.worker import worker_router

router = APIRouter()

router.include_router(auth_router.router)
router.include_router(company_router.router)
router.include_router(worker_router.router)
router.include_router(balance_router.router)
router.include_router(budget_router.router)
router.include_router(finances_router.router)
router.include_router(products_router.router)
