"""WebSocket 路由"""

from fastapi import APIRouter, WebSocket
from websocket.manager import connect, disconnect

ws_router = APIRouter()


@ws_router.websocket("/platform")
async def platform_websocket(websocket: WebSocket):
    """平台端连接"""
    await connect(websocket, "platform")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from platform: {data}")
    except Exception:
        disconnect(websocket)


@ws_router.websocket("/client")
async def client_websocket(websocket: WebSocket):
    """客户端连接"""
    await connect(websocket, "client")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from client: {data}")
    except Exception:
        disconnect(websocket)


@ws_router.websocket("/driver")
async def driver_websocket(websocket: WebSocket):
    """司机端连接"""
    await connect(websocket, "driver")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from driver: {data}")
    except Exception:
        disconnect(websocket)
