import pytest
from sqlalchemy.exc import IntegrityError

from app.repositories import UserRepository


@pytest.mark.asyncio
async def test_add_and_find_user(db_session):
    repo = UserRepository(db_session)

    new_user = await repo.add({
        "username": "testuser",
        "hashed_password": "fakehash"
    })

    assert new_user.username == "testuser"

    found_user = await repo.find_one(username="testuser")
    assert found_user is not None
    assert found_user.id == new_user.id


@pytest.mark.asyncio
async def test_delete_user(db_session):
    repo = UserRepository(db_session)

    user = await repo.add({
        "username": "todelete",
        "hashed_password": "xxx"
    })

    deleted = await repo.delete(id=user.id)
    assert deleted is True

    should_be_none = await repo.find_one(id=user.id)
    assert should_be_none is None


@pytest.mark.asyncio
async def test_delete_nonexistent_user_returns_false(db_session):
    repo = UserRepository(db_session)

    deleted = await repo.delete(id=999)
    assert deleted is False


@pytest.mark.asyncio
async def test_find_all_with_limit_and_order(db_session):
    repo = UserRepository(db_session)

    await repo.add({"username": "b", "hashed_password": "x"})
    await repo.add({"username": "a", "hashed_password": "x"})
    await repo.add({"username": "c", "hashed_password": "x"})

    users = await repo.find_all(order_by={"username": "asc"}, limit=2)
    assert len(users) == 2
    assert users[0].username == "a"
    assert users[1].username == "b"


@pytest.mark.asyncio
async def test_update_user_success(db_session):
    repo = UserRepository(db_session)

    user = await repo.add({"username": "updatable", "hashed_password": "old"})
    updated = await repo.update({"hashed_password": "new"}, id=user.id)

    assert updated is not None
    assert updated.hashed_password == "new"


@pytest.mark.asyncio
async def test_update_user_not_found(db_session):
    repo = UserRepository(db_session)

    result = await repo.update({"hashed_password": "new"}, id=999)
    assert result is None


@pytest.mark.asyncio
async def test_add_duplicate_user_raises(db_session):
    repo = UserRepository(db_session)

    await repo.add({"username": "dupe", "hashed_password": "x"})

    with pytest.raises(IntegrityError):
        await repo.add({"username": "dupe", "hashed_password": "y"})
