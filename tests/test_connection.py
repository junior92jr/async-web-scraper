import pytest
from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from psycopg_pool import AsyncConnectionPool


@pytest.mark.asyncio
async def test_connection_pool_and_tables(
    db_pool: AsyncConnectionPool[AsyncConnection[TupleRow]],
) -> None:
    """Test that the connection pool works and tables exist."""
    async with db_pool.connection() as conn, conn.cursor() as cur:
        await cur.execute("SELECT 1 AS value;")
        result = await cur.fetchall()
        assert result[0][0] == 1

        tables = ["monitored_urls", "website_metrics"]
        for table in tables:
            await cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = %s
                );
                """,
                (table,),
            )
            row = await cur.fetchone()
            assert row is not None, f"Expected a result row for table {table}"
            exists = row[0]
            assert exists, f"Table {table} should exist in the database"


@pytest.mark.asyncio
async def test_connection_pool(
    db_pool: AsyncConnectionPool[AsyncConnection[TupleRow]],
) -> None:
    """Test that the connection pool works and a simple query succeeds."""
    async with db_pool.connection() as conn, conn.cursor() as cur:
        await cur.execute("SELECT 1 AS value;")
        result = await cur.fetchall()
        assert result[0][0] == 1


@pytest.mark.asyncio
async def test_tables_exist(
    db_pool: AsyncConnectionPool[AsyncConnection[TupleRow]],
) -> None:
    """Test that the required tables exist in the database."""
    tables = ["monitored_urls", "website_metrics"]
    async with db_pool.connection() as conn, conn.cursor() as cur:
        for table in tables:
            await cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = %s
                );
                """,
                (table,),
            )
            row = await cur.fetchone()
            assert row is not None, f"Expected a row for table {table}"
            exists = row[0]
            assert exists, f"Table {table} should exist"
