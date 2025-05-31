import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.api.dependencies.dependencies import get_connection_manager, get_current_username_websocket
from app.core.websockets import ConnectionManager

logger = logging.getLogger("app")

router = APIRouter()

@router.websocket("/ws/tasks")
async def websocket_endpoint(
    websocket: WebSocket,
    manager: ConnectionManager = Depends(get_connection_manager)
):
    """
    WebSocket endpoint for task updates.
    Clients must provide a valid JWT token as a query parameter.
    """
    username = await get_current_username_websocket(websocket)

    try:
        await manager.connect(websocket, username)

        while True:
            data = await websocket.receive_text()
            logger.debug(f"[WebSocket] Received from {username}: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, username)

    except Exception as e:
        manager.disconnect(websocket, username)
        logger.exception(f"[WebSocket] Unexpected error from {username}: {e}")
