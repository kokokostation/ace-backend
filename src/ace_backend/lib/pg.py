import os

import asyncpg


async def get_connection_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        user='ace',
        password='ace',
        database='ace',
        host=os.environ.get('ACE_PG_HOST') or 'pg',
    )
