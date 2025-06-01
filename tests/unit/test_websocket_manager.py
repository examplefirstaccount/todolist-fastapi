import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import WebSocket
from pydantic import BaseModel

from app.core.websockets import ConnectionManager


class SampleModel(BaseModel):
    field1: str
    field2: int


@pytest.fixture
def manager():
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    ws = MagicMock(spec=WebSocket)
    ws.send_text = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_connect_adds_new_connection(manager, mock_websocket):
    username = "test_user"

    await manager.connect(mock_websocket, username)

    assert username in manager.active_connections
    assert mock_websocket in manager.active_connections[username]
    mock_websocket.accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_multiple_sockets_same_user(manager, mock_websocket):
    username = "test_user"
    ws2 = MagicMock(spec=WebSocket)
    ws2.send_text = AsyncMock()

    await manager.connect(mock_websocket, username)
    await manager.connect(ws2, username)

    assert len(manager.active_connections[username]) == 2


def test_disconnect_removes_connection(manager, mock_websocket):
    username = "test_user"
    manager.active_connections[username] = [mock_websocket]

    manager.disconnect(mock_websocket, username)

    assert username not in manager.active_connections


def test_disconnect_multiple_connections(manager, mock_websocket):
    username = "test_user"
    ws2 = MagicMock(spec=WebSocket)
    manager.active_connections[username] = [mock_websocket, ws2]

    manager.disconnect(mock_websocket, username)

    assert username in manager.active_connections
    assert len(manager.active_connections[username]) == 1
    assert ws2 in manager.active_connections[username]


@pytest.mark.asyncio
async def test_send_personal_message(manager, mock_websocket):
    username = "test_user"
    manager.active_connections[username] = [mock_websocket]
    message = {"event": "test", "data": {"key": "value"}}

    await manager.send_personal_message(message, username)

    mock_websocket.send_text.assert_awaited_once_with(json.dumps(message))


@pytest.mark.asyncio
async def test_send_personal_message_multiple_sockets(manager, mock_websocket):
    username = "test_user"
    ws2 = MagicMock(spec=WebSocket)
    ws2.send_text = AsyncMock()
    manager.active_connections[username] = [mock_websocket, ws2]
    message = {"event": "test", "data": {"key": "value"}}

    await manager.send_personal_message(message, username)

    mock_websocket.send_text.assert_awaited_once_with(json.dumps(message))
    ws2.send_text.assert_awaited_once_with(json.dumps(message))


@pytest.mark.asyncio
async def test_send_personal_message_no_user(manager, mock_websocket):
    message = {"event": "test", "data": {"key": "value"}}

    # Should not raise any exception
    await manager.send_personal_message(message, "nonexistent_user")


@pytest.mark.asyncio
async def test_broadcast(manager, mock_websocket):
    ws2 = MagicMock(spec=WebSocket)
    ws2.send_text = AsyncMock()
    manager.active_connections = {
        "user1": [mock_websocket],
        "user2": [ws2]
    }
    message = {"event": "broadcast", "data": {"key": "value"}}

    await manager.broadcast(message)

    mock_websocket.send_text.assert_awaited_once_with(json.dumps(message))
    ws2.send_text.assert_awaited_once_with(json.dumps(message))


def test_prepare_message(manager):
    event_type = "sample_event"
    data = SampleModel(field1="test", field2=42)

    result = manager.prepare_message(event_type, data)

    assert result == {
        "event": event_type,
        "data": {"field1": "test", "field2": 42}
    }
