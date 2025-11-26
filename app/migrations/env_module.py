"""
You use import the functions and call it in this module instead of
using alembic command
"""
from concurrent.futures import ProcessPoolExecutor

from alembic import command, config
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


ALEMBIC_CONFIG = config.Config("alembic.ini")
ALEMBIC_CONFIG.set_main_option("sqlalchemy.url", settings.DATABASE_URI)


async def run_async_upgrade():
    async_engine = create_async_engine(settings.DATABASE_URI, echo=True)
    async with async_engine.begin() as conn:
        await conn.run_sync(_run_upgrade)


def _upgrade_head():
    command.upgrade(ALEMBIC_CONFIG, "head")


def _run_upgrade(connection):
    ALEMBIC_CONFIG.attributes["connection"] = connection

    # we use new process to run to avoid loop collision.
    # we didn't use threading cause there is a logging bug.
    with ProcessPoolExecutor() as executor:
        future = executor.submit(_upgrade_head)
        future.result()
