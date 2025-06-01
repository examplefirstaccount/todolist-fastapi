from datetime import datetime

import pytest

from app.api.schemas.project import ProjectBase, ProjectCreate, ProjectUpdate, ProjectResponse
from app.api.schemas.task import TaskCreate, TaskUpdate, TaskResponse, PriorityLevel
from app.api.schemas.user import UserBase, UserCreate, UserLogin, UserResponse


def test_user_base_validation():
    # Test valid username
    valid_user = UserBase(username="valid")
    assert valid_user.username == "valid"

    # Test field constraints
    with pytest.raises(ValueError):
        UserBase(username="a")  # Too short (min_length=3)

    with pytest.raises(ValueError):
        UserBase(username="a" * 51)  # Too long (max_length=50)


def test_user_create_password():
    # Test password requirements
    valid = UserCreate(username="test", password="longenough")
    assert valid.password == "longenough"

    with pytest.raises(ValueError):
        UserCreate(username="test", password="short")  # Too short


def test_user_login_similar_to_create():
    # Test login schema matches create schema
    login = UserLogin(username="test", password="password")
    assert login.username == "test"


def test_user_response_omit_password():
    # Test ORM conversion omits sensitive fields
    orm_data = {
        "id": 1,
        "username": "testuser",
        "hashed_password": "secret"  # Shouldn't appear in response
    }

    response = UserResponse.model_validate(orm_data)
    assert response.id == 1
    assert not hasattr(response, 'hashed_password')


def test_task_create_validation():
    # Test valid creation
    valid_task = TaskCreate(
        title="Valid Task",
        priority=PriorityLevel.high
    )
    assert valid_task.title == "Valid Task"

    # Test field constraints
    with pytest.raises(ValueError):
        TaskCreate(title="")  # Empty title

    with pytest.raises(ValueError):
        TaskCreate(title="a" * 101)  # Exceeds max_length


def test_task_update_partial():
    # Test partial updates
    update = TaskUpdate(title="New Title")
    assert update.title == "New Title"
    assert update.description is None  # Other fields remain optional

    # Test all fields can be updated
    full_update = TaskUpdate(
        title="Title",
        description="Desc",
        is_completed=True,
        priority=PriorityLevel.low,
        deadline=datetime.now()
    )
    assert full_update.is_completed is True


def test_task_response_from_orm():
    # Test ORM model conversion
    orm_data = {
        "id": 1,
        "title": "ORM Task",
        "user_id": 1,
        "created_at": datetime.now(),
        "updated_at": None,
        "is_completed": False,
        "priority": "high"
    }

    response = TaskResponse.model_validate(orm_data)
    assert response.id == 1
    assert response.priority == PriorityLevel.high


def test_project_base_validation():
    # Test valid creation
    valid_project = ProjectBase(name="Valid Project")
    assert valid_project.name == "Valid Project"

    # Test field constraints
    with pytest.raises(ValueError):
        ProjectBase(name="")  # Empty name

    with pytest.raises(ValueError):
        ProjectBase(name="a" * 101)  # Exceeds max_length


def test_project_create_inheritance():
    # Test inheritance from ProjectBase
    project = ProjectCreate(name="New Project", description="Test")
    assert project.description == "Test"


def test_project_update_partial():
    # Test partial updates
    update = ProjectUpdate(name="Updated Name")
    assert update.name == "Updated Name"
    assert update.description is None

    # Test all fields can be updated
    full_update = ProjectUpdate(
        name="Full Update",
        description="New description"
    )
    assert full_update.description == "New description"


def test_project_response_from_orm():
    # Test ORM model conversion
    orm_data = {
        "id": 1,
        "name": "ORM Project",
        "owner_id": 1,
        "created_at": datetime.now(),
        "description": "Test"
    }

    response = ProjectResponse.model_validate(orm_data)
    assert response.id == 1
    assert response.owner_id == 1
