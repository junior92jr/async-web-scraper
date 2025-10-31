from collections.abc import AsyncGenerator
from typing import Any

import pytest_asyncio
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from src.db.connection import get_pool
from src.db.schema import create_tables
from utils.logger import logger

TEST_DB_URL = "postgresql://test_user:test_pass@test-db:5432/test_db"


@pytest_asyncio.fixture(scope="session")
async def db_pool() -> AsyncGenerator[AsyncConnectionPool[AsyncConnection]]:
    """Provide a database connection pool for testing."""
    pool = await get_pool(override_url=TEST_DB_URL)

    async with pool:
        logger.info("Creating tables in test DB...")
        await create_tables(pool)
        yield pool


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(
    db_pool: AsyncConnectionPool[AsyncConnection[Any]],
) -> AsyncGenerator[None]:
    """Automatically truncate tables before each test."""
    async with db_pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            "TRUNCATE TABLE monitored_urls, website_metrics RESTART IDENTITY CASCADE;"
        )
    yield
