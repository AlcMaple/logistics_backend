from fastapi import APIRouter

from .company import router as company_router
from .user import router as user_router

router = APIRouter()

router.include_router(company_router)
router.include_router(user_router)
