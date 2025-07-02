from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import uuid4
from datetime import datetime
from .enums import OrderStatusEnum


class Fee(SQLModel, table=True):
    __tablename__ = "fees"

    fee_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    path_id: str = Field(description="运单号")
    order_id: str = Field(description="订单号")
    status: OrderStatusEnum = Field(
        default=OrderStatusEnum.PENDING_PAYMENT, description="订单状态"
    )
    total_price: int = Field(default=0, description="基本路费（分）")
    driver_fee: int = Field(default=0, description="司机费用（分）")
    highway_fee: int = Field(default=0, description="高速费（分）")
    parking_fee: int = Field(default=0, description="停车费（分）")
    carry_fee: int = Field(default=0, description="搬运费（分）")
    wait_fee: int = Field(default=0, description="等候费（分）")
    order_time: Optional[datetime] = Field(default_factory=datetime.utcnow)
    highway_bill_imgs: Optional[str] = Field(default="", description="高速费图片")
    parking_bill_imgs: Optional[str] = Field(default="", description="停车费图片")
