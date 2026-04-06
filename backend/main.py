from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        to_remove = []
        for connection in list(self.active_connections):
            try:
                await connection.send_text(data)
            except Exception:
                to_remove.append(connection)
        for c in to_remove:
            self.disconnect(c)

manager = ConnectionManager()

@app.websocket("/ws/flight-data")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # pour garder la connexion
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/push")
async def push(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "invalid json"}, status_code=400)

    asyncio.create_task(manager.broadcast(payload))
    return {"ok": True}