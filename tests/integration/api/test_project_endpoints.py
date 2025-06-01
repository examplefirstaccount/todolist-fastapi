import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_create_project_success(test_client, auth_headers):
    project_data = {"name": "New Project"}
    response = await test_client.post(
        "/projects/",
        json=project_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "New Project"


@pytest.mark.asyncio
async def test_create_project_unauthenticated(test_client):
    response = await test_client.post(
        "/projects/",
        json={"name": "Should Fail"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_projects(test_client, auth_headers, test_projects):
    response = await test_client.get(
        "/projects/",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == len(test_projects)
    assert all(p["owner_id"] == test_projects[0].owner_id for p in data)


@pytest.mark.asyncio
async def test_get_projects_pagination(test_client, auth_headers, multiple_test_projects):
    response = await test_client.get(
        "/projects/?skip=5&limit=5",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 5


@pytest.mark.asyncio
async def test_pagination_out_of_bounds(test_client, auth_headers):
    response = await test_client.get(
        "/projects/?skip=1000",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_get_project(test_client, auth_headers, test_project):
    response = await test_client.get(
        f"/projects/{test_project.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_project.id


@pytest.mark.asyncio
async def test_get_project_unauthorized(test_client, other_users_project, auth_headers):
    response = await test_client.get(
        f"/projects/{other_users_project.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_project_tasks(test_client, auth_headers, test_project_with_tasks):
    response = await test_client.get(
        f"/projects/{test_project_with_tasks.id}/tasks",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3


@pytest.mark.asyncio
async def test_get_project_tasks_filtering(test_client, auth_headers, test_project_with_mixed_tasks):
    # Test completed filter
    response = await test_client.get(
        f"/projects/{test_project_with_mixed_tasks.id}/tasks?completed=true",
        headers=auth_headers
    )
    assert all(t["is_completed"] for t in response.json())

    # Test priority filter
    response = await test_client.get(
        f"/projects/{test_project_with_mixed_tasks.id}/tasks?priority=high",
        headers=auth_headers
    )
    assert all(t["priority"] == "high" for t in response.json())


@pytest.mark.asyncio
async def test_get_project_tasks_sorting(test_client, auth_headers, test_project_with_mixed_tasks):
    # Test created_at desc
    response = await test_client.get(
        f"/projects/{test_project_with_mixed_tasks.id}/tasks?sort_by=created_at&sort_order=desc",
        headers=auth_headers
    )
    tasks = response.json()
    assert tasks[0]["created_at"] > tasks[-1]["created_at"]

    # Test priority asc
    response = await test_client.get(
        f"/projects/{test_project_with_mixed_tasks.id}/tasks?sort_by=priority&sort_order=asc",
        headers=auth_headers
    )
    tasks = response.json()
    assert tasks[0]["priority"] == "low"


@pytest.mark.asyncio
async def test_update_project(test_client, auth_headers, test_project):
    update_data = {"name": "Updated Name"}
    response = await test_client.put(
        f"/projects/{test_project.id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_project_unauthorized(test_client, auth_headers, other_users_project):
    response = await test_client.put(
        f"/projects/{other_users_project.id}",
        json={"name": "Should Fail"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_project(test_client, auth_headers, test_project):
    response = await test_client.delete(
        f"/projects/{test_project.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify project is gone
    response = await test_client.get(
        f"/projects/{test_project.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
