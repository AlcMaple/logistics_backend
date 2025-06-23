import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlmodel import Session

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from config.database import get_db, engine
from config.settings import settings

"""
# 运行数据库测试
pytest tests/test_database.py -v -s

# 或运行所有测试
pytest -v -s

Args:
    -v: --verbose的简写，显示详细输出
    -s：显示 print 输出
"""


@pytest.fixture
def client():
    """
    FastAPI测试客户端

    Returns:
        TestClient: FastAPI测试客户端实例
    """
    return TestClient(app)


@pytest.fixture
def db_session():
    """
    数据库会话fixture

    Yields:
        Session: 数据库会话
    """
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    测试环境初始化

    Notes:
        scope="session": 整个测试会话只执行一次
        autouse=True: 自动使用，无需显式调用
    """
    print(f"\n🚀 开始测试 - 环境: {settings.ENVIRONMENT}")
    print(f"📊 数据库: {settings.MYSQL_DATABASE}")
    yield
    print("\n✅ 测试完成")
