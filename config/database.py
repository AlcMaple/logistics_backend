from sqlmodel import SQLModel, create_engine, Session
from typing import Generator


from .settings import settings

# 数据库引擎
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 每次从连接池获取连接前先测试连接是否有效
    echo=settings.ENVIRONMENT == "development",  # 输出SQL日志
    pool_recycle=3600,  # 1小时回收连接，避免MySQL timeout
)


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话

    Returns:
        Generator[Session, None, None]: 数据库会话
    """
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """
    创建数据库和表

    Notes:
        SQLModel.metadata.create_all()  根据模型定义创建数据表
    """
    SQLModel.metadata.create_all(engine)