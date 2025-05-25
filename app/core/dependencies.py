from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.database import get_db
from app.db.repositories.task_repository import TaskRepository
from app.db.repositories.user_repository import UserRepository


async def get_task_repository(session: AsyncSession = Depends(get_db)) -> TaskRepository:
    """Dependency that provides a TaskRepository instance."""
    return TaskRepository(session=session)


async def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    """Dependency that provides a UserRepository instance."""
    return UserRepository(session=session)
