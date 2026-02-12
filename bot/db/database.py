from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.config import settings

engine = create_async_engine(
    settings.postgres_dsn,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with session_factory() as session:
        yield session
