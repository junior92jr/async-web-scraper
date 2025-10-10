from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from utils.config import Settings

settings = Settings()

_pool: AsyncConnectionPool[AsyncConnection[dict]] | None = None


async def get_pool() -> AsyncConnectionPool[AsyncConnection[dict]]:
    """Get or create a global async connection pool."""
    global _pool
    if _pool is None:
        if settings.DATABASE_URL is None:
            raise ValueError("DATABASE_URL is not set in environment or .env file.")
        _pool = AsyncConnectionPool[AsyncConnection[dict]](
            conninfo=str(settings.DATABASE_URL),
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
