import pytest

from app.api.schemas.task import TaskCreate, TaskUpdate
from app.exceptions import (ProjectNotFoundError,
                            PermissionDeniedError,
                            TaskNotFoundError)


@pytest.mark.asyncio
async def test_create_task_success(task_service, test_user, uow_test):
    # Test basic task creation
    task_data = TaskCreate(
        title="Test task",
        description="Do something important",
        project_id=None
    )

    created_task = await task_service.create_task(test_user.id, task_data)

    assert created_task.title == "Test task"
    assert created_task.user_id == test_user.id

    # Verify DB state
    async with uow_test:
        db_task = await uow_test.task.find_one(id=created_task.id)
        assert db_task is not None
        assert db_task.user_id == test_user.id


@pytest.mark.asyncio
async def test_create_task_with_project(task_service, test_user, test_project, uow_test):
    # Test task creation with valid project
    task_data = TaskCreate(
        title="Project task",
        description="Project-related work",
        project_id=test_project.id
    )

    created_task = await task_service.create_task(test_user.id, task_data)
    assert created_task.project_id == test_project.id


@pytest.mark.asyncio
async def test_create_task_with_nonexistent_project(task_service, test_user):
    # Test invalid project reference
    task_data = TaskCreate(
        title="Invalid project",
        description="Should fail",
        project_id=99999  # Non-existent
    )

    with pytest.raises(ProjectNotFoundError):
        await task_service.create_task(test_user.id, task_data)


@pytest.mark.asyncio
async def test_create_task_with_unauthorized_project(task_service, test_user, other_users_project):
    # Test project ownership validation
    task_data = TaskCreate(
        title="Unauthorized",
        description="Should fail",
        project_id=other_users_project.id
    )

    with pytest.raises(PermissionDeniedError):
        await task_service.create_task(test_user.id, task_data)


@pytest.mark.asyncio
async def test_get_tasks(task_service, test_user, test_tasks):
    # Test task listing
    tasks = await task_service.get_tasks(test_user.id)

    assert len(tasks) == len(test_tasks)
    assert all(task.user_id == test_user.id for task in tasks)


@pytest.mark.asyncio
async def test_get_tasks_pagination(task_service, test_user, multiple_test_tasks):
    # Test pagination
    page1 = await task_service.get_tasks(test_user.id, skip=0, limit=5)
    page2 = await task_service.get_tasks(test_user.id, skip=5, limit=5)

    assert len(page1) == 5
    assert len(page2) == 5
    assert {t.id for t in page1}.isdisjoint({t.id for t in page2})


@pytest.mark.asyncio
async def test_get_task_success(task_service, test_user, test_task):
    # Test successful task retrieval
    task = await task_service.get_task(test_user.id, test_task.id)
    assert task.id == test_task.id


@pytest.mark.asyncio
async def test_get_task_not_found(task_service, test_user):
    # Test non-existent task
    with pytest.raises(TaskNotFoundError):
        await task_service.get_task(test_user.id, 99999)


@pytest.mark.asyncio
async def test_get_task_unauthorized(task_service, other_user, test_task):
    # Test permission check
    with pytest.raises(PermissionDeniedError):
        await task_service.get_task(other_user.id, test_task.id)


@pytest.mark.asyncio
async def test_update_task_success(task_service, test_user, test_task):
    # Test successful update
    update_data = TaskUpdate(
        title="Updated title",
        description="New description"
    )

    updated_task = await task_service.update_task(test_user.id, test_task.id, update_data)

    assert updated_task.title == "Updated title"
    assert updated_task.description == "New description"


@pytest.mark.asyncio
async def test_update_task_change_project(task_service, test_user, test_task, test_project):
    # Test project reassignment
    data = {"project_id": test_project.id}
    update_data = TaskUpdate(**data)
    updated_task = await task_service.update_task(test_user.id, test_task.id, update_data)
    assert updated_task.project_id == test_project.id


@pytest.mark.asyncio
async def test_update_task_to_invalid_project(task_service, test_user, test_task):
    # Test invalid project update
    data = {"project_id": 99999}
    update_data = TaskUpdate(**data)
    with pytest.raises(ProjectNotFoundError):
        await task_service.update_task(test_user.id, test_task.id, update_data)


@pytest.mark.asyncio
async def test_update_task_unauthorized_project(task_service, test_user, test_task, other_users_project):
    # Test unauthorized project update
    data = {"project_id": other_users_project.id}
    update_data = TaskUpdate(**data)
    with pytest.raises(PermissionDeniedError):
        await task_service.update_task(test_user.id, test_task.id, update_data)


@pytest.mark.asyncio
async def test_delete_task_success(task_service, test_user, test_task, uow_test):
    # Test successful deletion
    task_id = test_task.id
    await task_service.delete_task(test_user.id, task_id)

    # Verify deletion
    async with uow_test:
        assert await uow_test.task.find_one(id=task_id) is None


@pytest.mark.asyncio
async def test_delete_task_not_found(task_service, test_user):
    # Test non-existent task deletion
    with pytest.raises(TaskNotFoundError):
        await task_service.delete_task(test_user.id, 99999)


@pytest.mark.asyncio
async def test_delete_task_unauthorized(task_service, other_user, test_task):
    # Test permission check
    with pytest.raises(PermissionDeniedError):
        await task_service.delete_task(other_user.id, test_task.id)
