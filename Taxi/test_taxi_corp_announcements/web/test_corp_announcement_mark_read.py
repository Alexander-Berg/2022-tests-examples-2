import pytest

from taxi_corp_announcements.internal import base_context

ANNOUNCEMENT_ID = '12345'
YANDEX_UID = '56789'
CLIENT_ID = 'client_id'
READ_STATUS = 'read'

PARAMS = {
    'announcement_id': ANNOUNCEMENT_ID,
    'yandex_uid': YANDEX_UID,
    'client_id': CLIENT_ID,
}


async def fetch_user_announcement_status(
        ctx: base_context.Web,
        announcement_id: str,
        client_id: str,
        yandex_uid: str,
):
    query = ctx.generated.postgres_queries[
        'fetch_announcement_read_status.sql'
    ]
    master_pool = ctx.generated.pg.master[0]
    with ctx.time_scope('fetch_announcement_status'):
        async with master_pool.acquire(log_extra={}) as conn:
            announcement_record = await conn.fetchrow(
                query, *(announcement_id, client_id, yandex_uid),
            )
    if not announcement_record:
        return None
    announcement = dict(announcement_record)

    return announcement['status']


@pytest.mark.pgsql(
    'corp_announcements',
    files=('announcements.sql', 'clients_announcements.sql'),
)
async def test_corp_announcement_mark_read(web_app_client, web_context):
    response = await web_app_client.post(
        '/v1/announcement/mark_read', params=PARAMS,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    ctx = base_context.Web(web_context, 'fetch_announcement_by_id')

    announcement_status = await fetch_user_announcement_status(
        ctx, ANNOUNCEMENT_ID, CLIENT_ID, YANDEX_UID,
    )
    assert announcement_status == READ_STATUS


async def test_corp_announcement_mark_read_fail(web_app_client):
    response = await web_app_client.post(
        '/v1/announcement/mark_read', params=PARAMS,
    )
    assert response.status == 404
    content = await response.json()
    assert content == {
        'code': 'invalid-input',
        'details': {},
        'message': 'announcement not found',
        'status': 'error',
    }
