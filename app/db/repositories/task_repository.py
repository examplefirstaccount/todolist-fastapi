from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task as DBTask
from app.api.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    """
    Repository class for Task database operations.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task_data: TaskCreate) -> DBTask:
        """Creates a new task in the database."""
        db_task = DBTask(**task_data.model_dump())
        self.session.add(db_task)
        await self.session.commit()
        await self.session.refresh(db_task)
        return db_task

    async def get_tasks(self, skip: int = 0, limit: int = 100) -> List[DBTask]:
        """Retrieves a list of tasks with pagination."""
        stmt = select(DBTask).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_task_by_id(self, task_id: int) -> Optional[DBTask]:
        """Retrieves a single task by its ID."""
        stmt = select(DBTask).where(DBTask.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[DBTask]:
        """Updates an existing task by its ID."""

        # Retrieve the task first
        db_task = await self.get_task_by_id(task_id)
        if not db_task:
            return None

        # Apply updates from the schema
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        await self.session.commit()
        await self.session.refresh(db_task)
        return db_task

    async def delete_task(self, task_id: int) -> bool:
        """Deletes a task by its ID."""
        stmt = delete(DBTask).where(DBTask.id == task_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
