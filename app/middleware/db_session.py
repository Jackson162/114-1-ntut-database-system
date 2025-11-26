"""Database session middleware utilities."""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Request
from app.logging.logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import session_factory

logger = get_logger()


async def get_db_session(
    request: Request = None,  # type: ignore
    request_name: str = "",
) -> AsyncGenerator[AsyncSession, None]:
    """Return a async database session."""
    start_time = time.time()
    request_name = (
        request_name if request_name else request.method + " " + str(request.url) if request else ""
    )
    async with session_factory() as session:
        got_db_time = time.time()
        logger.debug(
            (
                f"The request {request_name} opened a db session: {id(session)},"
                f" time elapsed: {got_db_time-start_time:.3f}s"
            )
        )
        try:
            yield session
        finally:
            await session_factory.remove()
            logger.debug(
                (
                    f"The request {request_name} "
                    f"closed the db session: {id(session)} "
                    f"time elapsed: {time.time() - got_db_time:.3f}s"
                )
            )


get_db_session_context_manager = asynccontextmanager(get_db_session)
