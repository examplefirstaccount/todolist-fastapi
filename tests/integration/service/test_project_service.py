import pytest

from app.api.schemas.project import ProjectCreate, ProjectUpdate
from app.api.schemas.task import PriorityLevel
from app.exceptions import ProjectNotFoundError, PermissionDeniedError


@pytest.mark.asyncio
async def test_create_project_success(project_service, test_user):
    # Test basic project creation
    project_data = ProjectCreate(name="Test Project")

    created_project = await project_service.create_project(test_user.id, project_data)

    assert created_project.name == "Test Project"
    assert created_project.owner_id == test_user.id


@pytest.mark.asyncio
async def test_get_projects(project_service, test_user, test_projects):
    # Test project listing
    projects = await project_service.get_projects(test_user.id)

    assert len(projects) == len(test_projects)
    assert all(p.owner_id == test_user.id for p in projects)


@pytest.mark.asyncio
async def test_get_projects_pagination(project_service, test_user, multiple_test_projects):
    # Test pagination
    page1 = await project_service.get_projects(test_user.id, skip=0, limit=5)
    page2 = await project_service.get_projects(test_user.id, skip=5, limit=5)

    assert len(page1) == 5
    assert len(page2) == 5
    assert {p.id for p in page1}.isdisjoint({p.id for p in page2})


@pytest.mark.asyncio
async def test_get_project_success(project_service, test_user, test_project):
    # Test successful project retrieval
    project = await project_service.get_project(test_user.id, test_project.id)
    assert project.id == test_project.id


@pytest.mark.asyncio
async def test_get_project_not_found(project_service, test_user):
    # Test non-existent project
    with pytest.raises(ProjectNotFoundError):
        await project_service.get_project(test_user.id, 99999)


@pytest.mark.asyncio
async def test_get_project_unauthorized(project_service, other_user, test_project):
    # Test permission check
    with pytest.raises(PermissionDeniedError):
        await project_service.get_project(other_user.id, test_project.id)


@pytest.mark.asyncio
async def test_get_project_tasks(project_service, test_user, test_project_with_tasks):
    # Test task listing for project
    tasks = await project_service.get_project_tasks(test_user.id, test_project_with_tasks.id)
    assert len(tasks) == 3  # Based on test_project_with_tasks fixture


@pytest.mark.asyncio
async def test_get_project_tasks_filtering(project_service, test_user, test_project_with_mixed_tasks):
    # Test completed filter
    completed_tasks = await project_service.get_project_tasks(
        test_user.id,
        test_project_with_mixed_tasks.id,
        completed=True
    )
    assert all(t.is_completed for t in completed_tasks)

    # Test priority filter
    high_priority_tasks = await project_service.get_project_tasks(
        test_user.id,
        test_project_with_mixed_tasks.id,
        priority=PriorityLevel.high
    )
    assert all(t.priority == PriorityLevel.high for t in high_priority_tasks)


@pytest.mark.asyncio
async def test_get_project_tasks_sorting(project_service, test_user, test_project_with_mixed_tasks):
    # Test created_at sorting
    tasks_desc = await project_service.get_project_tasks(
        test_user.id,
        test_project_with_mixed_tasks.id,
        sort_by="created_at",
        sort_order="desc"
    )
    assert tasks_desc[0].created_at > tasks_desc[-1].created_at

    tasks_asc = await project_service.get_project_tasks(
        test_user.id,
        test_project_with_mixed_tasks.id,
        sort_by="created_at",
        sort_order="asc"
    )
    assert tasks_asc[0].created_at < tasks_asc[-1].created_at

    # Test priority sorting
    priority_tasks = await project_service.get_project_tasks(
        test_user.id,
        test_project_with_mixed_tasks.id,
        sort_by="priority"
    )
    assert priority_tasks[0].priority.value >= priority_tasks[-1].priority.value


@pytest.mark.asyncio
async def test_update_project_success(project_service, test_user, test_project):
    # Test successful update
    update_data = ProjectUpdate(name="Updated Name")
    updated_project = await project_service.update_project(test_user.id, test_project.id, update_data)
    assert updated_project.name == "Updated Name"


@pytest.mark.asyncio
async def test_update_project_not_found(project_service, test_user):
    # Test non-existent project update
    update_data = ProjectUpdate(name="Should Fail")
    with pytest.raises(ProjectNotFoundError):
        await project_service.update_project(test_user.id, 99999, update_data)


@pytest.mark.asyncio
async def test_update_project_unauthorized(project_service, other_user, test_project):
    # Test permission check
    update_data = ProjectUpdate(name="Unauthorized Update")
    with pytest.raises(PermissionDeniedError):
        await project_service.update_project(other_user.id, test_project.id, update_data)


@pytest.mark.asyncio
async def test_delete_project_success(project_service, test_user, test_project, uow_test):
    # Test successful deletion
    project_id = test_project.id
    await project_service.delete_project(test_user.id, project_id)

    # Verify deletion
    async with uow_test:
        assert await uow_test.project.find_one(id=project_id) is None


@pytest.mark.asyncio
async def test_delete_project_not_found(project_service, test_user):
    # Test non-existent project deletion
    with pytest.raises(ProjectNotFoundError):
        await project_service.delete_project(test_user.id, 99999)


@pytest.mark.asyncio
async def test_delete_project_unauthorized(project_service, other_user, test_project):
    # Test permission check
    with pytest.raises(PermissionDeniedError):
        await project_service.delete_project(other_user.id, test_project.id)
