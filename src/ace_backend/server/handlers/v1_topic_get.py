import dataclasses

from aiohttp import web


@dataclasses.dataclass(frozen=True)
class Response:
    topic: str


async def handle(request: web.Request) -> web.Response:
    topic = await request.app['pool'].fetchval(
        '''
        SELECT text
        FROM ace.topic
        WHERE created_at < NOW()
        ORDER BY created_at DESC
        LIMIT 1
    '''
    )

    if topic is None:
        topic = 'tuzach.in mirror'

    return web.json_response(dataclasses.asdict(Response(topic=topic)))
