from fastapi import APIRouter

from .company import router as company_router

router = APIRouter()

router.include_router(company_router)
