from collections.abc import AsyncGenerator

import pytest_asyncio
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from src.db.connection import get_pool

TEST_DB_URL = "postgresql://test_user:test_pass@test-db:5432/test_db"


@pytest_asyncio.fixture
async def db_pool() -> AsyncGenerator[AsyncConnectionPool[AsyncConnection[dict]]]:
    """Provide a database connection pool for testing."""
    pool = await get_pool(override_url=TEST_DB_URL)
    async with pool:
        yield pool
