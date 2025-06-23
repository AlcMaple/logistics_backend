from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import random
import string

from .base import BaseModel, generate_uuid
from .enums import OperatorTypeEnum


class Company(BaseModel, table=True):
    """
    企业模型
    """

    __tablename__ = "companies"

    company_id: str = Field(
        default_factory=generate_uuid, primary_key=True, description="企业ID"
    )

    company_name: str = Field(
        max_length=100, description="企业名称", example="数字化智能"
    )

    invite_code: str = Field(
        max_length=8, unique=True, description="企业邀请码", example="ABCDEFGH"
    )

    operator_type: OperatorTypeEnum = Field(
        default=OperatorTypeEnum.CLIENT, description="操作员类型"
    )

    wallet: float = Field(
        default=0.0, ge=0.0, description="企业钱包余额"  # 余额不能为负数
    )

    administrator_name: str = Field(
        max_length=50, description="管理员姓名", example="张三"
    )

    administrator_phone: str = Field(max_length=20, description="管理员手机号")

    administrator_password: str = Field(max_length=255, description="哈希密码")

    # 关联关系：一个企业有多个用户
    users: List["User"] = Relationship(back_populates="company")


class CompanyCreate(BaseModel):
    """企业创建模型"""

    company_name: str = Field(max_length=100)
    administrator_name: str = Field(
        None, max_length=50, description="管理员姓名", example="李四"
    )
    administrator_phone: str = Field(
        None,
        max_length=20,
        description="管理员手机号",
        example="18800001234",
    )
    administrator_password: str = Field(
        None, max_length=32, description="管理员密码", example="734567"
    )
    operator_type: OperatorTypeEnum = OperatorTypeEnum.CLIENT


class CompanyUpdate(BaseModel):
    """企业更新模型"""

    administrator_name: str = Field(None, max_length=50)
    administrator_phone: str = Field(None, max_length=20)
    administrator_password: str = Field(None, max_length=255)


class CompanyResponse(BaseModel):
    """企业响应模型"""

    company_id: str
    company_name: str
    invite_code: str
    operator_type: OperatorTypeEnum
    administrator_name: str
    administrator_phone: str
    created_at: str
    updated_at: str


def generate_invite_code() -> str:
    """
    生成8位大写字母邀请码

    Returns:
        str: 8位大写字母邀请码
    """
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    return "".join(random.choices(letters, k=8))
