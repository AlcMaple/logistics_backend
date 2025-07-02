from fastapi import APIRouter

from .company import router as company_router
from .user import router as user_router
from .driver import router as driver_router

router = APIRouter()
finance_router = APIRouter()

router.include_router(company_router)
router.include_router(user_router)

finance_router.include_router(driver_router)
