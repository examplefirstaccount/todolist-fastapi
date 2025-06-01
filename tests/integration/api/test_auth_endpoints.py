import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_register_endpoint(test_client):
    # Test successful registration
    user_data = {
        "username": "new_user",
        "password": "securepassword123"
    }
    response = await test_client.post(
        "/auth/register",
        json=user_data
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "new_user"
    assert "id" in data
    assert "password" not in data  # Ensure password isn't leaked


@pytest.mark.asyncio
async def test_register_existing_user(test_client, existing_user):
    # Test duplicate registration
    user_data = {
        "username": "existing_user",  # From your existing_user fixture
        "password": "anypassword"
    }
    response = await test_client.post(
        "/auth/register",
        json=user_data
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(test_client, existing_user):
    # Test successful login
    login_data = {
        "username": "existing_user",
        "password": "valid_password"  # From your existing_user fixture
    }
    response = await test_client.post(
        "/auth/login",
        json=login_data
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(test_client, existing_user):
    # Test failed login
    login_data = {
        "username": "existing_user",
        "password": "wrong_password"
    }
    response = await test_client.post(
        "/auth/login",
        json=login_data
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(test_client):
    # Test login with non-existent user
    login_data = {
        "username": "ghost_user",
        "password": "anypassword"
    }
    response = await test_client.post(
        "/auth/login",
        json=login_data
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
