from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from utils.config import Settings

settings = Settings()

_pool: AsyncConnectionPool[AsyncConnection[dict]] | None = None


async def get_pool(override_url: str | None = None) -> AsyncConnectionPool[AsyncConnection[dict]]:
    """
    Get or create a global async connection pool.

    Parameters:
        override_url: Optional database URL (used for tests with pytest-postgresql)
    """
    global _pool
    if _pool is None:
        db_url = override_url or settings.DATABASE_URL
        if not db_url:
            raise ValueError("Database URL is not set in environment or .env file.")
        _pool = AsyncConnectionPool[AsyncConnection[dict]](
            conninfo=str(db_url),
            max_size=settings.MAX_POOL_SIZE,
            timeout=settings.SCRAPER_TIMEOUT,
        )
        await _pool.open()
    return _pool


async def close_pool() -> None:
    """Close the global database pool, if it exists."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
