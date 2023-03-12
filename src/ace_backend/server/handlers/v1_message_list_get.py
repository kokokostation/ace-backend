import dataclasses
from typing import List
from typing import Optional

from aiohttp import web
import aiohttp_session

from ace_backend.sync import message as message_module


@dataclasses.dataclass(frozen=True)
class Picture:
    name: str
    imgurl: str
    thumburl: str
    filedata: str
    imgw: str
    imgh: str
    thumbw: str
    thumbh: str


@dataclasses.dataclass(frozen=True)
class Message:
    id: str
    type: str
    time: str
    text: str
    user_id: str
    avatar: Optional[str]
    picture: Optional[Picture]


@dataclasses.dataclass(frozen=True)
class Response:
    data: List[Message]
    user_count: int


async def _get_messages(request: web.Request, last: int) -> List[Message]:
    rows = await request.app['pool'].fetch(
        '''
        SELECT 
            m.external_id AS m_external_id,
            m.type AS m_type,
            m.time AS m_time,
            m.text AS m_text,
            m.user_id AS m_user_id,
            m.avatar AS m_avatar,
            p.name AS p_name,
            p.imgurl AS p_imgurl,
            p.thumburl AS p_thumburl,
            p.filedata AS p_filedata,
            p.imgw AS p_imgw,
            p.imgh AS p_imgh,
            p.thumbw AS p_thumbw,
            p.thumbh AS p_thumbh
        FROM sync.message AS m
        LEFT JOIN sync.picture AS p
            ON m.picture_id = p.id
        WHERE m.external_id > $1
        ORDER BY m.external_id DESC
        LIMIT 50
    ''',
        last,
    )

    data = []
    for row in reversed(rows):
        picture = None
        if row['p_name']:
            picture = Picture(
                name=row['p_name'],
                imgurl=row['p_imgurl'],
                thumburl=row['p_thumburl'],
                filedata=row['p_filedata'],
                imgw=row['p_imgw'],
                imgh=row['p_imgh'],
                thumbw=row['p_thumbw'],
                thumbh=row['p_thumbh'],
            )

        message = Message(
            id=str(row['m_external_id']),
            type=row['m_type'],
            time=row['m_time'].isoformat(),
            text=row['m_text'],
            user_id=row['m_user_id'],
            avatar=row['m_avatar'],
            picture=picture,
        )

        data.append(message)

    return data


async def _get_user_count(
    request: web.Request, session: aiohttp_session.Session
) -> int:
    if session.identity:
        await request.app['pool'].execute(
            '''
            INSERT INTO ace.touch
                (
                    ace_session_id
                )
            VALUES
                (
                    $1
                )
            ON CONFLICT (ace_session_id) DO UPDATE
            SET last_seen_at = NOW()
        ''',
            session.identity,
        )

    return await request.app['pool'].fetchval(
        '''
        SELECT COALESCE(COUNT(DISTINCT ace_session_id), 0) AS user_count
        FROM ace.touch
        WHERE last_seen_at > NOW() - INTERVAL '1 MINUTE'
    '''
    )


async def handle(request: web.Request) -> web.Response:
    last = int(request.query['last'])
    force_sync = bool(request.query.get('force_sync'))
    session = await aiohttp_session.get_session(request)

    if force_sync:
        await message_module.do_sync(request.app['pool'], request.app['client_session'])

    data = await _get_messages(request, last)
    user_count = await _get_user_count(request, session)

    return web.json_response(
        dataclasses.asdict(Response(data=data, user_count=user_count))
    )
