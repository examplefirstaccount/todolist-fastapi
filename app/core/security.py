from datetime import datetime, timedelta, UTC
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status, WebSocket, WebSocketException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.core.config import settings
from app.db.models import User as DBUser
from app.db.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(user_repo: UserRepository, username: str, password: str) -> Optional[DBUser]:
    """
    Authenticates a user against the database.

    Args:
        user_repo: The user repository.
        username: The username to authenticate.
        password: The plain password provided by the user.

    Returns:
        The database User object if authentication is successful, None otherwise.
    """
    db_user = await user_repo.get_user_by_username(username)
    if db_user and pwd_context.verify(password, db_user.hashed_password):
        return db_user
    return None


def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",
                                headers={"WWW-Authenticate": "Bearer"})

        # Optional: Check if the user still exists in the database
        # user = db.query(User).filter(User.username == username).first()
        # if user is None:
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",
        #                         headers={"WWW-Authenticate": "Bearer"})

        return {"username": username}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired",
                            headers={"WWW-Authenticate": "Bearer"})
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token",
                            headers={"WWW-Authenticate": "Bearer"})


async def authenticate_websocket(websocket: WebSocket, token: Optional[str] = None):
    """Authenticate WebSocket connection using JWT."""
    token = token or websocket.query_params.get("token")
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise ValueError("Missing 'sub' in token payload")
        return username
    except (jwt.ExpiredSignatureError, jwt.PyJWTError, ValueError) as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=str(e))
