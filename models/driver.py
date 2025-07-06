from sqlmodel import SQLModel, Field
from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from .base import BaseModel


class Driver(SQLModel, table=True):
    __tablename__ = "driver_accounts"

    driver_account_id: str = Field(
        default_factory=lambda: str(uuid4()), primary_key=True
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    driver_name: str = Field(description="司机姓名")
    driver_phone: str = Field(description="司机手机号")
    driver_account_balance: int = Field(default=0, description="司机账户余额（分）")
