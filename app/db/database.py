from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

if settings.MODE == "TEST":
    DATABASE_URL = settings.TEST_DABASE_URL
    DATABASE_PARAMS = {"poolclass": NullPool}
else:
    DATABASE_URL = settings.DATABASE_URL
    DATABASE_PARAMS = {}

engine = create_async_engine(url=DATABASE_URL, **DATABASE_PARAMS)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    db = async_session_maker()
    try:
        yield db
    finally:
        await db.close()
