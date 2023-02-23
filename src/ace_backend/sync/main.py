import logging

import asyncio

from ace_backend.sync import message
from ace_backend.lib import pg


logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    pool = await pg.get_connection_pool()

    tasks = [message.sync_messages(pool)]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
