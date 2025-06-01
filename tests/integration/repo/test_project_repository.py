import pytest
from sqlalchemy.exc import IntegrityError

from app.repositories import ProjectRepository, UserRepository


@pytest.mark.asyncio
async def test_add_and_find_project(db_session):
    user_repo = UserRepository(db_session)
    project_repo = ProjectRepository(db_session)

    user = await user_repo.add({
        "username": "projectowner",
        "hashed_password": "123"
    })

    new_project = await project_repo.add({
        "name": "Project Alpha",
        "description": "First project",
        "owner_id": user.id
    })

    assert new_project.name == "Project Alpha"
    assert new_project.owner_id == user.id

    found = await project_repo.find_one(name="Project Alpha")
    assert found is not None
    assert found.id == new_project.id


@pytest.mark.asyncio
async def test_delete_project(db_session):
    user_repo = UserRepository(db_session)
    project_repo = ProjectRepository(db_session)

    user = await user_repo.add({
        "username": "deleteme",
        "hashed_password": "123"
    })

    project = await project_repo.add({
        "name": "To Delete",
        "description": "Bye bye",
        "owner_id": user.id
    })

    deleted = await project_repo.delete(id=project.id)
    assert deleted is True

    should_be_none = await project_repo.find_one(id=project.id)
    assert should_be_none is None


@pytest.mark.asyncio
async def test_update_project_description(db_session):
    user_repo = UserRepository(db_session)
    project_repo = ProjectRepository(db_session)

    user = await user_repo.add({
        "username": "updater",
        "hashed_password": "123"
    })

    project = await project_repo.add({
        "name": "Old Project",
        "description": "Old desc",
        "owner_id": user.id
    })

    updated = await project_repo.update(
        {"description": "Updated description"},
        id=project.id
    )

    assert updated is not None
    assert updated.description == "Updated description"


@pytest.mark.asyncio
async def test_find_all_projects_with_order_and_filter(db_session):
    user_repo = UserRepository(db_session)
    project_repo = ProjectRepository(db_session)

    user = await user_repo.add({
        "username": "manyprojects",
        "hashed_password": "123"
    })

    await project_repo.add({"name": "Zeta", "description": "Z", "owner_id": user.id})
    await project_repo.add({"name": "Alpha", "description": "A", "owner_id": user.id})
    await project_repo.add({"name": "Beta", "description": "B", "owner_id": user.id})

    results = await project_repo.find_all(
        owner_id=user.id,
        order_by={"name": "asc"},
        limit=2
    )

    assert len(results) == 2
    assert results[0].name == "Alpha"
    assert results[1].name == "Beta"


@pytest.mark.asyncio
async def test_add_project_without_owner_fails(db_session):
    repo = ProjectRepository(db_session)

    with pytest.raises(IntegrityError):
        await repo.add({
            "name": "Orphan Project",
            "description": "No owner",
            # Missing owner_id
        })


@pytest.mark.asyncio
async def test_update_nonexistent_project_returns_none(db_session):
    repo = ProjectRepository(db_session)

    result = await repo.update({"name": "Doesn't Matter"}, id=99999)
    assert result is None


@pytest.mark.asyncio
async def test_delete_nonexistent_project_returns_false(db_session):
    repo = ProjectRepository(db_session)
    deleted = await repo.delete(id=98765)
    assert deleted is False
