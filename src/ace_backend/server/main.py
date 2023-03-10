import logging

import aiohttp
from aiohttp import web
import aiohttp_cors
import aiohttp_session
import aiohttp_session.redis_storage

from ace_backend.lib import pg
from ace_backend.lib import redis
from ace_backend.server.handlers import v1_message_list_get
from ace_backend.server.handlers import v1_message_post
from ace_backend.server.handlers import v1_topic_get
from ace_backend.server.handlers import v1_whoami_get


logging.basicConfig(level=logging.DEBUG)


async def init_app():
    app = web.Application()

    app['pool'] = await pg.get_connection_pool()
    app['client_session'] = aiohttp.ClientSession(raise_for_status=True)

    app.add_routes(
        [
            web.get('/v1/message/list', v1_message_list_get.handle),
            web.post('/v1/message', v1_message_post.handle),
            web.get('/v1/whoami', v1_whoami_get.handle),
            web.get('/v1/topic', v1_topic_get.handle),
        ]
    )

    cors = aiohttp_cors.setup(
        app,
        defaults={
            'http://localhost:3000': aiohttp_cors.ResourceOptions(
                allow_credentials=True, expose_headers="*", allow_headers="*"
            )
        },
    )

    for route in list(app.router.routes()):
        cors.add(route)

    storage = aiohttp_session.redis_storage.RedisStorage(
        await redis.get_connection(),
        cookie_name='ace_session',
        max_age=86400 * 30,
        secure=True,
    )
    aiohttp_session.setup(app, storage)

    return app


def main():
    web.run_app(init_app())


if __name__ == '__main__':
    main()
