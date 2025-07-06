from sqlmodel import SQLModel, Field
from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from .base import BaseModel
from .enums import RechargeStatusEnum


class Account(SQLModel, table=True):
    __tablename__ = "company_accounts"

    company_account_id: str = Field(
        default_factory=lambda: str(uuid4()), primary_key=True
    )
    company_id: str = Field(description="客户公司ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    company_account_updatetime: datetime = Field(default_factory=datetime.utcnow)
    company_account_balance: int = Field(default=0, description="账户余额（分）")
    company_account_balance_warning_val: int = Field(
        default=0, description="余额预警值（分）"
    )
    company_account_balance_warning_phone: Optional[str] = Field(
        default=None, description="预警手机号"
    )
    company_account_balance_warning_enable: bool = Field(
        default=False, description="是否启用余额预警"
    )
    recharge_status: RechargeStatusEnum = Field(
        default=RechargeStatusEnum.UNDER_REVIEW, description="充值状态"
    )
    recharge_time: Optional[datetime] = Field(default=None, description="充值时间")
    recharge_name: Optional[str] = Field(default=None, description="充值人姓名")
    recharge_phone: Optional[str] = Field(default=None, description="充值人手机号")
    recharge_amount: int = Field(default=0, description="充值金额（分）")
    received_amount: int = Field(default=0, description="到账金额（分）")


class AccountRecharge(BaseModel):
    company_account_id: str = Field(description="账户ID")
    recharge_name: str = Field(description="充值人姓名")
    recharge_phone: str = Field(description="充值人手机号")
    recharge_amount: int = Field(description="充值金额（分）")


class AccountResponse(BaseModel):
    company_account_id: str
    company_id: str
    created_at: datetime
    updated_at: datetime
    company_account_updatetime: datetime
    company_account_balance: int
    company_account_balance_warning_val: int
    company_account_balance_warning_phone: Optional[str]
    company_account_balance_warning_enable: bool
    recharge_status: str
    recharge_time: Optional[datetime]
    recharge_name: Optional[str]
    recharge_phone: Optional[str]
    recharge_amount: int
    received_amount: int


class PaginatedAccountResponse(BaseModel):
    items: List[AccountResponse]
    total: int
    page: int
    size: int
    total_pages: int


class BalanceWarningUpdateRequest(BaseModel):
    company_account_id: str
    company_account_balance_warning_val: int
    company_account_balance_warning_phone: str
    company_account_balance_warning_enable: bool
