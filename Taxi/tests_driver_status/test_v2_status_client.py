# pylint: disable=import-only-modules
import datetime
import json

import pytest

from tests_driver_status.enum_constants import DriverStatus
from tests_driver_status.enum_constants import OrderStatus
import tests_driver_status.fallback_queue as fallback_queue
import tests_driver_status.pg_helpers as pg_helpers
import tests_driver_status.utils as utils


SOME_ORDER = 'order_001'
SOME_PROVIDER = 1024


async def _post_status(
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        order_id=None,
        expected_code=200,
):
    body = {'target_status': status}

    if order_id is not None:
        body['order'] = order_id

    response = await taxi_driver_status.post(
        'v2/status/client',
        headers={
            'X-YaTaxi-Park-Id': park_id,
            'X-YaTaxi-Driver-Profile-Id': driver_id,
            'X-Request-Application-Version': '9.40',
            'X-Request-Version-Type': '',  # '' for taximeter
            'X-Request-Platform': 'android',
        },
        data=json.dumps(body),
    )
    assert response.status_code == expected_code


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'status,expected_code',
    [
        pytest.param('free', 200, id='single status insert free'),
        pytest.param('busy', 200, id='single status insert busy'),
        pytest.param('offline', 200, id='single status insert offline'),
        pytest.param('unknown', 400, id='single status insert unknown'),
    ],
)
async def test_status_insert(
        taxi_driver_status,
        pgsql,
        mocked_time,
        status,
        expected_code,
        taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'

    await _post_status(
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        expected_code=expected_code,
    )

    if expected_code == 200:
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_statuses_table(
            pgsql, driver_record_id, status, 'client', mocked_time.now(),
        )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'status,call_ts',
    [
        pytest.param(
            'free', '2021-05-17 00:01:07.0+00', id='single status insert free',
        ),
        pytest.param(
            'busy', '2021-05-17 00:01:08.0+00', id='single status insert busy',
        ),
        pytest.param(
            'offline',
            '2021-05-17 00:01:09.0+00',
            id='single status insert offline',
        ),
    ],
)
async def test_fallback_store(
        taxi_driver_status,
        pgsql,
        mocked_time,
        status,
        taxi_config,
        redis_store,
        testpoint,
        call_ts,
):
    # clear redis storage from the previous tests
    fallback_queue.clear(redis_store, fallback_queue.STATUS_EVENT_QUEUE)

    # set call timestamp
    expected_updated_ts = utils.parse_date_str(call_ts)
    mocked_time.set(expected_updated_ts)
    await taxi_driver_status.invalidate_caches(clean_update=True)

    park_id = 'parkid000'
    driver_id = 'driverid000'

    # inject persistet storage failure
    @testpoint('persistent_storage_store_tp')
    def _inject_failure_tp(data):
        return {'inject_failure': True}

    await _post_status(taxi_driver_status, park_id, driver_id, status)

    expected_event = {
        (driver_id, park_id): {
            'statuses': {
                utils.date_to_ms(
                    expected_updated_ts,
                ): DriverStatus.from_legacy(status),
            },
        },
    }

    result = fallback_queue.read_events(
        redis_store, fallback_queue.STATUS_EVENT_QUEUE,
    )
    assert expected_event == fallback_queue.to_comparable_status_repr(result)


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_status_insert_multi(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'
    statuses = ['free', 'busy', 'offline', 'free']

    for status in statuses:
        await _post_status(taxi_driver_status, park_id, driver_id, status)
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_statuses_table(
            pgsql, driver_record_id, status, 'client', mocked_time.now(),
        )
        mocked_time.sleep(0.001)


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_status_request_order(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'

    now = mocked_time.now()
    past = now - datetime.timedelta(seconds=1)
    future = now + datetime.timedelta(seconds=1)

    status1 = 'free'
    await _post_status(taxi_driver_status, park_id, driver_id, status1)
    driver_record_id = pg_helpers.check_drivers_table(
        pgsql, park_id, driver_id,
    )
    pg_helpers.check_statuses_table(
        pgsql, driver_record_id, status1, 'client', now,
    )

    mocked_time.set(past)
    status2 = 'busy'
    await _post_status(taxi_driver_status, park_id, driver_id, status2)
    pg_helpers.check_statuses_table(
        pgsql, driver_record_id, status1, 'client', now,
    )

    mocked_time.set(future)
    status3 = 'offline'
    await _post_status(taxi_driver_status, park_id, driver_id, status3)
    pg_helpers.check_statuses_table(
        pgsql, driver_record_id, status3, 'client', future,
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_order_insert(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'
    status = 'free'
    order_id = 'order_id_000'
    default_order_provider = 0

    await _post_status(
        taxi_driver_status, park_id, driver_id, status, order_id,
    )

    driver_record_id = pg_helpers.check_drivers_table(
        pgsql, park_id, driver_id,
    )

    pg_helpers.check_orders_table(
        pgsql,
        order_id,
        driver_record_id,
        OrderStatus.kDriving,
        default_order_provider,
        mocked_time.now(),
    )


@pytest.mark.redis_store(
    [
        'hset',
        'Order:SetCar:Items:Providers:parkid000',
        SOME_ORDER,
        SOME_PROVIDER,
    ],
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_order_insert_redis(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'
    status = 'free'

    await _post_status(
        taxi_driver_status, park_id, driver_id, status, SOME_ORDER,
    )

    driver_record_id = pg_helpers.check_drivers_table(
        pgsql, park_id, driver_id,
    )

    pg_helpers.check_orders_table(
        pgsql,
        SOME_ORDER,
        driver_record_id,
        OrderStatus.kDriving,
        SOME_PROVIDER,
        mocked_time.now(),
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_order_insert_multi_orders(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'
    status = 'free'
    order_id1 = 'order_id_000'
    order_id2 = 'order_id_001'
    order_id3 = 'order_id_002'
    order_provider = 0

    # insert 1st order
    await _post_status(
        taxi_driver_status, park_id, driver_id, status, order_id1,
    )
    driver_record_id = pg_helpers.check_drivers_table(
        pgsql, park_id, driver_id,
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id1,
        driver_record_id,
        OrderStatus.kDriving,
        order_provider,
        mocked_time.now(),
    )

    # insert 2nd order, 1st is going to have status 'complete'
    mocked_time.sleep(1)
    await _post_status(
        taxi_driver_status, park_id, driver_id, status, order_id2,
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id1,
        driver_record_id,
        OrderStatus.kComplete,
        order_provider,
        mocked_time.now(),
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id2,
        driver_record_id,
        OrderStatus.kDriving,
        order_provider,
        mocked_time.now(),
    )

    # update 1st order, 2nd is going to have status 'complete'
    mocked_time.sleep(1)
    await _post_status(
        taxi_driver_status, park_id, driver_id, status, order_id1,
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id1,
        driver_record_id,
        OrderStatus.kDriving,
        order_provider,
        mocked_time.now(),
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id2,
        driver_record_id,
        OrderStatus.kComplete,
        order_provider,
        mocked_time.now(),
    )
    tp_finished2 = mocked_time.now()

    # insert 3rd order, 1st and 2nd should have status 'complete'
    # but 2nd already had, timestamp should not be updated
    mocked_time.sleep(1)
    await _post_status(
        taxi_driver_status, park_id, driver_id, status, order_id3,
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id1,
        driver_record_id,
        'complete',
        order_provider,
        mocked_time.now(),
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id2,
        driver_record_id,
        OrderStatus.kComplete,
        order_provider,
        tp_finished2,
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id3,
        driver_record_id,
        OrderStatus.kDriving,
        order_provider,
        mocked_time.now(),
    )
    tp_finished1 = mocked_time.now()

    # set driver offline, all orders should have status 'complete'
    # but 1st and 2nd already had, timestamp should not be updated
    mocked_time.sleep(1)
    await _post_status(taxi_driver_status, park_id, driver_id, 'offline')
    pg_helpers.check_orders_table(
        pgsql,
        order_id1,
        driver_record_id,
        'complete',
        order_provider,
        tp_finished1,
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id2,
        driver_record_id,
        'complete',
        order_provider,
        tp_finished2,
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id3,
        driver_record_id,
        'complete',
        order_provider,
        mocked_time.now(),
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_order_request_order(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'
    status = 'free'
    active_order_id = 'order_id_000'
    inactive_order_id = 'order_id_001'
    default_order_provider = 0

    now = mocked_time.now()
    just_before_now = now - datetime.timedelta(seconds=0.001)
    past = now - datetime.timedelta(seconds=1)
    future = now + datetime.timedelta(seconds=1)

    mocked_time.set(just_before_now)
    await _post_status(
        taxi_driver_status, park_id, driver_id, status, inactive_order_id,
    )
    mocked_time.set(now)
    await _post_status(
        taxi_driver_status, park_id, driver_id, status, active_order_id,
    )
    driver_record_id = pg_helpers.check_drivers_table(
        pgsql, park_id, driver_id,
    )
    pg_helpers.check_orders_table(
        pgsql,
        active_order_id,
        driver_record_id,
        OrderStatus.kDriving,
        default_order_provider,
        now,
    )
    pg_helpers.check_orders_table(
        pgsql,
        inactive_order_id,
        driver_record_id,
        OrderStatus.kComplete,
        default_order_provider,
        now,
    )

    # request "from the past" doesn't change orders state
    mocked_time.set(past)
    await _post_status(
        taxi_driver_status, park_id, driver_id, status, active_order_id,
    )
    pg_helpers.check_orders_table(
        pgsql,
        active_order_id,
        driver_record_id,
        OrderStatus.kDriving,
        default_order_provider,
        now,
    )
    pg_helpers.check_orders_table(
        pgsql,
        inactive_order_id,
        driver_record_id,
        OrderStatus.kComplete,
        default_order_provider,
        now,
    )

    # future request doesn't update already finished orders
    mocked_time.set(future)
    await _post_status(
        taxi_driver_status, park_id, driver_id, status, active_order_id,
    )
    pg_helpers.check_orders_table(
        pgsql,
        active_order_id,
        driver_record_id,
        OrderStatus.kDriving,
        default_order_provider,
        future,
    )
    pg_helpers.check_orders_table(
        pgsql,
        inactive_order_id,
        driver_record_id,
        OrderStatus.kComplete,
        default_order_provider,
        now,
    )
