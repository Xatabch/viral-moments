from techcrunch_server.techcrunch_parser_server import post_watcher
import asyncio

if __name__ == "__main__":
    asyncio.run(post_watcher())
