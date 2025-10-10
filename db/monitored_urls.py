import json

from db.connection import get_pool
from psycopg.errors import DatabaseError
from psycopg.rows import dict_row
from pydantic import BaseModel, Field, HttpUrl
from utils.logger import logger


class MonitoredURL(BaseModel):
    """Schema for monitored URL entries."""

    url: HttpUrl
    interval: int = Field(..., ge=5, le=300, description="Interval in seconds (5-300)")
    regex: str | None = None


async def get_monitored_urls() -> list[MonitoredURL]:
    """Fetch all monitored URLs from the database as dicts."""
    pool = await get_pool()
    try:
        async with pool.connection() as conn:
            conn.row_factory = dict_row
            rows = await (
                await conn.execute("SELECT url, interval, regex FROM monitored_urls")
            ).fetchall()

        monitored_urls = [MonitoredURL(**row) for row in rows]
        logger.info(f"Loaded {len(monitored_urls)} monitored URL(s).")
        return monitored_urls

    except DatabaseError as e:
        logger.error(f"Failed to fetch monitored URLs: {e}")
        return []


def _load_json_file(json_path: str) -> list[MonitoredURL]:
    """Load and validate JSON file into a list of MonitoredURL models."""
    try:
        with open(json_path, encoding="utf-8") as f:
            raw_data = json.load(f)

        if not isinstance(raw_data, list):
            raise ValueError("JSON root must be a list.")

        monitored_urls = [MonitoredURL(**entry) for entry in raw_data]
        return monitored_urls

    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        logger.error(f"Error loading JSON from {json_path}: {e}")
        raise


async def load_monitored_urls_from_file(json_path: str) -> None:
    """Load monitored URLs from a JSON file into the database using Pydantic models."""
    pool = await get_pool()
    try:
        data = _load_json_file(json_path)

        async with pool.connection() as conn, conn.cursor() as cur:
            for entry in data:
                logger.info(f"Upserting monitored URL: {entry.url}")
                await cur.execute(
                    """INSERT INTO monitored_urls (url, interval, regex)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (url) DO UPDATE SET
                            interval = EXCLUDED.interval,
                            regex = EXCLUDED.regex;
                        """,
                    (str(entry.url), entry.interval, entry.regex),
                )

        logger.info("Monitored URLs successfully upserted.")
    except Exception as e:
        logger.error(f"Failed to load monitored URLs from file: {e}")
