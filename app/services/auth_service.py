from typing import Dict

from app.api.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.security import get_password_hash, verify_password, create_jwt_token
from app.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.utils.unitofwork import UnitOfWork


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def register(self, user: UserCreate) -> UserResponse:
        async with self.uow:
            if await self.uow.user.find_one(username=user.username):
                raise UserAlreadyExistsError(user.username)

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
            if not user_db or not verify_password(user.password, user_db.hashed_password):
                raise InvalidCredentialsError()

            return {
                "access_token": create_jwt_token({"sub": user.username}),
                "token_type": "bearer"
            }
