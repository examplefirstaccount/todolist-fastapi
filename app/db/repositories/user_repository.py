from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User as DBUser
from app.api.schemas.user import UserCreate


class UserRepository:
    """
    Repository class for Task database operations.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: UserCreate) -> DBUser:
        """Creates a new user in the database."""
        db_user = DBUser(
            username=user_data.username,
            hashed_password=user_data.password
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def get_user_by_username(self, username: str) -> Optional[DBUser]:
        """Retrieves a single user by its username."""
        stmt = select(DBUser).where(DBUser.username == username)
        result = await self.session.execute(stmt)
        return result.scalars().first()
