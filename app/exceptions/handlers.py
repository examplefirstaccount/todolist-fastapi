import logging

from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from starlette import status

from app.exceptions import (
    TokenError,
    NotFoundError,
    AlreadyExistsError,
    UnauthorizedError,
    ForbiddenError,
    PermissionDeniedError
)

logger = logging.getLogger("app")


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(_: Request, exc: NotFoundError):
        logger.warning(f"NotFoundError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)}
        )

    @app.exception_handler(AlreadyExistsError)
    async def already_exists_exception_handler(_: Request, exc: AlreadyExistsError):
        logger.warning(f"AlreadyExistsError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)}
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_exception_handler(_: Request, exc: UnauthorizedError):
        logger.warning(f"UnauthorizedError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc) or "Unauthorized"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_exception_handler(_: Request, exc: ForbiddenError):
        logger.warning(f"ForbiddenError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc) or "Access forbidden"},
        )

    @app.exception_handler(TokenError)
    async def token_exception_handler(_: Request, exc: TokenError):
        logger.warning(f"TokenError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_exception_handler(_: Request, exc: PermissionDeniedError):
        logger.warning(f"PermissionDeniedError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(_: Request, _exc: Exception):
        logger.exception("Unhandled exception occurred")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )
