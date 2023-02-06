import datetime
from typing import List

import pytest

from iiko_integration.generated.cron import run_cron


@pytest.mark.parametrize(
    ('iterations_count', 'sleep_interval'),
    (
        pytest.param(
            3,
            2,
            marks=pytest.mark.config(
                IIKO_INTEGRATION_ORDER_STATUS_POLLING_DELAY=2,
                IIKO_INTEGRATION_PROACTIVE_EXPIRATION_TIME=20,
                IIKO_INTEGRATION_CRON_SETTINGS={
                    '__default__': {
                        'max_duration_s': 300,
                        'run_interval_s': 30,
                    },
                    'check_external_activity': {
                        'max_duration_s': 17,
                        'run_interval_s': 6,
                    },
                },
            ),
        ),
        pytest.param(
            2,
            1,
            marks=pytest.mark.config(
                IIKO_INTEGRATION_ORDER_STATUS_POLLING_DELAY=2,
                IIKO_INTEGRATION_PROACTIVE_EXPIRATION_TIME=10,
                IIKO_INTEGRATION_CRON_SETTINGS={
                    '__default__': {'max_duration_s': 8, 'run_interval_s': 2},
                },
            ),
        ),
    ),
)
async def test_iterations(iterations_count: int, sleep_interval: int, patch):

    delta = datetime.timedelta(seconds=0)
    iteration = 1

    # we have 5 _now() calls per 1 iteration
    @patch('iiko_integration.utils.cron_loop._now')
    def _mock_now():
        nonlocal delta
        delta += datetime.timedelta(seconds=1)
        return datetime.datetime(2020, 1, 1, 0, 0, 20) + delta

    @patch('iiko_integration.utils.cron_loop._sleep')
    async def _mock_sleep(interval: int):
        assert interval == sleep_interval
        nonlocal delta
        nonlocal iteration
        delta += datetime.timedelta(seconds=interval)
        iteration += 1

    await run_cron.main(
        ['iiko_integration.crontasks.check_external_activity', '-t', '0'],
    )

    assert iteration == iterations_count


@pytest.mark.parametrize(
    'expired_orders',
    (
        pytest.param(
            [],
            marks=pytest.mark.config(
                IIKO_INTEGRATION_ORDER_STATUS_POLLING_DELAY=2,
                IIKO_INTEGRATION_PROACTIVE_EXPIRATION_TIME=20,
                IIKO_INTEGRATION_CRON_SETTINGS={
                    '__default__': {'max_duration_s': 3, 'run_interval_s': 2},
                },
            ),
        ),
        pytest.param(
            ['1'],
            marks=pytest.mark.config(
                IIKO_INTEGRATION_ORDER_STATUS_POLLING_DELAY=3,
                IIKO_INTEGRATION_PROACTIVE_EXPIRATION_TIME=2,
                IIKO_INTEGRATION_CRON_SETTINGS={
                    '__default__': {'max_duration_s': 3, 'run_interval_s': 2},
                },
            ),
        ),
        pytest.param(
            ['1', '2'],
            marks=pytest.mark.config(
                IIKO_INTEGRATION_ORDER_STATUS_POLLING_DELAY=1,
                IIKO_INTEGRATION_PROACTIVE_EXPIRATION_TIME=2,
                IIKO_INTEGRATION_CRON_SETTINGS={
                    '__default__': {'max_duration_s': 3, 'run_interval_s': 2},
                },
            ),
        ),
    ),
)
async def test_expiration(expired_orders: List[str], get_db_item, patch):
    delta = datetime.timedelta(seconds=0)

    all_orders = ['1', '2']
    all_activities = dict()

    for order_id in all_orders:
        order = await get_db_item(
            table_name='iiko_integration.external_activity',
            fields=['last_activity_at'],
            order_id=order_id,
        )
        all_activities[order_id] = order['last_activity_at']

    # we have 5 _now() calls per 1 iteration
    @patch('iiko_integration.utils.cron_loop._now')
    def _mock_now():
        return datetime.datetime(2020, 1, 1, 0, 0, 0) + delta

    @patch('iiko_integration.utils.cron_loop._sleep')
    async def _mock_sleep(interval: int):
        nonlocal delta
        delta += datetime.timedelta(seconds=interval)

    await run_cron.main(
        ['iiko_integration.crontasks.check_external_activity', '-t', '0'],
    )

    for order_id, last_activity_at in all_activities.items():
        activity = await get_db_item(
            table_name='iiko_integration.external_activity',
            fields=['last_activity_at'],
            order_id=order_id,
        )
        order = await get_db_item(
            table_name='iiko_integration.orders',
            fields=['status'],
            id=order_id,
        )

        if order_id in expired_orders:
            assert not activity
            assert order['status']['restaurant_status'] == 'EXPIRED'
        else:
            assert activity['last_activity_at'] == last_activity_at
            assert order['status']['restaurant_status'] != 'EXPIRED'


@pytest.mark.config(
    IIKO_INTEGRATION_ORDER_STATUS_POLLING_DELAY=1,
    IIKO_INTEGRATION_PROACTIVE_EXPIRATION_TIME=2,
    IIKO_INTEGRATION_CRON_SETTINGS={
        '__default__': {'max_duration_s': 3, 'run_interval_s': 2},
    },
)
async def test_reset(get_db_item, patch):
    delta = datetime.timedelta(seconds=0)

    all_orders = ['1', '2']
    all_activities = dict()

    for order_id in all_orders:
        order = await get_db_item(
            table_name='iiko_integration.external_activity',
            fields=['last_activity_at'],
            order_id=order_id,
        )
        all_activities[order_id] = order['last_activity_at']

    @patch('iiko_integration.utils.cron_loop._now')
    def _mock_now():
        return datetime.datetime(2020, 1, 1, 0, 0, 15) + delta

    @patch('iiko_integration.utils.cron_loop._sleep')
    async def _mock_sleep(interval: int):
        nonlocal delta
        delta += datetime.timedelta(seconds=interval)

    await run_cron.main(
        ['iiko_integration.crontasks.check_external_activity', '-t', '0'],
    )

    for order_id, last_activity_at in all_activities.items():
        activity = await get_db_item(
            table_name='iiko_integration.external_activity',
            fields=['last_activity_at'],
            order_id=order_id,
        )
        order = await get_db_item(
            table_name='iiko_integration.orders',
            fields=['status'],
            id=order_id,
        )

        assert activity['last_activity_at'] != last_activity_at
        assert order['status']['restaurant_status'] != 'EXPIRED'
