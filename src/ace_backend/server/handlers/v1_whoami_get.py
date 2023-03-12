import dataclasses
import datetime as dt
from typing import Optional
import uuid

from aiohttp import web
import aiohttp_session

from ace_backend.sync import message as message_module


SYNC_TTL_S = 600


@dataclasses.dataclass(frozen=True)
class Response:
    user_id: Optional[str]
    sync_message: Optional[str]
    avatar: Optional[str]


def _set_sync_message(session: aiohttp_session.Session) -> None:
    session['user_id_sync'][
        'sync_message'
    ] = f'%%technical message for tuzach in/net user_id sync: {uuid.uuid4().hex}%%'
    session.changed()


def _set_user_id(session: aiohttp_session.Session, user_id: str) -> None:
    session['user_id'] = user_id
    session['user_id_sync']['last_sync_timestamp'] = dt.datetime.now().timestamp()
    del session['user_id_sync']['sync_message']


async def _is_sync_needed(
    request: web.Request, session: aiohttp_session.Session
) -> bool:
    if 'user_id' not in session:
        return True

    now = dt.datetime.now()
    last_sync_timestamp = dt.datetime.fromtimestamp(
        session['user_id_sync']['last_sync_timestamp']
    )
    if (now - last_sync_timestamp).total_seconds() < SYNC_TTL_S:
        return False

    rows = await request.app['pool'].fetch(
        '''
        SELECT sm.user_id AS user_id
        FROM sync.message AS sm
        INNER JOIN ace.message AS am
            ON sm.text = am.text AND sm.time > am.created_at - INTERVAL '5 MINUTES'
        WHERE am.id = (
            SELECT id
            FROM ace.message
            WHERE ace_session_id = $1 AND created_at < NOW() - INTERVAL '1 MINUTE'
            ORDER BY created_at DESC
            LIMIT 1
        )
        ''',
        session.identity,
    )
    user_ids = [row['user_id'] for row in rows]

    return bool(user_ids) and session['user_id'] not in user_ids


async def _do_sync(request: web.Request, session: aiohttp_session.Session) -> None:
    pg_pool = request.app['pool']
    await message_module.do_sync(pg_pool, request.app['client_session'])

    user_id = await pg_pool.fetchval(
        '''
        SELECT user_id
        FROM sync.message
        WHERE text = $1
        ORDER BY time
        LIMIT 1
        ''',
        session['user_id_sync']['sync_message'],
    )

    if user_id is not None:
        _set_user_id(session, user_id)

        return

    _set_sync_message(session)


async def handle(request: web.Request) -> web.Response:
    session = await aiohttp_session.get_session(request)

    if 'user_id_sync' not in session:
        session['user_id_sync'] = {}

    if 'sync_message' in session['user_id_sync']:
        await _do_sync(request, session)
    elif await _is_sync_needed(request, session):
        _set_sync_message(session)

    return web.json_response(
        dataclasses.asdict(
            Response(
                user_id=session.get('user_id'),
                sync_message=session['user_id_sync'].get('sync_message'),
                avatar=None,
            )
        )
    )
