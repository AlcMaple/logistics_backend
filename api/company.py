from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session
from datetime import datetime

from models.company import (
    Company,
    CompanyUpdate,
    CompanyResponse,
)
from utils.validation import validate_phone
from utils.response import (
    success_response,
    not_found_response,
    param_error_response,
    internal_error_response,
)
from config.database import get_db

router = APIRouter(
    prefix="/companies",
    tags=["企业管理"],
)


@router.get(
    "/{company_id}",
    summary="获取企业详情",
    description="根据企业ID获取企业详细信息",
    responses={
        200: {
            "description": "获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "获取企业信息成功",
                        "data": {
                            "company_id": "550e8400-e29b-41d4-a716-446655440000",
                            "company_name": "数字化智能",
                            "invite_code": "ABCDEFGH",
                            "administrator_name": "张三",
                            "administrator_phone": "18800001234",
                            "administrator_password": "734567",
                            "operator_type": "CLIENT（CLIENT：用户，PLATFORM：平台）",
                            "created_at": "2022-01-01T00:00:00+00:00",
                            "updated_at": "2022-01-01T00:00:00+00:00",
                        },
                    }
                }
            },
        },
        404: {
            "description": "企业不存在",
            "content": {
                "application/json": {
                    "example": {"code": 404, "message": "企业不存在", "data": None}
                }
            },
        },
    },
)
async def get_company(company_id: str, db: Session = Depends(get_db)) -> JSONResponse:
    """
    获取企业详情

    Args:
        company_id: 企业UUID
        db: 数据库会话

    Returns:
        JSONResponse: 企业信息或错误信息
    """
    try:
        company = db.get(Company, company_id)
        if not company:
            return not_found_response("企业不存在")

        # 企业数据
        company_data = CompanyResponse(
            company_id=company.company_id,
            company_name=company.company_name,
            invite_code=company.invite_code,
            operator_type=company.operator_type,
            administrator_name=company.administrator_name,
            administrator_phone=company.administrator_phone,
            administrator_password=company.administrator_password,
            created_at=company.created_at.isoformat(),
            updated_at=company.updated_at.isoformat(),
        )

        return success_response(
            data=company_data.model_dump(), message="获取企业信息成功"
        )

    except Exception as e:
        print(f"获取企业信息错误: {e}")  # 添加调试日志
        print(f"错误类型: {type(e)}")
        return internal_error_response("获取企业信息失败")


@router.put(
    "/{company_id}",
    summary="更新企业信息",
    description="更新企业信息",
    responses={
        200: {
            "description": "更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "企业信息更新成功",
                        "data": {
                            "company_id": "550e8400-e29b-41d4-a716-446655440000",
                            "administrator_name": "李四",
                            "administrator_phone": "18800005678",
                            "administrator_password": "734567",
                            "updated_at": "2022-01-01T00:00:00+00:00",
                        },
                    }
                }
            },
        },
        400: {
            "description": "参数错误",
            "content": {
                "application/json": {
                    "example": {"code": 400, "message": "手机号格式错误", "data": None}
                }
            },
        },
        404: {"description": "企业不存在"},
    },
)
async def update_company_admin_info(
    company_id: str,
    update_data: CompanyUpdate,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    更新企业信息

    Args:
        company_id: 企业UUID
        update_data: 更新数据（必须包含姓名、手机号、密码三个字段）
        db: 数据库会话

    Returns:
        JSONResponse: 更新结果
    """
    try:
        # 获取企业
        company = db.query(Company).filter(Company.company_id == company_id).first()
        if not company:
            return not_found_response("企业不存在")

        # 验证字段不为空
        if not update_data.administrator_name.strip():
            return param_error_response("管理员姓名不能为空")

        if not update_data.administrator_phone.strip():
            return param_error_response("管理员手机号不能为空")

        if not update_data.administrator_password.strip():
            return param_error_response("管理员密码不能为空")

        # 验证手机号格式
        if not validate_phone(update_data.administrator_phone):
            return param_error_response("手机号格式错误")

        # 更新字段
        company.administrator_name = update_data.administrator_name.strip()
        company.administrator_phone = update_data.administrator_phone.strip()
        company.administrator_password = update_data.administrator_password.strip()
        company.updated_at = datetime.utcnow()

        # 保存到数据库
        db.add(company)
        db.commit()
        db.refresh(company)

        # 返回更新后的数据
        response_data = {
            "company_id": company.company_id,
            "administrator_name": company.administrator_name,
            "administrator_phone": company.administrator_phone,
            "administrator_password": company.administrator_password,
            "updated_at": company.updated_at.isoformat(),
        }

        return success_response(data=response_data, message="企业信息更新成功")

    except Exception as e:
        db.rollback()
        return internal_error_response("企业信息更新失败")
