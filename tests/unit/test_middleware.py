from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.core.middleware import log_requests


@pytest.fixture
def test_app():
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    @app.get("/error")
    async def error_endpoint():
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return app


@pytest.fixture
def mock_logger():
    with patch("app.core.middleware.logger") as mock_logger:
        yield mock_logger


@pytest.fixture
def mock_time():
    with patch("app.core.middleware.time") as mock_time:
        mock_time.time.side_effect = [100.0, 100.123]  # start time, end time
        yield mock_time


@pytest.mark.asyncio
async def test_middleware_passes_through_response(test_app, mock_logger, mock_time):
    """Test that middleware doesn't modify the response"""
    request = Request({
        "type": "http",
        "method": "GET",
        "path": "/test",
        "headers": [],
        "client": ("127.0.0.1", 12345)
    })

    async def call_next(_request):
        return JSONResponse({"original": "response"})

    response = await log_requests(request, call_next)
    assert response.body == b'{"original":"response"}'


@pytest.mark.asyncio
async def test_middleware_calls_call_next(test_app, mock_logger, mock_time):
    """Test that middleware properly calls the next handler"""
    mock_call_next = AsyncMock(return_value=JSONResponse({}))
    request = Request({
        "type": "http",
        "method": "GET",
        "path": "/test",
        "headers": [],
        "client": ("127.0.0.1", 12345)
    })

    response = await log_requests(request, mock_call_next)

    mock_call_next.assert_awaited_once_with(request)
    assert isinstance(response, JSONResponse)


def test_middleware_logs_correct_values(test_app, mock_logger, mock_time):
    """Test that middleware logs the expected values"""
    client = TestClient(test_app)
    test_app.middleware("http")(log_requests)

    _response = client.get("/test")

    # Verify the log output
    expected_log = {
        "method": "GET",
        "path": "/test",
        "status_code": 200,
        "process_time": "0.123s",
        "client": "testclient",
    }

    mock_logger.info.assert_called_once_with(expected_log)


def test_middleware_handles_missing_client(test_app, mock_logger, mock_time):
    """Test that middleware handles requests with no client info"""
    client = TestClient(test_app)
    test_app.middleware("http")(log_requests)

    # Create request without client headers
    _response = client.get("/test")

    # Verify log contains testclient (default TestClient host)
    assert mock_logger.info.call_args[0][0]["client"] == "testclient"


@pytest.mark.asyncio
async def test_middleware_handles_exceptions(test_app, mock_logger, mock_time):
    """Test that middleware still logs when call_next raises an exception"""
    client = TestClient(test_app)
    test_app.middleware("http")(log_requests)

    response = client.get("/error")

    expected_log = {
        "method": "GET",
        "path": "/error",
        "status_code": 500,
        "process_time": "0.123s",
        "client": "testclient",
    }

    assert response.status_code == 500
    mock_logger.info.assert_called_once_with(expected_log)
