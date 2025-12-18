import os

from fastapi import FastAPI
from app.logging.logger import get_logger
from sqlalchemy import text

from app.db.db import engine
from app.migrations.env_module import run_async_upgrade

logger = get_logger()


async def init_db(app: FastAPI) -> None:
    """
    Initialize main function for database.

    This function will do the following tasks:
    1. Try to connect database.
    2. Check the connection to database is healthy, if not, try to re-connect.
    3. Check if the table is created, if so, skip the process.
    """
    logger.info("init_db script start.")
    if os.path.isfile(".init_db.lock"):
        logger.warning(
            "Another process is already doing database initialization, stopping the init process."
        )
        return
    else:
        with open(".init_db.lock", "w") as f:
            logger.info(
                f"Creating database initialization lock file at: {os.path.abspath('.init_db.lock')}"
            )
            f.write("init_db locked")
        try:
            await _install_postgres_extensions()
            await _migrate_db()
        finally:
            try:
                os.remove(".init_db.lock")
            except OSError as e:
                logger.error(
                    f"An error occurred while attempting to remove the database initialization"
                    f" lock file at {os.path.abspath('.init_db.lock')}, error_msg: {e}"
                )
            else:
                logger.info("Remove lock file successfully.")

    logger.info("init_db script end.")


async def _install_postgres_extensions():
    """Install necessary extensions."""
    logger.info("Start to install postgres extensions.")
    try:
        async with engine.begin() as conn:
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
    except Exception as e:
        logger.error(f"database error:{e}")
        return True
    logger.info("Install extensions successfully.")


async def _migrate_db():
    """Do db migrations by alembic."""
    logger.info("Start to initialize tables.")
    try:
        await run_async_upgrade()
    except Exception as e:
        logger.error(f"database error:{e}")
        return True
    logger.info("DB migrations are successful.")