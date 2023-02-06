import asyncio

import pytest

from taxi.maintenance import run
from taxi.util import dates

from rida.crontasks import expire_push_notifications


@pytest.mark.translations(
    rida={
        'notifications.driver.new_offer_push_expired.title': {
            'en': 'This offer has expired',
        },
    },
)
@pytest.mark.config(
    RIDA_NOTIFICATION_OVERRIDES={
        'new_offer_push_expired': {
            'is_enabled': True,
            'android': {'min_build_number': 200111},
            'iphone': {'min_build_number': 200500},
        },
    },
)
async def test_expire_push_notifications(
        cron_context, loop, validate_cron_sent_notifications,
):
    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )
    loop = asyncio.get_event_loop()
    await expire_push_notifications.do_stuff(stuff_context, loop)
    validate_cron_sent_notifications(
        expected_notifications=[
            {
                'id': '00000000000000000000000000000001',
                'firebase_token': 'firebase_token',
                'title': 'This offer has expired',
            },
            {
                'id': '00000000000000000000000000000003',
                'firebase_token': 'firebase_token',
                'data': {
                    'push_type': 666,
                    'push_id': '00000000000000000000000000000003',
                },
            },
            {
                'id': '00000000000000000000000000000004',
                'firebase_token': 'firebase_token',
                'data': {
                    'push_type': 666,
                    'push_id': '00000000000000000000000000000004',
                },
                'wake_application': True,
            },
        ],
    )
    async with cron_context.pg.ro_pool.acquire() as conn:
        records = await conn.fetch('SELECT * FROM push_notifications;')
        assert len(records) == 1


@pytest.mark.pgsql('rida', files=['pg_rida_empty.sql'])
async def test_empty_db(cron_context, loop, validate_cron_sent_notifications):
    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )
    loop = asyncio.get_event_loop()
    await expire_push_notifications.do_stuff(stuff_context, loop)
    validate_cron_sent_notifications(expected_times_called=0)
    async with cron_context.pg.ro_pool.acquire() as conn:
        records = await conn.fetch('SELECT * FROM push_notifications;')
        assert len(records) == 1


@pytest.mark.translations(
    rida={
        'notifications.driver.new_offer_push_expired.title': {
            'en': 'This offer has expired',
        },
    },
)
@pytest.mark.pgsql('rida', files=['pg_rida_big_batch.sql'])
async def test_big_batch(cron_context, loop, validate_cron_sent_notifications):
    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )
    loop = asyncio.get_event_loop()
    await expire_push_notifications.do_stuff(stuff_context, loop)
    validate_cron_sent_notifications(expected_total_notifications=69)
    async with cron_context.pg.ro_pool.acquire() as conn:
        records = await conn.fetch('SELECT * FROM push_notifications;')
        assert len(records) == 0  # pylint: disable=len-as-condition
