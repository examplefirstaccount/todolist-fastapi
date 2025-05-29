from typing import Dict, Optional

import jwt
from fastapi import Depends, HTTPException, WebSocket, WebSocketException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.security import get_password_hash, verify_password, create_jwt_token, decode_jwt_token
from app.utils.unitofwork import UnitOfWork

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def register(self, user: UserCreate) -> UserResponse:
        async with self.uow:
            if await self.uow.user.find_one(username=user.username):
                return None

            user_dict = user.model_dump()
            hashed_password = get_password_hash(user_dict.pop("password"))
            user_dict["hashed_password"] = hashed_password

            user_db = await self.uow.user.add(user_dict)
            user_response = UserResponse.model_validate(user_db)
            await self.uow.commit()

            return user_response

    async def login(self, user: UserLogin) -> Dict[str, str]:
        async with self.uow:
            user_db = await self.uow.user.find_one(username=user.username)
            if user_db and verify_password(user.password, user_db.hashed_password):
                token_data = {"sub": user.username}
                access_token = create_jwt_token(token_data)
                return {
                    "access_token": access_token,
                    "token_type": "bearer"
                }
            return None

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
        try:
            payload = decode_jwt_token(token)
            username: str = payload.get("sub")
            if not username:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"})
            return {"username": username}

            # Optional: Check if the user still exists in the database
            # user = db.query(User).filter(User.username == username).first()
            # if user is None:
            #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",
            #                         headers={"WWW-Authenticate": "Bearer"})

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired",
                                headers={"WWW-Authenticate": "Bearer"})
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token",
                                headers={"WWW-Authenticate": "Bearer"})

    @staticmethod
    async def authenticate_websocket(websocket: WebSocket, token: Optional[str] = None):
        """Authenticate WebSocket connection using JWT."""
        token = token or websocket.query_params.get("token")
        if token is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized")

        try:
            payload = decode_jwt_token(token)
            username: str = payload.get("sub")
            if not username:
                raise ValueError("Missing 'sub' in token payload")
            return username
        except (jwt.ExpiredSignatureError, jwt.PyJWTError, ValueError) as e:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=str(e))
