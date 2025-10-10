from db.connection import get_pool
from utils.logger import logger


async def create_tables() -> None:
    """Create the necessary tables in the database if they do not exist,
    using a transaction to ensure atomic execution.
    """
    pool = await get_pool()
    async with pool.connection() as conn, conn.transaction(), conn.cursor() as cur:
        logger.info("Ensuring tables exist...")
        await cur.execute("""
                    CREATE TABLE IF NOT EXISTS website_metrics (
                        id SERIAL PRIMARY KEY,
                        url TEXT NOT NULL,
                        checked_at TIMESTAMPTZ NOT NULL,
                        status_code INTEGER,
                        response_time REAL,
                        regex_match BOOLEAN
                    );
                    """)
        await cur.execute("""
                    CREATE TABLE IF NOT EXISTS monitored_urls (
                        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        url TEXT NOT NULL UNIQUE,
                        interval INTEGER NOT NULL CHECK (interval BETWEEN 5 AND 300),
                        regex TEXT
                    );
                    """)
        logger.info("Tables checked/created.")
