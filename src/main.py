import asyncio
import signal
import ssl

import aiohttp
import certifi

from db.connection import get_pool
from db.monitored_urls import get_monitored_urls, load_monitored_urls_from_file
from db.schema import create_tables
from monitor.checker import check_website
from utils.logger import logger

ssl_context = ssl.create_default_context(cafile=certifi.where())


async def main() -> None:
    """Run the main entry point for the application."""
    await create_tables()

    await load_monitored_urls_from_file(json_path="config.json")

    monitored_urls = await get_monitored_urls()

    if not monitored_urls:
        logger.warning("No monitored URLs found. Exiting.")
        return

    pool = await get_pool()
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context)
    ) as session:
        tasks = [
            asyncio.create_task(check_website(entry, session, pool))
            for entry in monitored_urls
        ]

        logger.info(f"Starting monitor for {len(tasks)} URL(s).")

        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)

        await stop_event.wait()

        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("Monitor shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down monitor.")
