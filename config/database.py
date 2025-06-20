from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .settings import settings

# 数据库引擎
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 每次从连接池获取连接前先测试连接是否有效
    echo=settings.ENVIRONMENT == "development",  # 输出SQL日志
)

# 会话管理
"""
    每次请求创建一个新会话，请求结束后自动关闭。保证事务隔离与连接管理
    Args：
        bind=engine: 绑定数据库引擎
        autocommit=False: 事务自动提交
        autoflush=False: 自动刷新
"""
SessionManager = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# 数据表基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话
    """
    db = SessionManager()
    try:
        yield db
    finally:
        db.close()
