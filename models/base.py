from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.sql import func

from config.database import Base


class BaseModel(Base):
    __abstract__ = True  # 抽象基类声明
    id = Column(Integer, primary_key=True, index=True)  # index，自动创建索引
    created_at = Column(
        DateTime(timezone=True),  # 带时区的时间戳类型
        server_default=func.now(),  # 数据库服务器默认值，记录当前时间
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # 数据库更新时，自动更新时间戳
    )
    is_deleted = Column(Boolean, default=False)  # 逻辑删除，非物理删除
