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

ws_manager = ConnectionManager()

# Import the CSV/Supabase manager from the local `core` package. Use a different
# name to avoid clobbering the websocket `ws_manager` above and to ensure the
# import works when running from the `backend/` folder (importing `backend.*`
# would fail when the current working directory is already `backend`).
import core.manager as csv_manager


@app.on_event("startup")
async def startup_event():
    try:
        csv_manager.start_csv_pusher(interval=5)
        print("CSV pusher started (interval=5s)")
    except Exception as e:
        print("Failed to start CSV pusher:", e)


@app.on_event("shutdown")
async def shutdown_event():
    try:
        csv_manager.stop_csv_pusher()
    except Exception:
        pass

@app.websocket("/ws/flight-data")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # pour garder la connexion
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.post("/push")
async def push(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "invalid json"}, status_code=400)

    # Broadcast to websocket clients
    asyncio.create_task(ws_manager.broadcast(payload))

    # Schedule ingestion (CSV + Supabase) in background thread to avoid blocking
    try:
        # Write payload to CSV in a thread to avoid blocking the event loop
        asyncio.create_task(asyncio.to_thread(csv_manager.process_payload, payload))
    except Exception as e:
        print("Failed to schedule ingestion:", e)

    return {"ok": True}