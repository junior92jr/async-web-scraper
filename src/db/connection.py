from typing import Any

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from utils.config import Settings

settings = Settings()


_pool_container: dict[str, AsyncConnectionPool[AsyncConnection[Any]] | None] = {
    "pool": None
}


async def get_pool(
    override_url: str | None = None,
) -> AsyncConnectionPool[AsyncConnection[Any]]:
    """Get or create a global async connection pool."""
    pool = _pool_container["pool"]
    if pool is None:
        db_url = override_url or settings.DATABASE_URL
        if not db_url:
            value_error_message = "Database URL is not set in environment or .env file."
            raise ValueError(value_error_message)
        pool = AsyncConnectionPool[AsyncConnection[Any]](
            conninfo=str(db_url),
            max_size=settings.MAX_POOL_SIZE,
            timeout=settings.SCRAPER_TIMEOUT,
        )
        await pool.open()
        _pool_container["pool"] = pool
    return pool
