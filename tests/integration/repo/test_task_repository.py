from datetime import datetime, timedelta, UTC

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.models import PriorityLevel
from app.repositories import UserRepository, ProjectRepository, TaskRepository


@pytest.mark.asyncio
async def test_add_and_find_task(db_session):
    user_repo = UserRepository(db_session)
    project_repo = ProjectRepository(db_session)
    task_repo = TaskRepository(db_session)

    user = await user_repo.add({
        "username": "taskuser",
        "hashed_password": "pass"
    })

    project = await project_repo.add({
        "name": "TaskProject",
        "description": "Proj",
        "owner_id": user.id
    })

    deadline = datetime.now(UTC) + timedelta(days=1)
    task = await task_repo.add({
        "title": "Task 1",
        "description": "Important task",
        "priority": PriorityLevel.high,
        "deadline": deadline,
        "user_id": user.id,
        "project_id": project.id
    })

    assert task.title == "Task 1"
    assert task.user_id == user.id

    found = await task_repo.find_one(id=task.id)
    assert found is not None
    assert found.title == "Task 1"


@pytest.mark.asyncio
async def test_update_task_status_and_priority(db_session):
    user_repo = UserRepository(db_session)
    task_repo = TaskRepository(db_session)

    user = await user_repo.add({
        "username": "changeme",
        "hashed_password": "pass"
    })

    task = await task_repo.add({
        "title": "Initial Task",
        "description": "To update",
        "priority": PriorityLevel.low,
        "user_id": user.id
    })

    updated = await task_repo.update(
        {"is_completed": True, "priority": PriorityLevel.high},
        id=task.id
    )

    assert updated is not None
    assert updated.is_completed is True
    assert updated.priority == PriorityLevel.high


@pytest.mark.asyncio
async def test_delete_task(db_session):
    user_repo = UserRepository(db_session)
    task_repo = TaskRepository(db_session)

    user = await user_repo.add({
        "username": "deleter",
        "hashed_password": "pass"
    })

    task = await task_repo.add({
        "title": "DeleteMe",
        "user_id": user.id
    })

    deleted = await task_repo.delete(id=task.id)
    assert deleted is True

    should_be_none = await task_repo.find_one(id=task.id)
    assert should_be_none is None


@pytest.mark.asyncio
async def test_find_all_tasks_by_user_ordered(db_session):
    user_repo = UserRepository(db_session)
    task_repo = TaskRepository(db_session)

    user = await user_repo.add({
        "username": "taskguy",
        "hashed_password": "pass"
    })

    await task_repo.add({"title": "C Task", "priority": PriorityLevel.low, "user_id": user.id})
    await task_repo.add({"title": "A Task", "priority": PriorityLevel.medium, "user_id": user.id})
    await task_repo.add({"title": "B Task", "priority": PriorityLevel.high, "user_id": user.id})

    tasks = await task_repo.find_all(
        user_id=user.id,
        order_by={"title": "asc"}
    )

    assert [t.title for t in tasks] == ["A Task", "B Task", "C Task"]


@pytest.mark.asyncio
async def test_add_task_without_user_fails(db_session):
    task_repo = TaskRepository(db_session)

    with pytest.raises(IntegrityError):
        await task_repo.add({
            "title": "No User",
            "description": "Fails",
            # user_id is missing
        })


@pytest.mark.asyncio
async def test_update_nonexistent_task_returns_none(db_session):
    task_repo = TaskRepository(db_session)

    result = await task_repo.update({"title": "Won't Work"}, id=99999)
    assert result is None


@pytest.mark.asyncio
async def test_delete_nonexistent_task_returns_false(db_session):
    task_repo = TaskRepository(db_session)

    result = await task_repo.delete(id=98765)
    assert result is False
