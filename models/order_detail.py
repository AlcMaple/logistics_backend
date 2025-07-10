from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4

from .base import BaseModel


class OrderDetail(SQLModel, table=True):
    """订单详情表"""

    __tablename__ = "order_details"

    detail_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关联字段
    order_id: str = Field(description="订单号", index=True)

    # 车辆信息
    car_plate: Optional[str] = Field(default=None, description="车牌号")

    # 地址信息
    loading_addr: Optional[str] = Field(default=None, description="装货地址")
    unloading_addr: Optional[str] = Field(default=None, description="卸货地址")

    # 联系人信息
    sender_name: Optional[str] = Field(default=None, description="装货联系人")
    sender_phone: Optional[str] = Field(default=None, description="装货联系手机号")
    receiver_name: Optional[str] = Field(default=None, description="卸货联系人")
    receiver_phone: Optional[str] = Field(default=None, description="卸货联系手机号")

    # 订单时间
    finish_time: Optional[datetime] = Field(default=None, description="订单完成时间")

    # 货物信息
    goods_volume: Optional[float] = Field(default=None, description="货物方数")
    goods_num: Optional[int] = Field(default=None, description="货物数量")
    goods_weight: Optional[float] = Field(default=None, description="货物重量")

    # 车型和服务配置
    demand_car_type: Optional[str] = Field(default=None, description="车型选择")
    is_carpool: Optional[bool] = Field(
        default=None, description="是否拼车，True-拼车，False-整车"
    )
    need_carry: Optional[bool] = Field(default=None, description="是否需要搬运服务")

    # 订单备注和总里程
    other_loading_demand: Optional[str] = Field(default=None, description="订单备注")
    total_distance: Optional[float] = Field(default=None, description="总里程(米)")

    # 照片信息
    loading_goods_imgs: Optional[str] = Field(default=None, description="装货-货物照片")
    loading_car_imgs: Optional[str] = Field(default=None, description="装货-车辆照片")
    unloading_goods_imgs: Optional[str] = Field(
        default=None, description="卸货-货物照片"
    )
    unloading_car_imgs: Optional[str] = Field(default=None, description="卸货-车辆照片")


class OrderDetailResponse(BaseModel):
    """订单详情响应模型"""

    # 基础订单信息
    path_id: str
    order_id: str
    status: str
    order_time: Optional[str] = None
    finish_time: Optional[str] = None

    # 司机信息
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None

    # 车辆信息
    car_plate: Optional[str] = None

    # 地址和联系人信息
    loading_addr: Optional[str] = None
    sender_name: Optional[str] = None
    sender_phone: Optional[str] = None
    unloading_addr: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None

    # 货物信息
    goods_volume: Optional[float] = None
    goods_num: Optional[int] = None
    goods_weight: Optional[float] = None

    # 车型和服务配置
    demand_car_type: Optional[str] = None
    is_carpool: Optional[bool] = None
    need_carry: Optional[bool] = None
    logistics_platform: Optional[str] = None

    # 订单备注和里程
    other_loading_demand: Optional[str] = None
    total_distance: Optional[float] = None

    # 照片信息
    loading_goods_imgs: Optional[str] = None
    loading_car_imgs: Optional[str] = None
    unloading_goods_imgs: Optional[str] = None
    unloading_car_imgs: Optional[str] = None
    receipt_imgs: Optional[str] = None
    parking_bill_imgs: Optional[str] = None
    highway_bill_imgs: Optional[str] = None

    # 费用信息
    total_price: int
    highway_fee: int
    parking_fee: int
    carry_fee: int
    wait_fee: int
