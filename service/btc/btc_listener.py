import websocket
import json
import threading
import asyncio
from ..connection_manager import ConnectionManager

manager = None  # Will be set from main.py

def blockchain_ws_listener(address: str):
    """Listens to Blockchain.info WebSocket for a specific address."""
    def on_open(ws):
        print(f"✅ Subscribed to BTC address: {address}")
        ws.send(json.dumps({"op": "addr_sub", "addr": address}))

    def on_message(ws, message):
        print(f"📢 New TX for {address}")
        asyncio.run(manager.broadcast(address, message))

    ws = websocket.WebSocketApp(
        "wss://ws.blockchain.info/inv",
        on_open=on_open,
        on_message=on_message
    )
    ws.run_forever()

def start_listener(address: str):
    thread = threading.Thread(target=blockchain_ws_listener, args=(address,), daemon=True)
    thread.start()
