import pytest

from taxi_corp_announcements.internal import base_context

ANNOUNCEMENT_ID = '12345'


async def fetch_announcements_records(ctx):
    query = ctx.generated.postgres_queries['fetch_announcements_records.sql']
    slave_pool = ctx.generated.pg.slave[0]
    async with slave_pool.acquire(log_extra={}) as conn:
        announcement_records = await conn.fetch(query)

    return [
        dict(announcement_record)
        for announcement_record in announcement_records
    ]


@pytest.mark.pgsql(
    'corp_announcements',
    files=('announcements.sql', 'clients_announcements.sql'),
)
async def test_set_announcements(web_context, web_app_client):
    response = await web_app_client.post(
        '/v1/clients/announcements',
        json=[
            {
                'announcement_id': ANNOUNCEMENT_ID,
                'client_id': 'client1_id',
                'action': 'set',
            },
        ],
    )
    assert response.status == 200

    ctx = base_context.Web(web_context, 'fetch_announcement_by_id')

    records = await fetch_announcements_records(ctx)

    assert len(records) == 3


@pytest.mark.pgsql(
    'corp_announcements',
    files=('announcements.sql', 'clients_announcements.sql'),
)
async def test_delete_announcements(web_context, web_app_client):
    response = await web_app_client.post(
        '/v1/clients/announcements',
        json=[
            {
                'announcement_id': ANNOUNCEMENT_ID,
                'client_id': 'client2_id',
                'action': 'delete',
            },
            {
                'announcement_id': ANNOUNCEMENT_ID,
                'client_id': 'client3_id',
                'action': 'delete',
            },
        ],
    )
    assert response.status == 200

    ctx = base_context.Web(web_context, 'fetch_announcement_by_id')

    records = await fetch_announcements_records(ctx)

    assert not records
