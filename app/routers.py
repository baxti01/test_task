from fastapi import APIRouter

from app.balance import balance_router
from app.company import company_router
from app.auth import auth_router

router = APIRouter()

router.include_router(auth_router.router)
router.include_router(company_router.router)
router.include_router(balance_router.router)
