# pylint: disable=redefined-outer-name
import decimal

from aiohttp import web
import pytest

from taxi_corp_announcements.api.common import announcements_helper as helper
from taxi_corp_announcements.generated.cron import run_cron
from taxi_corp_announcements.internal import base_context

ANNOUNCEMENT_ID = '23456'
APPROVER_ID = decimal.Decimal('56789')


async def fetch_announcements_records(ctx):
    query = ctx.generated.postgres_queries['fetch_announcements_records.sql']
    slave_pool = ctx.generated.pg.slave[0]
    async with slave_pool.acquire(log_extra={}) as conn:
        announcement_records = await conn.fetch(query)

    return [
        dict(announcement_record)
        for announcement_record in announcement_records
    ]


@pytest.mark.pgsql('corp_announcements', files=('announcements.sql',))
async def test_set_announcements_to_clients(stq3_context, mockserver):
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

    await run_cron.main(
        [
            'taxi_corp_announcements.crontasks.set_announcements_to_managers',
            '-t',
            '0',
        ],
    )

    ctx = base_context.Stq(stq3_context, 'fetch_announcements_records')
    records = await fetch_announcements_records(ctx)
    assert len(records) == 4
    for record in records:
        assert record['client_id'] in ['client1_id', 'client2_id']
        if record['client_id'] == 'client1_id':
            assert record['user_yandex_uid'] in [
                decimal.Decimal('234567'),
                decimal.Decimal('345678'),
            ]
        else:
            assert record['user_yandex_uid'] in [
                decimal.Decimal('456789'),
                decimal.Decimal('567890'),
            ]
        assert record['announcement_id'] == ANNOUNCEMENT_ID
        assert record['status'] == 'not_read'
        assert record['updated_at']

    announcement = await helper.fetch_announcement_by_id(ctx, ANNOUNCEMENT_ID)
    assert announcement['status'] == 'approved'
    assert announcement['approved_by'] == APPROVER_ID
