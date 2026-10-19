from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def get_engine() -> AsyncEngine:
    return create_async_engine(settings.database_url, echo=settings.db_echo, future=True, isolation_level="AUTOCOMMIT")


engine = get_engine()
AsyncSessionMaker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionMaker() as session:
        yield session


__all__ = ["engine", "AsyncSessionMaker", "get_db_session"]
