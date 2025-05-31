from typing import List

from fastapi import APIRouter, Depends, status, Security, Query

from app.api.dependencies.dependencies import (
    get_project_service,
    get_user_service,
    get_current_username_http,
    get_connection_manager,
    ProjectService,
    UserService
)
from app.api.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.api.schemas.task import TaskResponse, PriorityLevel
from app.core.websockets import ConnectionManager

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Security(get_current_username_http)]
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectResponse,
    summary="Create a new project",
    description="Creates a new project with the provided details."
)
async def create_project(
        project: ProjectCreate,
        username: str = Depends(get_current_username_http),
        project_service: ProjectService = Depends(get_project_service),
        user_service: UserService = Depends(get_user_service),
        manager: ConnectionManager = Depends(get_connection_manager)
):
    user = await user_service.get_user_by_username(username)
    project_response = await project_service.create_project(user.id, project)

    message = manager.prepare_message("project_created", project_response)
    await manager.broadcast(message)

    return project_response


@router.get(
    "/",
    response_model=List[ProjectResponse],
    summary="Get all projects",
    description="Retrieves a list of all projects with optional pagination."
)
async def read_projects(
        skip: int = 0,
        limit: int = 100,
        username: str = Depends(get_current_username_http),
        project_service: ProjectService = Depends(get_project_service),
        user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_by_username(username)
    projects = await project_service.get_projects(user.id, skip=skip, limit=limit)
    return projects


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
    description="Retrieves a single project by its unique ID."
)
async def read_project(
        project_id: int,
        username: str = Depends(get_current_username_http),
        project_service: ProjectService = Depends(get_project_service),
        user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_by_username(username)
    project = await project_service.get_project(user.id, project_id)
    return project


@router.get(
    "/{project_id}/tasks",
    response_model=List[TaskResponse],
    summary="Get tasks for a project",
    description="Retrieves tasks for a project."
)
async def get_tasks(
        project_id: int,
        completed: bool | None = Query(None),
        priority: PriorityLevel | None = Query(None),
        sort_by: str = Query("created_at"),
        sort_order: str = Query("desc"),
        skip: int = 0,
        limit: int | None = None,
        username: str = Depends(get_current_username_http),
        project_service: ProjectService = Depends(get_project_service),
        user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_by_username(username)
    tasks = await project_service.get_project_tasks(
        user_id=user.id,
        project_id=project_id,
        completed=completed,
        priority=priority,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    return tasks


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Updates an existing project identified by its ID."
)
async def update_project(
        project_id: int,
        project: ProjectUpdate,
        username: str = Depends(get_current_username_http),
        project_service: ProjectService = Depends(get_project_service),
        user_service: UserService = Depends(get_user_service),
        manager: ConnectionManager = Depends(get_connection_manager)
):
    user = await user_service.get_user_by_username(username)
    project_response = await project_service.update_project(user.id, project_id, project)

    message = manager.prepare_message("project_updated", project_response)
    await manager.broadcast(message)

    return project_response


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Deletes a project identified by its ID."
)
async def delete_project(
        project_id: int,
        username: str = Depends(get_current_username_http),
        project_service: ProjectService = Depends(get_project_service),
        user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_by_username(username)
    await project_service.delete_project(user.id, project_id)
    return None
