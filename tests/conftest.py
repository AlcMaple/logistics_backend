import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlmodel import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from config.database import get_db, engine
from config.settings import settings


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
    """
    print(f"\n🚀 开始测试 - 环境: {settings.ENVIRONMENT}")
    print(f"📊 数据库: {settings.MYSQL_DATABASE}")
    yield
    print("\n✅ 测试完成")
