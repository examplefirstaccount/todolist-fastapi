import logging
import json
from typing import Dict, List, Any

from fastapi import WebSocket
from pydantic import BaseModel

logger = logging.getLogger("app")


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasting messages.
    """
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, username: str):
        """Accept and add a new WebSocket connection."""
        await websocket.accept()
        if username not in self.active_connections:
            self.active_connections[username] = []
        self.active_connections[username].append(websocket)
        logger.info(
            "WebSocket connected",
            extra={"username": username, "total_connections": len(self.active_connections[username])}
        )

    def disconnect(self, websocket: WebSocket, username: str):
        """Remove a disconnected WebSocket connection."""
        connections = self.active_connections.get(username)
        if connections and websocket in connections:
            connections.remove(websocket)
            logger.info(
                "WebSocket disconnected",
                extra={"username": username, "remaining_connections": len(connections)}
            )
            if not connections:
                del self.active_connections[username]
                logger.info("No active connections for user", extra={"username": username})

    async def send_personal_message(self, message: Dict[str, Any], username: str):
        """Send a personal message."""
        if username in self.active_connections:
            message_json = json.dumps(message)
            for ws in self.active_connections[username]:
                await ws.send_text(message_json)
            logger.debug("Sent personal message", extra={"username": username, "message": message})

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all active connections."""
        message_json = json.dumps(message)
        for user_sockets in self.active_connections.values():
            for ws in user_sockets:
                await ws.send_text(message_json)
        logger.debug("Broadcasted message", extra={"message": message})

    @staticmethod
    def prepare_message(event_type: str, data: BaseModel) -> Dict[str, Any]:
        """Prepare a message suitable for broadcasting."""
        return {
            "event": event_type,
            "data": data.model_dump(mode="json")
        }
