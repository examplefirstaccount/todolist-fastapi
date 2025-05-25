from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Security

from app.api.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.core.dependencies import get_task_repository
from app.core.security import verify_jwt_token
from app.db.repositories.task_repository import TaskRepository

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Security(verify_jwt_token)]
)

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse,
    summary="Create a new task",
    description="Creates a new task with the provided details."
)
async def create_task(
        task: TaskCreate,
        task_repo: TaskRepository = Depends(get_task_repository)
):
    db_task = await task_repo.create_task(task)
    return db_task


@router.get(
    "/",
    response_model=List[TaskResponse],
    summary="Get all tasks",
    description="Retrieves a list of all tasks with optional pagination."
)
async def read_tasks(
        skip: int = 0,
        limit: int = 100,
        task_repo: TaskRepository = Depends(get_task_repository)
):
    tasks = await task_repo.get_tasks(skip=skip, limit=limit)
    return tasks


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID",
    description="Retrieves a single task by its unique ID."
)
async def read_task(
        task_id: int,
        task_repo: TaskRepository = Depends(get_task_repository)
):
    task = await task_repo.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
    description="Updates an existing task identified by its ID."
)
async def update_task(
        task_id: int,
        task: TaskUpdate,
        task_repo: TaskRepository = Depends(get_task_repository)
):
    update_task = await task_repo.update_task(task_id, task)
    if not update_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return update_task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Deletes a task identified by its ID."
)
async def delete_task(
        task_id: int,
        task_repo: TaskRepository = Depends(get_task_repository)
):
    deleted = await task_repo.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return None
