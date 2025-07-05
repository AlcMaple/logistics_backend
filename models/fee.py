from sqlmodel import SQLModel, Field
from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from .enums import OrderStatusEnum
from .base import BaseModel


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
    order_time: Optional[datetime] = Field(default_factory=datetime.utcnow)
    highway_bill_imgs: Optional[str] = Field(default="", description="高速费图片")
    parking_bill_imgs: Optional[str] = Field(default="", description="停车费图片")


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
    created_at: str
    updated_at: str


class FeeListResponse(BaseModel):
    """费用列表响应模型"""

    items: List[FeeResponse] = Field(description="费用列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")
