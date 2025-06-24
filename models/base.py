from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid


class BaseModel(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )


class Config:
    """SQLModel 配置"""

    from_attributes = True
    use_enum_values = True


def generate_uuid() -> str:
    """
    生成UUID字符串

    Returns:
        str: UUID字符串
    """
    return str(uuid.uuid4())
