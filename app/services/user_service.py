from typing import List

from app.api.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash
from app.exceptions import UserNotFoundError, UserAlreadyExistsError
from app.utils.unitofwork import UnitOfWork


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_user(self, user: UserCreate) -> UserResponse:
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

    async def get_users(self, skip: int = 0, limit: int | None = None) -> List[UserResponse]:
        async with self.uow:
            users = await self.uow.user.find_all(skip, limit)
            return [UserResponse.model_validate(user) for user in users]

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        async with self.uow:
            user = await self.uow.user.find_one(id=user_id)
            if not user:
                raise UserNotFoundError(user_id)
            return UserResponse.model_validate(user)

    async def get_user_by_username(self, username: str) -> UserResponse:
        async with self.uow:
            user = await self.uow.user.find_one(username=username)
            if not user:
                raise UserNotFoundError(username)
            return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> None:
        async with self.uow:
            user = await self.uow.user.find_one(id=user_id)
            if not user:
                raise UserNotFoundError(user_id)

            deleted = await self.uow.user.delete(id=user_id)
            if not deleted:
                raise UserNotFoundError(user_id)
            await self.uow.commit()
