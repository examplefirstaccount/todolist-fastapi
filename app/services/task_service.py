from typing import List

from app.api.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.exceptions import ProjectNotFoundError, PermissionDeniedError, TaskNotFoundError
from app.utils.unitofwork import UnitOfWork


class TaskService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_task(self, user_id: int, task: TaskCreate) -> TaskResponse:
        async with self.uow:
            task_data = task.model_dump()

            if task.project_id is not None:
                project = await self.uow.project.find_one(id=task.project_id)
                if not project:
                    raise ProjectNotFoundError(task.project_id)
                if project.owner_id != user_id:
                    raise PermissionDeniedError("You do not own this project.")

            task_data["user_id"] = user_id

            task_db = await self.uow.task.add(task_data)
            task_response = TaskResponse.model_validate(task_db)
            await self.uow.commit()

            return task_response

    async def get_tasks(self, user_id: int, skip: int = 0, limit: int | None = None) -> List[TaskResponse]:
        async with self.uow:
            tasks = await self.uow.task.find_all(skip, limit, user_id=user_id)
            return [TaskResponse.model_validate(task) for task in tasks]

    async def get_task(self, user_id: int, task_id: int) -> TaskResponse:
        async with self.uow:
            task = await self.uow.task.find_one(id=task_id)
            if not task:
                raise TaskNotFoundError(task_id)
            if task.user_id != user_id:
                raise PermissionDeniedError("You do not own this task.")
            return TaskResponse.model_validate(task)

    async def update_task(self, user_id: int, task_id: int, task: TaskUpdate) -> TaskResponse:
        async with self.uow:
            task_db = await self.uow.task.find_one(id=task_id)
            if not task_db:
                raise TaskNotFoundError(task_id)
            if task_db.user_id != user_id:
                raise PermissionDeniedError("You do not own this task.")

            update_data = task.model_dump(exclude_unset=True)

            if task.project_id is not None:
                project = await self.uow.project.find_one(id=task.project_id)
                if not project:
                    raise ProjectNotFoundError(task.project_id)
                if project.owner_id != user_id:
                    raise PermissionDeniedError("You do not own this project.")

            task_updated = await self.uow.task.update(update_data, id=task_id)
            if not task_updated:
                raise TaskNotFoundError(task_id)
            task_response = TaskResponse.model_validate(task_updated)
            await self.uow.commit()

            return task_response

    async def delete_task(self, user_id: int, task_id: int) -> None:
        async with self.uow:
            task = await self.uow.task.find_one(id=task_id)
            if not task:
                raise TaskNotFoundError(task_id)
            if task.user_id != user_id:
                raise PermissionDeniedError("You do not own this task.")

            deleted = await self.uow.task.delete(id=task_id)
            if not deleted:
                raise TaskNotFoundError(task_id)
            await self.uow.commit()
