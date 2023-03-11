import os

from redis import asyncio as aioredis


async def get_connection() -> aioredis.Redis:
    redis_host = os.environ.get('ACE_REDIS_HOST') or 'redis'

    return await aioredis.from_url(f'redis://{redis_host}:6379')
