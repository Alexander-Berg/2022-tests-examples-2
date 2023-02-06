import decimal

from aiohttp import web
import pytest

from taxi_corp_announcements.api.common import announcements_helper as helper
from taxi_corp_announcements.internal import base_context
from taxi_corp_announcements.stq import corp_publish_announcement_task

ANNOUNCEMENT_ID = '12345'
APPROVER_ID = decimal.Decimal('987654321')


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
    'announcement_id, client_ids, user_yandex_ids',
    [
        ('12345', ['client1_id', 'client1_id'], ['234567', '345678']),
        (
            'all_rus',
            [
                'client1_id',
                'client1_id',
                'client1_id',
                'client2_id',
                'client3_id',
            ],
            ['123456', '123457', '123458', '234567', '345678'],
        ),
        ('with_vat', ['client2_id', 'client3_id'], ['123457', '123458']),
        (
            'without_vat',
            ['client1_id', 'client1_id', 'client1_id'],
            ['123456', '234567', '345678'],
        ),
    ],
)
async def test_task(
        stq3_context, mockserver, announcement_id, client_ids, user_yandex_ids,
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

    user_yandex_ids = [decimal.Decimal(x) for x in user_yandex_ids]

    await corp_publish_announcement_task.task(
        stq3_context, announcement_id, APPROVER_ID,
    )
    ctx = base_context.Stq(stq3_context, 'fetch_announcements_records')
    records = await fetch_announcements_records(ctx)

    for record in records:
        assert record['client_id'] in client_ids
        client_ids.remove(record['client_id'])
        assert record['user_yandex_uid'] in user_yandex_ids
        user_yandex_ids.remove(record['user_yandex_uid'])
        assert record['announcement_id'] == announcement_id
        assert record['status'] == 'not_read'
        assert record['updated_at']

    assert not client_ids
    assert not user_yandex_ids

    announcement = await helper.fetch_announcement_by_id(ctx, announcement_id)
    assert announcement['status'] == 'approved'
    assert announcement['approved_by'] == APPROVER_ID


async def test_task_empty(stq3_context):
    await corp_publish_announcement_task.task(
        stq3_context, ANNOUNCEMENT_ID, APPROVER_ID,
    )
    ctx = base_context.Stq(stq3_context, 'fetch_announcements_records')
    records = await fetch_announcements_records(ctx)
    assert records == []
