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

    # 启用ORM 模式，支持 from_orm 方法
    from_attributes = True
    # JSON序列化使用枚举值
    use_enum_values = True


def generate_uuid() -> str:
    """
    生成UUID字符串

    Returns:
        str: UUID字符串

    Notes:
        企业级实践：统一UUID生成函数，便于后续扩展和管理
    """
    return str(uuid.uuid4())
