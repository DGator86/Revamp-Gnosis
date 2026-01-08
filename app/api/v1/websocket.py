from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections for real-time streaming"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.symbol_subscribers: dict = {}
    
    async def connect(self, websocket: WebSocket, symbol: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if symbol not in self.symbol_subscribers:
            self.symbol_subscribers[symbol] = []
        self.symbol_subscribers[symbol].append(websocket)
        
        logger.info(f"Client connected for symbol {symbol}")
    
    def disconnect(self, websocket: WebSocket, symbol: str):
        self.active_connections.remove(websocket)
        if symbol in self.symbol_subscribers:
            self.symbol_subscribers[symbol].remove(websocket)
        
        logger.info(f"Client disconnected from symbol {symbol}")
    
    async def broadcast_to_symbol(self, symbol: str, message: dict):
        """Broadcast message to all subscribers of a symbol"""
        if symbol not in self.symbol_subscribers:
            return
        
        dead_connections = []
        for connection in self.symbol_subscribers[symbol]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for dead in dead_connections:
            if dead in self.symbol_subscribers[symbol]:
                self.symbol_subscribers[symbol].remove(dead)
            if dead in self.active_connections:
                self.active_connections.remove(dead)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific client"""
        await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/stream/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for real-time market data streaming
    
    Clients connect to this endpoint to receive real-time updates for a symbol:
    - Market bars (1-minute cadence)
    - Technical indicators
    - Collapse field analytics
    """
    await manager.connect(websocket, symbol)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connected",
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Connected to real-time stream for {symbol}"
        }, websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive messages from client (e.g., subscription updates)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Echo back for now (can implement command handling)
                await manager.send_personal_message({
                    "type": "ack",
                    "received": message,
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)
                
            except WebSocketDisconnect:
                manager.disconnect(websocket, symbol)
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        manager.disconnect(websocket, symbol)


async def broadcast_bar_update(symbol: str, bar_data: dict):
    """
    Helper function to broadcast bar updates to subscribers
    Called by the ingestion service when new bars arrive
    """
    message = {
        "type": "bar",
        "symbol": symbol,
        "timestamp": datetime.utcnow().isoformat(),
        "data": bar_data
    }
    await manager.broadcast_to_symbol(symbol, message)


async def broadcast_indicator_update(symbol: str, indicator_data: dict):
    """
    Helper function to broadcast indicator updates to subscribers
    Called by the analytics service when new indicators are computed
    """
    message = {
        "type": "indicator",
        "symbol": symbol,
        "timestamp": datetime.utcnow().isoformat(),
        "data": indicator_data
    }
    await manager.broadcast_to_symbol(symbol, message)


async def broadcast_collapse_field_update(symbol: str, collapse_data: dict):
    """
    Helper function to broadcast collapse field updates to subscribers
    Called by the analytics service when new analytics are computed
    """
    message = {
        "type": "collapse_field",
        "symbol": symbol,
        "timestamp": datetime.utcnow().isoformat(),
        "data": collapse_data
    }
    await manager.broadcast_to_symbol(symbol, message)
