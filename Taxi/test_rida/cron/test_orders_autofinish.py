import asyncio
import datetime

import pytest

from taxi.maintenance import run
from taxi.util import dates

from rida.crontasks import orders_autofinish


_NOW = datetime.datetime(2020, 2, 26, 13, 50)


async def is_driver_busy(mongo, driver_guid: str) -> bool:
    driver = await mongo.rida_drivers.find_one({'guid': driver_guid})
    return driver['is_busy'] == '1'


async def get_user_trips(pg, user_guid: str) -> int:  # pylint: disable=C0103
    query = f"""
    SELECT number_of_trips
    FROM users
    WHERE guid = '{user_guid}';
    """
    async with pg.ro_pool.acquire() as conn:
        record = await conn.fetchrow(query)
    return record['number_of_trips']


async def get_driver_trips(  # pylint: disable=C0103
        pg, driver_guid: str,
) -> int:
    query = f"""
    SELECT number_of_trips
    FROM drivers
    WHERE guid = '{driver_guid}';
    """
    async with pg.ro_pool.acquire() as conn:
        record = await conn.fetchrow(query)
    return record['number_of_trips']


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    RIDA_ADJUST_SETTINGS=dict(
        rida_android=dict(
            app_token='rida_android_token',
            event_tokens=dict(
                rider_first_order_completed='rider_first_order_done',
                rider_order_completed='rider_order_done',
                driver_first_order_completed='driver_first_order_done',
                driver_order_completed='driver_order_done',
            ),
        ),
    ),
)
async def test_orders_autofinish(
        cron_context, loop, get_stats_by_label_values, stq,
):
    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )
    loop = asyncio.get_event_loop()
    await orders_autofinish.do_stuff(stuff_context, loop)
    busy_drivers = {
        '9373F48B-C6B4-4812-A2D0-413F3A000000': False,
        '9373F48B-C6B4-4812-A2D0-413F3A000001': False,
        '9373F48B-C6B4-4812-A2D0-413F3A000100': True,
        '9373F48B-C6B4-4812-A2D0-413F3A000101': True,
        '9373F48B-C6B4-4812-A2D0-413F3A000002': False,
        '9373F48B-C6B4-4812-A2D0-413F3A000003': True,
        '9373F48B-C6B4-4812-A2D0-413F3A000004': False,
        '9373F48B-C6B4-4812-A2D0-413F3A000005': True,
        '9373F48B-C6B4-4812-A2D0-413F3A000006': False,
        '9373F48B-C6B4-4812-A2D0-413F3A000007': True,
    }
    for driver_guid, expected_is_busy in busy_drivers.items():
        is_busy = await is_driver_busy(cron_context.mongo, driver_guid)
        assert is_busy == expected_is_busy, driver_guid

    number_of_trips = {
        '9373F48B-C6B4-4812-A2D0-413F3A000006': 1,
        '9373F48B-C6B4-4812-A2D0-413F3A000007': 0,
    }
    for guid, expected_trips_number in number_of_trips.items():
        user_trips = await get_user_trips(cron_context.pg, guid)
        assert user_trips == expected_trips_number, guid
        driver_trips = await get_driver_trips(cron_context.pg, guid)
        assert driver_trips == expected_trips_number, guid

    stats = get_stats_by_label_values(
        cron_context, {'sensor': 'offers.status_change'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {'sensor': 'offers.status_change', 'status': 'EXPIRED'},
            'timestamp': None,
            'value': 1,
        },
        {
            'kind': 'IGAUGE',
            'labels': {
                'sensor': 'offers.status_change',
                'status': 'UNFINISHED',
            },
            'timestamp': None,
            'value': 2,
        },
        {
            'kind': 'IGAUGE',
            'labels': {
                'sensor': 'offers.status_change',
                'status': 'AUTOCOMPLETE',
            },
            'timestamp': None,
            'value': 1,
        },
    ]

    adjust_queue = stq.rida_adjust_events
    assert adjust_queue.times_called == 4
    stq_calls_kwargs = [adjust_queue.next_call()['kwargs'] for _ in range(4)]
    stq_calls_kwargs.sort(key=lambda kwargs: kwargs['event_token'])
    assert stq_calls_kwargs[0] == {
        'application': 'rida_android',
        'app_token': 'rida_android_token',
        'user_guid': '9373F48B-C6B4-4812-A2D0-413F3A000007',
        'event_token': 'driver_first_order_done',
        'created_at': {'$date': 1582725000000},
        'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3A000006',
    }
    assert stq_calls_kwargs[1] == {
        'application': 'rida_android',
        'app_token': 'rida_android_token',
        'user_guid': '9373F48B-C6B4-4812-A2D0-413F3A000007',
        'event_token': 'driver_order_done',
        'created_at': {'$date': 1582725000000},
        'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3A000006',
    }
    assert stq_calls_kwargs[2] == {
        'application': 'rida_android',
        'app_token': 'rida_android_token',
        'user_guid': '9373F48B-C6B4-4812-A2D0-413F3A000006',
        'event_token': 'rider_first_order_done',
        'created_at': {'$date': 1582725000000},
        'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3A000006',
    }
    assert stq_calls_kwargs[3] == {
        'application': 'rida_android',
        'app_token': 'rida_android_token',
        'user_guid': '9373F48B-C6B4-4812-A2D0-413F3A000006',
        'event_token': 'rider_order_done',
        'created_at': {'$date': 1582725000000},
        'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3A000006',
    }
