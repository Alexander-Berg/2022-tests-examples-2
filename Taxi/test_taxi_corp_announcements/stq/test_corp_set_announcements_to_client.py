from aiohttp import web
import pytest

from taxi_corp_announcements.internal import base_context
from taxi_corp_announcements.stq import corp_set_announcements_to_client


async def fetch_announcements_records(ctx):
    query = ctx.generated.postgres_queries['fetch_announcements_records.sql']
    slave_pool = ctx.generated.pg.slave[0]
    with ctx.time_scope('fetch_announcements_records.sql'):
        async with slave_pool.acquire(log_extra={}) as conn:
            announcement_records = await conn.fetch(query)
    return [
        dict(announcement_record)
        for announcement_record in announcement_records
    ]


@pytest.mark.pgsql('corp_announcements', files=('announcements.sql',))
@pytest.mark.parametrize(
    'client_id, expected_announcement_ids',
    [
        ('client1_id', ['all_rus', 'without_vat']),
        ('client2_id', ['all_rus', 'with_vat']),
        ('client3_id', ['all_rus', 'with_vat']),
    ],
)
async def test_task(
        stq3_context, mockserver, client_id, expected_announcement_ids,
):
    @mockserver.json_handler('/corp-clients/v1/contracts')
    async def _request(*args, **kwargs):
        return web.json_response(
            {
                'contracts': [
                    {
                        'contract_id': 116,
                        'external_id': '116/716',
                        'billing_client_id': '12345',
                        'billing_person_id': '54321',
                        'payment_type': 'prepaid',
                        'is_offer': True,
                        'currency': 'RUB',
                        'services': ['drive', 'taxi', 'cargo', 'eats2'],
                    },
                ],
            },
        )

    await corp_set_announcements_to_client.task(stq3_context, client_id)
    ctx = base_context.Stq(stq3_context, 'fetch_announcements_records')
    records = await fetch_announcements_records(ctx)

    for record in records:
        assert record['client_id'] == client_id
        assert record['announcement_id'] in expected_announcement_ids
        expected_announcement_ids.remove(record['announcement_id'])
        assert record['status'] == 'not_read'
        assert record['updated_at']

    assert not expected_announcement_ids
