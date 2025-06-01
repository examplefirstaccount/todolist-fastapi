import logging
from typing import Optional

from fastapi import Depends, HTTPException, WebSocket, WebSocketException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import verify_jwt_token
from app.core.websockets import ConnectionManager
from app.exceptions import TokenError
from app.services import AuthService, TaskService, ProjectService, UserService
from app.utils.unitofwork import UnitOfWork

logger = logging.getLogger("app")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
connection_manager = ConnectionManager()


async def get_uow() -> UnitOfWork:
    """Dependency that provides a UnitOfWork instance."""
    return UnitOfWork()


async def get_auth_service(uow: UnitOfWork = Depends(get_uow)) -> AuthService:
    """Dependency that provides a AuthService instance."""
    return AuthService(uow)


async def get_task_service(uow: UnitOfWork = Depends(get_uow)) -> TaskService:
    """Dependency that provides a TaskService instance."""
    return TaskService(uow)


async def get_user_service(uow: UnitOfWork = Depends(get_uow)) -> UserService:
    """Dependency that provides a UserService instance."""
    return UserService(uow)


async def get_project_service(uow: UnitOfWork = Depends(get_uow)) -> ProjectService:
    """Dependency that provides a ProjectService instance."""
    return ProjectService(uow)


async def get_current_username_http(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = verify_jwt_token(token)
        username = payload["sub"]
        return username
    except TokenError as e:
        logger.warning(f"[HTTP] TokenError: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_username_websocket(websocket: WebSocket, token: Optional[str] = None) -> str:
    try:
        token = websocket.query_params.get("token") or token
        payload = verify_jwt_token(token)
        username = payload["sub"]
        return username
    except TokenError as e:
        logger.warning(f"[WebSocket] TokenError: {e.message}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=e.message)


def get_connection_manager() -> ConnectionManager:
    """Dependency to get the singleton ConnectionManager instance."""
    return connection_manager
