from content_update_server.base import fetch_and_compare
import asyncio

from configs.video.techcrunch import config

async def async_wrapper():
    await fetch_and_compare(config)

asyncio.run(async_wrapper())