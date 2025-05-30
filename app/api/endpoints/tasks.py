from typing import List

from fastapi import APIRouter, Depends, status, Security

from app.api.dependencies.dependencies import (
    get_task_service,
    get_user_service,
    get_current_username_http,
    get_connection_manager,
    TaskService,
    UserService
)
from app.api.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.core.websockets import ConnectionManager

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Security(get_current_username_http)]
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
        username: str = Depends(get_current_username_http),
        task_service: TaskService = Depends(get_task_service),
        user_service: UserService = Depends(get_user_service),
        manager: ConnectionManager = Depends(get_connection_manager)
):
    user = await user_service.get_user_by_username(username)
    task_response = await task_service.create_task(user.id, task)

    message = manager.prepare_message("task_created", task_response)
    await manager.broadcast(message)

    return task_response


@router.get(
    "/",
    response_model=List[TaskResponse],
    summary="Get all tasks",
    description="Retrieves a list of all tasks with optional pagination."
)
async def read_tasks(
        skip: int = 0,
        limit: int = 100,
        username: str = Depends(get_current_username_http),
        task_service: TaskService = Depends(get_task_service),
        user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_by_username(username)
    tasks = await task_service.get_tasks(user.id, skip=skip, limit=limit)
    return tasks


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID",
    description="Retrieves a single task by its unique ID."
)
async def read_task(
        task_id: int,
        username: str = Depends(get_current_username_http),
        task_service: TaskService = Depends(get_task_service),
        user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_by_username(username)
    task = await task_service.get_task(user.id, task_id)
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
        username: str = Depends(get_current_username_http),
        task_service: TaskService = Depends(get_task_service),
        user_service: UserService = Depends(get_user_service),
        manager: ConnectionManager = Depends(get_connection_manager)
):
    user = await user_service.get_user_by_username(username)
    task_response = await task_service.update_task(user.id, task_id, task)

    message = manager.prepare_message("task_updated", task_response)
    await manager.broadcast(message)

    return task_response


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Deletes a task identified by its ID."
)
async def delete_task(
        task_id: int,
        username: str = Depends(get_current_username_http),
        task_service: TaskService = Depends(get_task_service),
        user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_by_username(username)
    await task_service.delete_task(user.id, task_id)
    return None
