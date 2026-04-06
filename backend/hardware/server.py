"""
Script futur pour acquérir des données des vrais capteurs
"""
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import json

app = FastAPI()

# Liste des clients connectés
connected_clients: list[WebSocket] = []

@app.websocket("/ws/flight-data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        connected_clients.remove(websocket)

import random

async def fake_flight_data():
    t = 0
    while True:
        data = {
            "timestamp": t,
            "altitude": random.uniform(0, 100),
            "speed": random.uniform(0, 50),
            "az": random.uniform(-5, 5),
            "roll": random.uniform(-30, 30),
            "pitch": random.uniform(-30, 30),
            "yaw": random.uniform(0, 360),
        }

        await broadcast_flight_data(data)

        t += 1
        await asyncio.sleep(1)


# Fonction pour broadcaster les données du simulateur
async def broadcast_flight_data(data: dict):
    for client in connected_clients:
        try:
            await client.send_json(data)
        except:
            pass


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fake_flight_data())


# Modify simulator.py to call this
# async_broadcast_flight_data(data_supabase)

# Pour lancer : uvicorn main:app --host 0.0.0.0 --port 8000