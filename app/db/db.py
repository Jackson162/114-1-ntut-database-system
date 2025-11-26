from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DB_ECHO,
)
session_factory = async_scoped_session(
    async_sessionmaker(
        engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    ),
    scopefunc=current_task,
)


async def reset_db_engine():
    global engine
    await engine.dispose()
    engine = create_async_engine(
        settings.DATABASE_URI,
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        echo=settings.DB_ECHO,
    )


def get_scoped_session() -> async_scoped_session:
    """Get scoped session in current coroutine."""
    return async_scoped_session(
        async_sessionmaker(
            engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        ),
        scopefunc=current_task,
    )
