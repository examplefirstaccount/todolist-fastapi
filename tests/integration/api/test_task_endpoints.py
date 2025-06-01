import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_create_task_success(test_client, auth_headers, test_project):
    task_data = {
        "title": "New Task",
        "project_id": test_project.id,
        "priority": "high"
    }
    response = await test_client.post(
        "/tasks/",
        json=task_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "New Task"
    assert data["priority"] == "high"


@pytest.mark.asyncio
async def test_task_with_deadline(test_client, auth_headers):
    response = await test_client.post(
        "/tasks/",
        json={
            "title": "Task with deadline",
            "deadline": "2023-12-31T23:59:59"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["deadline"] == "2023-12-31T23:59:59"


@pytest.mark.asyncio
async def test_invalid_priority(test_client, auth_headers):
    response = await test_client.post(
        "/tasks/",
        json={
            "title": "Invalid priority",
            "priority": "invalid"
        },
        headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_bulk_task_creation(test_client, auth_headers):
    tasks = [{"title": f"Task {i}"} for i in range(5)]
    responses = [
        await test_client.post("/tasks/", json=task, headers=auth_headers)
        for task in tasks
    ]
    assert all(r.status_code == 201 for r in responses)


@pytest.mark.asyncio
async def test_create_task_unauthenticated(test_client):
    response = await test_client.post(
        "/tasks/",
        json={"title": "Should Fail"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_tasks(test_client, auth_headers, test_tasks):
    response = await test_client.get(
        "/tasks/",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == len(test_tasks)
    assert all(t["user_id"] == test_tasks[0].user_id for t in data)


@pytest.mark.asyncio
async def test_get_tasks_pagination(test_client, auth_headers, multiple_test_tasks):
    response = await test_client.get(
        "/tasks/?skip=5&limit=5",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 5


@pytest.mark.asyncio
async def test_get_task(test_client, auth_headers, test_task):
    response = await test_client.get(
        f"/tasks/{test_task.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_task.id


@pytest.mark.asyncio
async def test_get_task_unauthorized(test_client, test_task, other_user, auth_headers):
    # First login as other user
    other_auth = await test_client.post(
        "/auth/login",
        json={"username": other_user.username, "password": "other_password"}
    )
    print(other_auth.json())
    other_token = other_auth.json()["access_token"]

    # Try to access task owned by test_user
    response = await test_client.get(
        f"/tasks/{test_task.id}",
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_update_task(test_client, auth_headers, test_task):
    update_data = {
        "title": "Updated Title",
        "priority": "low"  # Testing priority update
    }
    response = await test_client.put(
        f"/tasks/{test_task.id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["priority"] == "low"


@pytest.mark.asyncio
async def test_update_task_priority_sorting(test_client, auth_headers, test_project_with_mixed_tasks):
    # Get tasks with proper priority sorting
    response = await test_client.get(
        f"/tasks/?project_id={test_project_with_mixed_tasks.id}&sort_by=priority&sort_order=asc",
        headers=auth_headers
    )
    tasks = response.json()

    # Verify priority order is low(0) < medium(1) < high(2)
    priorities = [t["priority"] for t in tasks]
    assert priorities == sorted(priorities, key=lambda p: ["low", "medium", "high"].index(p))


@pytest.mark.asyncio
async def test_delete_task(test_client, auth_headers, test_task):
    response = await test_client.delete(
        f"/tasks/{test_task.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify task is gone
    response = await test_client.get(
        f"/tasks/{test_task.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
