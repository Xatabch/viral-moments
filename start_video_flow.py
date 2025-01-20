from content_update_server.techcrunch import fetch_and_compare
import asyncio

async def async_wrapper():
    await fetch_and_compare()

asyncio.run(async_wrapper())