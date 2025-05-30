from typing import Any, Dict, List

from app.api.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash
from app.exceptions import UserNotFoundError, UserAlreadyExistsError
from app.utils.unitofwork import UnitOfWork


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def find_all(self, skip: int = 0, limit: int | None = None) -> List[UserResponse]:
        async with self.uow:
            users = await self.uow.user.find_all(skip, limit)
            return [UserResponse.model_validate(user) for user in users]

    async def find_by_id(self, user_id: int) -> UserResponse:
        async with self.uow:
            user = await self.uow.user.find_one(id=user_id)
            if not user:
                raise UserNotFoundError(user_id)
            return UserResponse.model_validate(user)

    async def find_by_username(self, username: str) -> UserResponse:
        async with self.uow:
            user = await self.uow.user.find_one(username=username)
            if not user:
                raise UserNotFoundError(username)
            return UserResponse.model_validate(user)

    async def add(self, user: UserCreate) -> UserResponse:
        async with self.uow:
            if await self.uow.user.find_one(username=user.username):
                raise UserAlreadyExistsError(user.username)

            user_dict = self._get_db_user_dict(user)
            user_db = await self.uow.user.add(user_dict)
            user_response = UserResponse.model_validate(user_db)
            await self.uow.commit()
            return user_response

    @staticmethod
    def _get_db_user_dict(user: UserCreate) -> Dict[str, Any]:
        user_dict = user.model_dump()
        password = user_dict.pop("password")
        hashed_password = get_password_hash(password)
        user_dict["hashed_password"] = hashed_password
        return user_dict
