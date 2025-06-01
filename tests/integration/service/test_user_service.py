import pytest

from app.api.schemas.user import UserCreate
from app.core.security import verify_password
from app.exceptions import UserNotFoundError, UserAlreadyExistsError
from app.services import UserService


@pytest.mark.asyncio
async def test_create_user_success(user_service: UserService, uow_test):
    # Test successful user creation
    new_user = UserCreate(
        username="new_user",
        password="secure_password123"
    )

    created_user = await user_service.create_user(new_user)

    # Verify returned data
    assert created_user.username == "new_user"

    # Verify database state
    async with uow_test:
        db_user = await uow_test.user.find_one(username="new_user")
        assert db_user is not None
        assert db_user.username == "new_user"
        assert verify_password(new_user.password, db_user.hashed_password)


@pytest.mark.asyncio
async def test_create_user_duplicate(user_service: UserService, existing_user):
    # Test duplicate username rejection
    duplicate_user = UserCreate(
        username="existing_user",
        password="any_password"
    )

    with pytest.raises(UserAlreadyExistsError):
        await user_service.create_user(duplicate_user)


@pytest.mark.asyncio
async def test_get_users(user_service: UserService, existing_user):
    # Test retrieving all users
    users = await user_service.get_users()

    assert len(users) == 1
    assert users[0].username == "existing_user"


@pytest.mark.asyncio
async def test_get_users_pagination(user_service: UserService, uow_test):
    # Create multiple test users
    for i in range(1, 6):
        async with uow_test:
            await uow_test.user.add({
                "username": f"user_{i}",
                "hashed_password": "hash"
            })
            await uow_test.commit()

    # Test pagination
    first_page = await user_service.get_users(skip=0, limit=2)
    assert len(first_page) == 2

    second_page = await user_service.get_users(skip=2, limit=2)
    assert len(second_page) == 2
    assert {u.username for u in first_page}.isdisjoint(
        {u.username for u in second_page})


@pytest.mark.asyncio
async def test_get_user_by_id_success(user_service: UserService, existing_user):
    # Test successful lookup
    user = await user_service.get_user_by_id(existing_user.id)
    assert user.username == "existing_user"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service: UserService):
    # Test non-existent user
    with pytest.raises(UserNotFoundError):
        await user_service.get_user_by_id(99999)  # Non-existent ID


@pytest.mark.asyncio
async def test_get_user_by_username_success(user_service: UserService, existing_user):
    # Test successful lookup
    user = await user_service.get_user_by_username("existing_user")
    assert user.id == existing_user.id


@pytest.mark.asyncio
async def test_get_user_by_username_not_found(user_service: UserService):
    # Test non-existent user
    with pytest.raises(UserNotFoundError):
        await user_service.get_user_by_username("ghost_user")


@pytest.mark.asyncio
async def test_delete_user_success(user_service: UserService, existing_user, uow_test):
    # Test successful deletion
    user_id = existing_user.id
    await user_service.delete_user(user_id)

    # Verify deletion
    async with uow_test:
        assert await uow_test.user.find_one(id=user_id) is None


@pytest.mark.asyncio
async def test_delete_user_not_found(user_service: UserService):
    # Test deletion of non-existent user
    with pytest.raises(UserNotFoundError):
        await user_service.delete_user(99999)  # Non-existent ID
