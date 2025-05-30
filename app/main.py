from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from app.api.endpoints import auth
from app.core.config import settings
from app.db.database import async_session_maker
from app.exceptions.handlers import register_exception_handlers

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup code
    try:
        db = async_session_maker()
        await db.execute(text("SELECT 1"))
        await db.close()
        print("✅ Database connected successfully.")
    except Exception as e:
        print("❌ Failed to connect to the database.")
        raise e

    yield

    # Shutdown code
    print("🛑 Application shutdown.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)
app.include_router(auth.router)
# app.include_router(tasks.router)
# app.include_router(websocket.router)
register_exception_handlers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
