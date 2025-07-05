"""管理连接池 + 推送逻辑"""

from typing import List, Dict
from fastapi import WebSocket

# 存储所有活跃的 WebSocket 连接
connected_clients: Dict[str, List[WebSocket]] = {
    "platform": [],  # 平台端连接
    "client": [],  # 客户端连接
    "driver": [],  # 司机端连接
}


async def connect(websocket: WebSocket, client_type: str):
    """新客户端连接时加入对应类型的连接池"""
    await websocket.accept()
    if client_type in connected_clients:
        connected_clients[client_type].append(websocket)


def disconnect(websocket: WebSocket):
    """客户端断开连接时从所有类型中移除"""
    for client_list in connected_clients.values():
        if websocket in client_list:
            client_list.remove(websocket)


async def send_message_to_type(client_type: str, message: dict):
    """向特定类型的所有客户端发送消息"""
    if client_type not in connected_clients:
        return

    for client in connected_clients[client_type]:
        try:
            await client.send_json(message)
        except Exception as e:
            print(f"Error sending message to {client_type} client: {e}")
            await client.close()
            disconnect(client)


async def send_message_to_all_except_sender(sender_type: str, message: dict):
    """向除发送者类型外的所有客户端发送消息"""
    for client_type, clients in connected_clients.items():
        if client_type == sender_type:
            continue
        for client in clients:
            try:
                await client.send_json(message)
            except Exception as e:
                print(f"Error sending message to {client_type} client: {e}")
                await client.close()
                disconnect(client)
