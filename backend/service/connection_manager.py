from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, address: str, websocket: WebSocket):
        await websocket.accept()
        if address not in self.active_connections:
            self.active_connections[address] = []
        self.active_connections[address].append(websocket)

    def disconnect(self, address: str, websocket: WebSocket):
        if address in self.active_connections:
            self.active_connections[address].remove(websocket)
            if not self.active_connections[address]:
                del self.active_connections[address]

    async def broadcast(self, address: str, message: str):
        if address in self.active_connections:
            for connection in self.active_connections[address]:
                await connection.send_text(message)
