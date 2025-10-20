import pytest
from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from psycopg_pool import AsyncConnectionPool


@pytest.mark.asyncio
async def test_connection_pool(
    db_pool: AsyncConnectionPool[AsyncConnection[TupleRow]],
) -> None:
    """Test that we can fetch a simple value from the async connection pool."""
    async with db_pool.connection() as conn, conn.cursor() as cur:
        await cur.execute("SELECT 1 AS value;")
        result = await cur.fetchall()

    # Each row is a tuple
    assert result[0][0] == 1
