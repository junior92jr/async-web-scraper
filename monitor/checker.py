import asyncio
import re
import ssl
import time
from datetime import UTC, datetime

import aiohttp
import certifi
from db.monitored_urls import MonitoredURL
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from utils.logger import logger

ssl_context = ssl.create_default_context(cafile=certifi.where())


async def check_website(
    monitored_url: MonitoredURL,
    session: aiohttp.ClientSession,
    pool: AsyncConnectionPool[AsyncConnection[dict]],
):
    """Check a website at regular intervals and log the results to the database."""
    compiled_regex = re.compile(monitored_url.regex) if monitored_url.regex else None

    try:
        while True:
            start_time = datetime.now(UTC)
            t0 = time.monotonic()

            try:
                async with session.get(
                    str(monitored_url.url), timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    status = response.status
                    text = await response.text()

                t1 = time.monotonic()
                response_time = t1 - t0

                match = bool(compiled_regex.search(text)) if compiled_regex else None

                async with pool.connection() as conn:
                    await conn.execute(
                        """
                        INSERT INTO website_metrics
                        (url, checked_at, status_code, response_time, regex_match)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            str(monitored_url.url),
                            start_time,
                            status,
                            response_time,
                            match,
                        ),
                    )

                logger.info(
                    f"[{start_time}] {monitored_url.url} | Status: {status} | Match: {match} | Time: {response_time:.3f}s"
                )

            except Exception as e:
                logger.error(f"[{start_time}] Error checking {monitored_url.url}: {e}")

            elapsed = time.monotonic() - t0
            await asyncio.sleep(max(0, monitored_url.interval - elapsed))

    except asyncio.CancelledError:
        logger.info(f"Website check for {monitored_url.url} cancelled.")
        raise
