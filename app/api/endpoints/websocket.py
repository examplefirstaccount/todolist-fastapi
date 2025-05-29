from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, WebSocketException

from app.api.dependencies.dependencies import get_connection_manager
from app.core.security import authenticate_websocket
from app.core.websockets import ConnectionManager


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
    try:
        username = await authenticate_websocket(websocket)
        await manager.connect(websocket, username)

        while True:
            data = await websocket.receive_text()
            print(f"[WebSocket] Received from {username}: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, username)
        print(f"[WebSocket] Client {username} disconnected")

    except WebSocketException as e:
        print(f"[WebSocket] Authentication failed: {e}")

    except Exception as e:
        manager.disconnect(websocket, username)
        print(f"[WebSocket] Unexpected error: {e}")
