import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from app.api.endpoints import auth, tasks, projects, websocket
from app.core.middleware import log_requests
from app.core.config import settings
from app.core.logger import setup_logging
from app.db.database import async_session_maker
from app.exceptions.handlers import register_exception_handlers


setup_logging()
logger = logging.getLogger("app")

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Application startup.")
    try:
        db = async_session_maker()
        await db.execute(text("SELECT 1"))
        await db.close()
        logger.info("Database connected successfully.")
    except Exception as e:
        logger.exception("Failed to connect to the database.")
        raise e

    yield

    logger.info("Application shutdown.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.middleware("http")(log_requests)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(websocket.router)

register_exception_handlers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
