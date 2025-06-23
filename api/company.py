from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from datetime import datetime

from models.company import (
    Company,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    generate_invite_code,
)

from utils.validation import validate_phone
from config.database import get_db

router = APIRouter(
    prefix="/companies",
    tags=["企业管理"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "企业不存在"},
    },
)


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="获取企业详情",
    response_description="企业详细信息",
)
async def get_company(company_id: str, db: Session = Depends(get_db)):
    """
    根据ID获取企业详细信息

    - **company_id**: 企业UUID
    """
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="企业不存在",
        )
    return company


@router.patch(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="更新企业信息",
    response_description="更新后的企业信息",
)
async def update_company_admin_info(
    company_id: str,
    update_data: CompanyUpdate,
    db: Session = Depends(get_db),
):
    """
    更新企业信息

    - **company_id**: 企业UUID
    - **administrator_name**: 管理员姓名
    - **administrator_phone**: 手机号
    - **administrator_password**: 密码
    """
    # 获取企业
    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="企业不存在",
        )

    # 验证手机号
    if update_data.administrator_phone and not validate_phone(
        update_data.administrator_phone
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式错误",
        )

    # 更新所有字段
    company.administrator_name = update_data.administrator_name
    company.administrator_phone = update_data.administrator_phone
    company.administrator_password = update_data.administrator_password
    company.updated_at = datetime.utcnow()

    try:
        db.add(company)
        db.commit()
        db.refresh(company)
        return company
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="企业信息更新失败",
        )
