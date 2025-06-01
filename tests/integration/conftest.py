from typing import AsyncGenerator, Any
from datetime import datetime, timedelta, UTC

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.api.dependencies.dependencies import get_uow
from app.core.security import get_password_hash
from app.db.models import Base
from app.services import AuthService, UserService, TaskService, ProjectService
from app.utils.unitofwork import UnitOfWork

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Async db session for repositories
@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, Any]:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

# Unit of Work instance with async session maker for services
@pytest.fixture
async def uow_test():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    uow = UnitOfWork()
    uow.session_factory = async_session_maker

    return uow

# Services
@pytest.fixture
async def auth_service(uow_test):
    return AuthService(uow_test)

@pytest.fixture
async def user_service(uow_test):
    return UserService(uow_test)

@pytest.fixture
async def task_service(uow_test):
    return TaskService(uow_test)

@pytest.fixture
async def project_service(uow_test):
    return ProjectService(uow_test)

# Test client for endpoints
@pytest.fixture
async def test_client(uow_test):
    app.dependency_overrides = {get_uow: lambda: uow_test}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

# Auth headers for endpoints
@pytest.fixture
async def auth_headers(test_client, test_user):
    res = await test_client.post("/auth/login", json={
        "username": "test_user",
        "password": "test_password"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# User service fixtures
@pytest.fixture
async def existing_user(uow_test):
    user_data = {
        "username": "existing_user",
        "hashed_password": get_password_hash("valid_password")
    }
    async with uow_test:
        user = await uow_test.user.add(user_data)
        await uow_test.commit()
        return user

@pytest.fixture
async def test_user(uow_test):
    user_data = {
        "username": "test_user",
        "hashed_password": get_password_hash("test_password")
    }
    async with uow_test:
        user = await uow_test.user.add(user_data)
        await uow_test.commit()
        return user

@pytest.fixture
async def other_user(uow_test):
    user_data = {
        "username": "other_user",
        "hashed_password": get_password_hash("other_password")
    }
    async with uow_test:
        user = await uow_test.user.add(user_data)
        await uow_test.commit()
        return user

# Project service fixtures
@pytest.fixture
async def test_project(uow_test, test_user):
    project_data = {"name": "Test Project", "owner_id": test_user.id}
    async with uow_test:
        project = await uow_test.project.add(project_data)
        await uow_test.commit()
        return project

@pytest.fixture
async def test_projects(uow_test, test_user):
    projects = []
    for i in range(3):
        project_data = {"name": f"Project {i}", "owner_id": test_user.id}
        async with uow_test:
            project = await uow_test.project.add(project_data)
            await uow_test.commit()
            projects.append(project)
    return projects

@pytest.fixture
async def other_users_project(uow_test, other_user):
    project_data = {"name": "Other Project", "owner_id": other_user.id}
    async with uow_test:
        project = await uow_test.project.add(project_data)
        await uow_test.commit()
        return project

@pytest.fixture
async def multiple_test_projects(uow_test, test_user):
    projects = []
    for i in range(10):
        project_data = {"name": f"Project {i}", "owner_id": test_user.id}
        async with uow_test:
            project = await uow_test.project.add(project_data)
            await uow_test.commit()
            projects.append(project)
    return projects

@pytest.fixture
async def test_project_with_tasks(uow_test, test_user):
    # Create project
    async with uow_test:
        project = await uow_test.project.add({"name": "With Tasks", "owner_id": test_user.id})
        await uow_test.commit()

    # Add tasks
    for i in range(3):
        task_data = {
            "title": f"Task {i}",
            "user_id": test_user.id,
            "project_id": project.id
        }
        async with uow_test:
            await uow_test.task.add(task_data)
            await uow_test.commit()

    return project

@pytest.fixture
async def test_project_with_mixed_tasks(uow_test, test_user):
    # Create project
    async with uow_test:
        project = await uow_test.project.add({"name": "Mixed Tasks", "owner_id": test_user.id})
        await uow_test.commit()

    # Add varied tasks
    task_types = [
        {"is_completed": True, "priority": "low"},
        {"is_completed": False, "priority": "medium"},
        {"is_completed": True, "priority": "high"},
        {"is_completed": False, "priority": "high"},
    ]

    for i, task_type in enumerate(task_types):
        task_data = {
            "title": f"Task {i}",
            "user_id": test_user.id,
            "project_id": project.id,
            "created_at": datetime.now(UTC) - timedelta(hours=i),
            **task_type
        }
        async with uow_test:
            await uow_test.task.add(task_data)
            await uow_test.commit()

    return project

# Task service fixtures
@pytest.fixture
async def test_task(uow_test, test_user):
    task_data = {"title": "Test Task", "user_id": test_user.id}
    async with uow_test:
        task = await uow_test.task.add(task_data)
        await uow_test.commit()
        return task

@pytest.fixture
async def test_tasks(uow_test, test_user):
    tasks = []
    for i in range(3):
        task_data = {"title": f"Task {i}", "user_id": test_user.id}
        async with uow_test:
            task = await uow_test.task.add(task_data)
            await uow_test.commit()
            tasks.append(task)
    return tasks

@pytest.fixture
async def multiple_test_tasks(uow_test, test_user):
    tasks = []
    for i in range(10):
        task_data = {"title": f"Task {i}", "user_id": test_user.id}
        async with uow_test:
            task = await uow_test.task.add(task_data)
            await uow_test.commit()
            tasks.append(task)
    return tasks
