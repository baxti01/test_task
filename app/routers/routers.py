from fastapi import APIRouter

from app.routers import auth_router

router = APIRouter()

router.include_router(auth_router.router)
