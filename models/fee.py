from sqlmodel import SQLModel, Field
from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from .enums import OrderStatusEnum
from .base import BaseModel
from pydantic import ValidationInfo, field_validator


class Fee(SQLModel, table=True):
    __tablename__ = "fees"

    fee_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    path_id: str = Field(description="运单号")
    order_id: str = Field(description="订单号")
    status: OrderStatusEnum = Field(
        default=OrderStatusEnum.APPEALING, description="订单状态"
    )
    total_price: int = Field(default=0, description="基本路费（分）")
    driver_fee: int = Field(default=0, description="司机费用（分）")
    highway_fee: int = Field(default=0, description="高速费（分）")
    parking_fee: int = Field(default=0, description="停车费（分）")
    carry_fee: int = Field(default=0, description="搬运费（分）")
    wait_fee: int = Field(default=0, description="等候费（分）")
    company_id: Optional[str] = Field(default=None, description="公司ID")
    driver_account_id: Optional[str] = Field(default=None, description="司机账户ID")
    order_time: Optional[datetime] = Field(default_factory=datetime.utcnow)
    receipt_imgs: Optional[str] = Field(default=None, description="回单照片路径")
    highway_bill_imgs: Optional[str] = Field(default="", description="高速费图片")
    parking_bill_imgs: Optional[str] = Field(default="", description="停车费图片")
    receipt_reject_reason: Optional[str] = Field(
        default=None, description="回单驳回原因"
    )
    bill_reject_reason: Optional[str] = Field(default=None, description="账单驳回原因")
    except_highway_fee: int = Field(default=0, description="期望高速费（分）")
    except_parking_fee: int = Field(default=0, description="期望停车费（分）")
    except_carry_fee: int = Field(default=0, description="期望搬运费（分）")
    except_wait_fee: int = Field(default=0, description="期望等候费（分）")
    logistics_platform: Optional[str] = Field(
        default=None, description="派单渠道（物流平台）"
    )
    settlement_enable: bool = Field(default=False, description="是否发起结算操作")


class FeeListRequest(BaseModel):
    """费用列表请求模型"""

    page: int = Field(default=1, ge=1, description="页码，从1开始")
    size: int = Field(default=10, ge=1, le=100, description="每页数量，最大100")
    search: Optional[str] = Field(default=None, description="搜索关键词（订单号）")
    status: Optional[str] = Field(default=None, description="费用状态筛选")


class FeeResponse(BaseModel):
    """费用响应模型"""

    fee_id: str
    path_id: str
    order_id: str
    status: str
    total_price: int
    driver_fee: int
    highway_fee: int
    parking_fee: int
    carry_fee: int
    wait_fee: int
    order_time: str
    highway_bill_imgs: Optional[str] = ""
    parking_bill_imgs: Optional[str] = ""
    company_id: Optional[str] = None
    driver_id: Optional[str] = None
    created_at: str
    updated_at: str


class FeeListResponse(BaseModel):
    """费用列表响应模型"""

    items: List[FeeResponse] = Field(description="费用列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")


class FeePayRequest(BaseModel):
    """费用支付请求模型"""

    fee_id: str = Field(description="费用ID")
    company_id: str = Field(description="公司ID")
    total_price: int = Field(description="基本路费（分）")
    highway_fee: int = Field(description="高速费（分）")
    parking_fee: int = Field(description="停车费（分）")
    carry_fee: int = Field(description="搬运费（分）")
    wait_fee: int = Field(description="等候费（分）")
    driver_account_id: str = Field(description="司机账户ID")


class FeeRejectRequest(BaseModel):
    fee_id: str = Field(..., description="费用ID")
    reject_type: str = Field(..., description="驳回类型: 'bill'或'receipt'")
    reject_reason: str = Field(..., description="驳回原因")

    # 以下字段仅在驳回类型为bill时需要
    reject_highway_fee: Optional[int] = Field(
        None, ge=0, description="驳回高速费金额（分）"
    )
    reject_parking_fee: Optional[int] = Field(
        None, ge=0, description="驳回停车费金额（分）"
    )

    @field_validator("reject_type")
    @classmethod
    def validate_reject_type(cls, v: str) -> str:
        if v not in ["bill", "receipt"]:
            raise ValueError("驳回类型必须是'bill'或'receipt'")
        return v

    @field_validator("reject_highway_fee", "reject_parking_fee")
    @classmethod
    def validate_reject_fees(
        cls, v: Optional[int], info: ValidationInfo
    ) -> Optional[int]:
        if info.data.get("reject_type") == "bill" and v is None:
            raise ValueError(f"当驳回类型为bill时，{info.field_name}不能为空")
        return v


class FeeSettlementRequest(BaseModel):
    fee_id: str = Field(..., description="费用ID")
