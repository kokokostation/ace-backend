import logging

from aiohttp import web

from ace_backend.lib import pg
from ace_backend.server.handlers import v1_message_list_get


logging.basicConfig(level=logging.DEBUG)


async def init_app():
    app = web.Application()

    app['pool'] = await pg.get_connection_pool()

    app.add_routes(
        [
            web.get('/v1/message/list', v1_message_list_get.handle),
        ]
    )

    return app


def main():
    web.run_app(init_app())


if __name__ == '__main__':
    main()