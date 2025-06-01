from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.utils.unitofwork import UnitOfWork


@pytest.mark.asyncio
async def test_uow_aenter_initializes_repos():
    mock_session = AsyncMock()
    mock_session_factory = MagicMock(return_value=mock_session)

    with patch("app.utils.unitofwork.async_session_maker", mock_session_factory):
        uow = UnitOfWork()
        async with uow:
            assert uow.session == mock_session
            assert uow.user.session is mock_session
            assert uow.task.session is mock_session
            assert uow.project.session is mock_session


@pytest.mark.asyncio
async def test_uow_commit_calls_session_commit():
    mock_session = AsyncMock()
    uow = UnitOfWork()
    uow.session = mock_session
    await uow.commit()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_uow_rollback_calls_session_rollback():
    mock_session = AsyncMock()
    uow = UnitOfWork()
    uow.session = mock_session
    await uow.rollback()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_uow_exit_rollbacks_and_closes():
    mock_session = AsyncMock()
    mock_session_factory = MagicMock(return_value=mock_session)

    with patch("app.utils.unitofwork.async_session_maker", mock_session_factory):
        uow = UnitOfWork()
        async with uow:
            pass

        mock_session.rollback.assert_awaited()
        mock_session.close.assert_awaited()
        assert uow.session is None


@pytest.mark.asyncio
async def test_uow_exit_on_exception_calls_rollback_and_close():
    mock_session = AsyncMock()
    mock_session_factory = MagicMock(return_value=mock_session)

    with patch("app.utils.unitofwork.async_session_maker", mock_session_factory):
        uow = UnitOfWork()

        class CustomError(Exception):
            pass

        with pytest.raises(CustomError):
            async with uow:
                raise CustomError("Simulated failure")

        mock_session.rollback.assert_awaited()
        mock_session.close.assert_awaited()
        assert uow.session is None
