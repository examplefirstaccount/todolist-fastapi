from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
DATABASE_PARAMS = {}

engine = create_async_engine(url=DATABASE_URL, **DATABASE_PARAMS)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
