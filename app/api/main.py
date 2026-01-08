from fastapi import FastAPI, WebSocket, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
import asyncio
from app.config import settings
from app.storage.db import get_session, init_db
from app.storage.models import MarketState
from app.worker import run_worker_loop

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/ui"), name="static")

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def on_startup():
    await init_db()
    asyncio.create_task(run_worker_loop(manager))

@app.get("/")
async def get_dashboard():
    with open("app/ui/dashboard.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws/state/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await manager.connect(websocket)
    try:
        while True: await websocket.receive_text()
    except:
        manager.disconnect(websocket)