import pytest
from fastapi.testclient import TestClient
from websocket.manager import connected_clients
from main import app
import json
import asyncio


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
async def websocket_connections(client):
    """
    建立三种类型的WebSocket连接用于测试
    """
    # 平台端连接
    with client.websocket_connect("/api/platform") as platform:
        # 客户端连接
        with client.websocket_connect("/api/client") as client_conn:
            # 司机端连接
            with client.websocket_connect("/api/driver") as driver:
                yield platform, client_conn, driver


@pytest.mark.asyncio
async def test_websocket_connections(websocket_connections):
    """
    测试WebSocket连接是否正常建立
    """
    platform, client_conn, driver = await websocket_connections.__anext__()

    # 检查连接池中的连接数量
    assert len(connected_clients["platform"]) == 1
    assert len(connected_clients["client"]) == 1
    assert len(connected_clients["driver"]) == 1


@pytest.mark.asyncio
async def test_fee_submission_push_notification(
    client, db_session, websocket_connections
):
    """
    测试司机提交费用后的推送功能
    """
    platform, client_conn, driver = await websocket_connections.__anext__()

    # 模拟司机提交费用
    fee_data = {
        "driver_id": "driver_123",
        "order_id": "order_456",
        "path_id": "path_789",
        "highway_fee": 1000,
        "parking_fee": 200,
        "carry_fee": 300,
        "wait_fee": 150,
        "highway_bill_imgs": "img1.jpg,img2.jpg",
        "parking_bill_imgs": "parking.jpg",
    }

    # 发送POST请求
    response = client.post("/finance/api/driver", json=fee_data)
    assert response.status_code == 200

    # 检查平台端和客户端是否收到推送
    platform_data = platform.receive_json()
    assert platform_data["type"] == "fee_submitted"
    assert platform_data["data"]["driver_id"] == "driver_123"

    client_data = client_conn.receive_json()
    assert client_data["type"] == "fee_submitted"
    assert client_data["data"]["order_id"] == "order_456"

    # 司机端不应该收到推送
    with pytest.raises(Exception):
        driver.receive_json(timeout=1)


@pytest.mark.asyncio
async def test_fee_confirmation_push_notification(
    client, db_session, websocket_connections
):
    """
    测试司机确认费用后的推送功能
    """
    platform, client_conn, driver = await websocket_connections.__anext__()

    # 模拟司机确认费用
    confirm_data = {
        "driver_id": "driver_123",
        "order_id": "order_456",
        "path_id": "path_789",
    }

    response = client.post("/finance/api/driver/confirm", json=confirm_data)
    assert response.status_code == 200

    # 检查平台端和客户端是否收到推送
    platform_data = platform.receive_json()
    assert platform_data["type"] == "fee_confirmed"

    client_data = client_conn.receive_json()
    assert client_data["data"]["path_id"] == "path_789"

    # 司机端不应该收到推送
    with pytest.raises(Exception):
        driver.receive_json(timeout=1)
