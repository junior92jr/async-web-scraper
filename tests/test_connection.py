import pytest
from db.monitored_urls import get_monitored_urls

@pytest.mark.asyncio
async def test_db_connection(db_connection):
    """
    Test that the ephemeral test database connection works.
    """
    # Simple query via your connection
    result = await db_connection.execute("SELECT 1 AS value")
    row = await result.fetchone()

    assert row is not None
    assert row["value"] == 1

    # Also check monitored_urls table exists (empty at start)
    urls = await get_monitored_urls()
    assert urls == []