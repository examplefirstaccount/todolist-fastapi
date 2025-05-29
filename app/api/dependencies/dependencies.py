from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.websockets import ConnectionManager
from app.db.database import get_db
from app.repositories import TaskRepository
from app.repositories import UserRepository


async def get_task_repository(session: AsyncSession = Depends(get_db)) -> TaskRepository:
    """Dependency that provides a TaskRepository instance."""
    return TaskRepository(session=session)


async def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    """Dependency that provides a UserRepository instance."""
    return UserRepository(session=session)


connection_manager = ConnectionManager()
def get_connection_manager() -> ConnectionManager:
    """Dependency to get the singleton ConnectionManager instance."""
    return connection_manager
