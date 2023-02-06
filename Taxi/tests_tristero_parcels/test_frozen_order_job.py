import datetime

import pytest

TASK_NAME = 'frozen-order-periodic-job'


async def test_basic(testpoint, taxi_tristero_parcels):
    """ Test that parcels-stocks-sync working properly."""

    @testpoint(f'{TASK_NAME}-finished')
    def task_finished(arg):
        pass

    async with taxi_tristero_parcels.spawn_task(TASK_NAME):
        await task_finished.wait_call()


@pytest.mark.parametrize('enabled', [True, False])
async def test_enabled(testpoint, taxi_config, taxi_tristero_parcels, enabled):
    """ Test that parcels-stocks-sync working properly."""

    taxi_config.set_values(
        {
            'TRISTERO_PARCELS_FROZEN_ORDERS': {
                'enabled': enabled,
                'frozen-interval-days': 30,
                'job-period-hours': 24,
            },
        },
    )

    @testpoint(f'{TASK_NAME}-result')
    def task_finished(arg):
        assert arg['mode'] == enabled

    async with taxi_tristero_parcels.spawn_task(TASK_NAME):
        await task_finished.wait_call()


@pytest.mark.config(
    TRISTERO_PARCELS_FROZEN_ORDERS={
        'enabled': True,
        'frozen-interval-days': 30,
        'job-period-hours': 24,
    },
)
@pytest.mark.now('2021-06-02T02:00:00+0000')
@pytest.mark.parametrize('frozen_threshold_days', [30])
@pytest.mark.parametrize(
    'status, is_outdated, is_frozen',
    [
        ('created', True, True),
        ('created', False, False),
        ('reserved', True, True),
        ('reserved', False, False),
        ('expecting_delivery', True, True),
        ('expecting_delivery', False, False),
        ('received_partialy', True, True),
        ('received_partialy', False, False),
        ('received', True, True),
        ('received', False, False),
        ('delivered_partially', True, True),
        ('delivered_partially', False, False),
        ('delivered', True, False),
        ('delivered', False, False),
        ('cancelled', True, False),
        ('cancelled', False, False),
    ],
)
async def test_get_frozen_orders(
        testpoint,
        taxi_tristero_parcels,
        tristero_parcels_db,
        mocked_time,
        frozen_threshold_days,
        status,
        is_outdated,
        is_frozen,
):
    """
    Test orders that are not in final status and outdated (older than
    frozen_threshold_days) are returned as frozen.
    """

    with tristero_parcels_db as db:
        order = db.add_order(1, status=status)

    if is_outdated:
        upd_time = mocked_time.now() - datetime.timedelta(
            days=frozen_threshold_days + 1,
        )
    else:
        upd_time = mocked_time.now()
    order.set_updated(upd_time)

    @testpoint(f'{TASK_NAME}-result')
    def task_result(arg):
        assert is_frozen == arg['count']

    async with taxi_tristero_parcels.spawn_task(TASK_NAME):
        await task_result.wait_call()
