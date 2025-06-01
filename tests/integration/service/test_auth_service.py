import pytest

from app.api.schemas.user import UserCreate, UserLogin
from app.core.security import verify_password
from app.exceptions import UserAlreadyExistsError, InvalidCredentialsError


@pytest.mark.asyncio
async def test_register_new_user(auth_service, uow_test):
    # Test full registration flow
    new_user = UserCreate(
        username="new_user",
        password="strong_password"
    )

    _result = await auth_service.register(new_user)

    # Verify database state
    async with uow_test:
        db_user = await uow_test.user.find_one(username=new_user.username)
        assert db_user is not None
        assert db_user.username == new_user.username
        assert verify_password(new_user.password, db_user.hashed_password)


@pytest.mark.asyncio
async def test_register_duplicate_user(auth_service, existing_user):
    duplicate_user = UserCreate(
        username="existing_user",
        password="any_password"
    )

    with pytest.raises(UserAlreadyExistsError):
        await auth_service.register(duplicate_user)


@pytest.mark.asyncio
async def test_login_success(auth_service, existing_user):
    credentials = UserLogin(
        username="existing_user",
        password="valid_password"
    )

    result = await auth_service.login(credentials)

    assert "access_token" in result
    assert result["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(auth_service, existing_user):
    credentials = UserLogin(
        username="existing_user",
        password="wrong_password"
    )

    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(credentials)


@pytest.mark.asyncio
async def test_login_wrong_username(auth_service, existing_user):
    credentials = UserLogin(
        username="non_existing_user",
        password="wrong_password"
    )

    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(credentials)
