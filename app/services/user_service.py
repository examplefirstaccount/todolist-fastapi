from typing import Any, Dict, List, Optional

from app.api.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash
from app.utils.unitofwork import UnitOfWork


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def find_all(self, skip: int = 0, limit: int | None = None) -> List[UserResponse]:
        async with self.uow:
            users = await self.uow.user.find_all(skip, limit)
            return [UserResponse.model_validate(user) for user in users]

    async def find_by_id(self, user_id: int) -> Optional[UserResponse]:
        async with self.uow:
            user = await self.uow.user.find_one(id=user_id)
            if user:
                return UserResponse.model_validate(user)
            return None

    async def find_by_username(self, username: str) -> Optional[UserResponse]:
        async with self.uow:
            user = await self.uow.user.find_one(username=username)
            if user:
                return UserResponse.model_validate(user)
            return None

    async def add(self, user: UserCreate) -> Optional[UserResponse]:
        if not await self.find_by_username(user.username):
            async with self.uow:
                user_dict = self._get_db_user_dict(user)
                user_db = await self.uow.user.add(user_dict)
                user_response = UserResponse.model_validate(user_db)

                await self.uow.commit()

                return user_response
        return None

    @staticmethod
    def _get_db_user_dict(user: UserCreate) -> Dict[str, Any]:
        user_dict = user.model_dump()
        password = user_dict.pop("password")
        hashed_password = get_password_hash(password)
        user_dict["hashed_password"] = hashed_password
        return user_dict
