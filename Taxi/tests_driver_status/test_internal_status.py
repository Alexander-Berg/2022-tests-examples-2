import datetime
import json

import pytest

# pylint: disable=import-only-modules
from tests_driver_status.enum_constants import OrderStatus
# pylint: enable=import-only-modules
import tests_driver_status.pg_helpers as pg_helpers


SOME_ORDER = 'order_id_000'
SOME_PROVIDER = 1024


async def _post_status(
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        order_id=None,
        order_provider=None,
        expected_code=200,
):
    body = {'park_id': park_id, 'driver_id': driver_id, 'status': status}

    if order_id is not None:
        body['order_id'] = order_id
    if order_provider is not None:
        body['order_provider'] = order_provider

    response = await taxi_driver_status.post(
        'v1/internal/status', data=json.dumps(body),
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
            pgsql, driver_record_id, status, 'service', mocked_time.now(),
        )


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
            pgsql, driver_record_id, status, 'service', mocked_time.now(),
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
        pgsql, driver_record_id, status1, 'service', now,
    )

    mocked_time.set(past)
    status2 = 'busy'
    await _post_status(taxi_driver_status, park_id, driver_id, status2)
    pg_helpers.check_statuses_table(
        pgsql, driver_record_id, status1, 'service', now,
    )

    mocked_time.set(future)
    status3 = 'offline'
    await _post_status(taxi_driver_status, park_id, driver_id, status3)
    pg_helpers.check_statuses_table(
        pgsql, driver_record_id, status3, 'service', future,
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'order_provider',
    [
        pytest.param(0, id='single order insert, provider=unknown'),
        pytest.param(1, id='single order insert, provider=park'),
        pytest.param(2, id='single order insert, provider=yandex'),
        pytest.param(16, id='single order insert, provider=upup'),
        pytest.param(128, id='single order insert, provider=formula'),
        pytest.param(1024, id='single order insert, provider=offtaxi'),
        pytest.param(524288, id='single order insert, provider=app'),
        pytest.param(
            100500,
            id='single order insert, provider=<not existing> '
            '(treated as unknown)',
        ),
    ],
)
async def test_order_insert(
        taxi_driver_status, pgsql, mocked_time, order_provider, taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'
    status = 'free'
    order_id = 'order_id_000'

    await _post_status(
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        order_id,
        order_provider,
    )

    driver_record_id = pg_helpers.check_drivers_table(
        pgsql, park_id, driver_id,
    )

    pg_helpers.check_orders_table(
        pgsql,
        order_id,
        driver_record_id,
        OrderStatus.kDriving,
        order_provider,
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
async def test_order_insert_multi_providers(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'
    status = 'free'
    order_id = 'order_id_000'
    order_providers = [0, 1, 2, 16, 128, 1024, 524288]

    for order_provider in order_providers:
        await _post_status(
            taxi_driver_status,
            park_id,
            driver_id,
            status,
            order_id,
            order_provider,
        )

        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_orders_table(
            pgsql,
            order_id,
            driver_record_id,
            OrderStatus.kDriving,
            order_provider,
            mocked_time.now(),
        )
        mocked_time.sleep(0.001)


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_order_insert_multi_orders(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'
    status = 'free'
    order_provider = 0
    order_id1 = 'order_id_000'
    order_id2 = 'order_id_001'
    order_id3 = 'order_id_002'

    # insert 1st order
    await _post_status(
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        order_id1,
        order_provider,
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
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        order_id2,
        order_provider,
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
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        order_id1,
        order_provider,
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
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        order_id3,
        order_provider,
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
        OrderStatus.kComplete,
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
    order_id = 'order_id_000'

    now = mocked_time.now()
    past = now - datetime.timedelta(seconds=1)
    future = now + datetime.timedelta(seconds=1)

    order_provider1 = 0
    await _post_status(
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        order_id,
        order_provider1,
    )
    driver_record_id = pg_helpers.check_drivers_table(
        pgsql, park_id, driver_id,
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id,
        driver_record_id,
        OrderStatus.kDriving,
        order_provider1,
        now,
    )

    mocked_time.set(past)
    order_provider2 = 1
    await _post_status(
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        order_id,
        order_provider2,
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id,
        driver_record_id,
        OrderStatus.kDriving,
        order_provider1,
        now,
    )

    mocked_time.set(future)
    order_provider3 = 2
    await _post_status(
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        order_id,
        order_provider3,
    )
    pg_helpers.check_orders_table(
        pgsql,
        order_id,
        driver_record_id,
        OrderStatus.kDriving,
        order_provider3,
        future,
    )
