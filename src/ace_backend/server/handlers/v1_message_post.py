import dataclasses
import logging

from aiohttp import web
import aiohttp_session
import marshmallow_dataclass as mdataclasses

from ace_backend.lib import server

logger = logging.getLogger(__name__)


@mdataclasses.add_schema
@dataclasses.dataclass
class Request:
    text: str


async def handle(request: web.Request) -> web.Response:
    request_body = await server.deser_request_body(request, Request)
    session = await aiohttp_session.get_session(request)

    await request.app['pool'].execute(
        '''
        INSERT INTO ace.message
            (
                ace_session_id,
                text
            )
        VALUES
            (
                $1,
                $2
            )
    ''',
        session.identity,
        request_body.text,
    )

    return web.Response()
