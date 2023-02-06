import datetime
import json

import pytest

# pylint: disable=import-only-modules
from tests_driver_status.enum_constants import DriverStatus
from tests_driver_status.enum_constants import OrderStatus
# pylint: enable=import-only-modules
import tests_driver_status.fallback_queue as fallback_queue
import tests_driver_status.pg_helpers as pg_helpers
import tests_driver_status.utils as utils


def _make_request_items(
        reccount, status='free', order_id_prefix=None, order_provider=None,
):
    request = list()
    for i in range(0, reccount):
        body = {
            'driver_id': f'driverid{i}',
            'park_id': f'parkid{i}',
            'status': f'{status}',
        }

        if order_id_prefix is not None:
            body['order_id'] = f'{order_id_prefix}_{i}'
        if order_provider is not None:
            body['order_provider'] = order_provider

        request.append(body)

    return request


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_nonunique_driver_insert(taxi_driver_status, pgsql, taxi_config):
    update_drv_statuses = _make_request_items(100)
    update_drv_statuses.extend(_make_request_items(100))

    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(100):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        pg_helpers.check_drivers_table(pgsql, park_id, driver_id)


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
    update_drv_statuses = _make_request_items(100, status=status)

    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        for i in range(100):
            park_id = f'parkid{i}'
            driver_id = f'driverid{i}'
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
    statuses = ['free', 'busy', 'offline', 'free']

    for status in statuses:
        update_drv_statuses = _make_request_items(100, status=status)
        response = await taxi_driver_status.post(
            'v1/internal/status/bulk',
            data=json.dumps({'items': update_drv_statuses}),
        )
        assert response.status_code == 200

        for i in range(100):
            park_id = f'parkid{i}'
            driver_id = f'driverid{i}'
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
    now = mocked_time.now()
    past = now - datetime.timedelta(seconds=1)
    future = now + datetime.timedelta(seconds=1)

    status1 = 'free'
    update_drv_statuses = _make_request_items(100, status=status1)
    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(100):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_statuses_table(
            pgsql, driver_record_id, status1, 'service', now,
        )

    mocked_time.set(past)
    status2 = 'busy'
    update_drv_statuses = _make_request_items(100, status=status2)
    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(100):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_statuses_table(
            pgsql, driver_record_id, status1, 'service', now,
        )

    mocked_time.set(future)
    status3 = 'offline'
    update_drv_statuses = _make_request_items(100, status=status3)
    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(100):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
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
async def test_orders_insert(
        taxi_driver_status, pgsql, mocked_time, order_provider, taxi_config,
):
    order_id_prefix = 'order_id'
    update_drv_statuses = _make_request_items(
        100, order_id_prefix=order_id_prefix, order_provider=order_provider,
    )

    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(100):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        order_id = f'{order_id_prefix}_{i}'
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
    ['hset', 'Order:SetCar:Items:Providers:parkid0', 'order_id_0', 0],
    ['hset', 'Order:SetCar:Items:Providers:parkid1', 'order_id_1', 1],
    ['hset', 'Order:SetCar:Items:Providers:parkid2', 'order_id_2', 2],
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_order_insert_redis(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    order_id_prefix = 'order_id'
    update_drv_statuses = _make_request_items(
        3, order_id_prefix=order_id_prefix,
    )

    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(3):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        order_id = f'{order_id_prefix}_{i}'
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_orders_table(
            pgsql,
            order_id,
            driver_record_id,
            OrderStatus.kDriving,
            i,
            mocked_time.now(),
        )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_orders_finish_orders(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    order_id_prefix = 'order_id'
    order_provider = 0

    # insert 100 new orders
    update_drv_statuses = _make_request_items(
        100, order_id_prefix=order_id_prefix, order_provider=order_provider,
    )
    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(100):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        order_id = f'{order_id_prefix}_{i}'
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

    # finish 50 orders
    save_time_point = mocked_time.now()
    mocked_time.sleep(1)
    update_drv_statuses = _make_request_items(50)
    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(100):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        order_id = f'{order_id_prefix}_{i}'
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_orders_table(
            pgsql,
            order_id,
            driver_record_id,
            OrderStatus.kComplete if i < 50 else OrderStatus.kDriving,
            order_provider,
            mocked_time.now() if i < 50 else save_time_point,
        )

    # all drivers are going offline
    save_time_point = mocked_time.now()
    mocked_time.sleep(1)
    update_drv_statuses = _make_request_items(100, status='offline')
    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(100):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        order_id = f'{order_id_prefix}_{i}'
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_orders_table(
            pgsql,
            order_id,
            driver_record_id,
            'complete',
            order_provider,
            save_time_point if i < 50 else mocked_time.now(),
        )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_order_insert_multi_providers(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    order_id_prefix = 'order_id'
    order_providers = [0, 1, 2, 16, 128, 1024, 524288]

    for order_provider in order_providers:
        update_drv_statuses = _make_request_items(
            100,
            order_id_prefix=order_id_prefix,
            order_provider=order_provider,
        )
        response = await taxi_driver_status.post(
            'v1/internal/status/bulk',
            data=json.dumps({'items': update_drv_statuses}),
        )
        assert response.status_code == 200

        for i in range(100):
            park_id = f'parkid{i}'
            driver_id = f'driverid{i}'
            order_id = f'{order_id_prefix}_{i}'
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
    order_id_prefixes = ['oid1', 'oid2', 'oid3', 'oid4', 'oid5']
    prefixes_len = len(order_id_prefixes)
    now = mocked_time.now()
    times = [
        now,
        now + datetime.timedelta(seconds=1),
        now + datetime.timedelta(seconds=2),
        now + datetime.timedelta(seconds=3),
        now + datetime.timedelta(seconds=4),
    ]
    assert len(times) == prefixes_len

    for i in range(prefixes_len):
        mocked_time.set(times[i])
        update_drv_statuses = _make_request_items(
            100, order_id_prefix=order_id_prefixes[i], order_provider=0,
        )
        response = await taxi_driver_status.post(
            'v1/internal/status/bulk',
            data=json.dumps({'items': update_drv_statuses}),
        )
        assert response.status_code == 200

        for j in range(100):
            park_id = f'parkid{j}'
            driver_id = f'driverid{j}'
            driver_record_id = pg_helpers.check_drivers_table(
                pgsql, park_id, driver_id,
            )

            for k in range(i + 1):
                order_id = f'{order_id_prefixes[k]}_{j}'
                # current time for this and previous step
                expected_upd_ts = times[min(k + 1, i)]
                pg_helpers.check_orders_table(
                    pgsql,
                    order_id,
                    driver_record_id,
                    OrderStatus.kDriving if k == i else OrderStatus.kComplete,
                    0,
                    expected_upd_ts,
                )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_order_request_order(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    order_id_prefix = 'order_id'
    order_provider = 0

    now = mocked_time.now()
    past = now - datetime.timedelta(seconds=1)
    future = now + datetime.timedelta(seconds=1)

    update_drv_statuses = _make_request_items(
        100, order_id_prefix=order_id_prefix, order_provider=order_provider,
    )
    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(100):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        order_id = f'{order_id_prefix}_{i}'
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_orders_table(
            pgsql,
            order_id,
            driver_record_id,
            OrderStatus.kDriving,
            order_provider,
            now,
        )

    mocked_time.set(past)
    update_drv_statuses = _make_request_items(
        100, order_id_prefix=order_id_prefix, order_provider=order_provider,
    )
    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(100):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        order_id = f'{order_id_prefix}_{i}'
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_orders_table(
            pgsql,
            order_id,
            driver_record_id,
            OrderStatus.kDriving,
            order_provider,
            now,
        )

    mocked_time.set(future)
    update_drv_statuses = _make_request_items(
        100, order_id_prefix=order_id_prefix, order_provider=order_provider,
    )
    response = await taxi_driver_status.post(
        'v1/internal/status/bulk',
        data=json.dumps({'items': update_drv_statuses}),
    )
    assert response.status_code == 200

    for i in range(100):
        park_id = f'parkid{i}'
        driver_id = f'driverid{i}'
        order_id = f'{order_id_prefix}_{i}'
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_orders_table(
            pgsql,
            order_id,
            driver_record_id,
            OrderStatus.kDriving,
            order_provider,
            future,
        )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_fallback_store(
        taxi_driver_status,
        pgsql,
        mocked_time,
        taxi_config,
        testpoint,
        redis_store,
):
    def _make_expected_items(reccount, order_id_prefix, updated_ts):
        result = {}
        for i in range(0, reccount):
            updated_ts_ms = utils.date_to_ms(updated_ts)
            result[(f'driverid{i}', f'parkid{i}')] = {
                'statuses': {updated_ts_ms: DriverStatus.Online},
                'orders': {
                    updated_ts_ms: {
                        f'{order_id_prefix}_{i}': {
                            'status': OrderStatus.kDriving,
                            'provider': 'unknown',
                        },
                    },
                },
            }

        return result

    # set call timestamp
    now = utils.parse_date_str('2021-05-17 00:01:09.0+00')
    mocked_time.set(now)
    await taxi_driver_status.invalidate_caches(clean_update=True)

    order_id_prefixes = ['oid1', 'oid2', 'oid3', 'oid4', 'oid5']
    prefixes_len = len(order_id_prefixes)
    times = [
        now,
        now + datetime.timedelta(seconds=1),
        now + datetime.timedelta(seconds=2),
        now + datetime.timedelta(seconds=3),
        now + datetime.timedelta(seconds=4),
    ]
    assert len(times) == prefixes_len

    # inject persistet storage failure
    @testpoint('persistent_storage_store_tp')
    def _inject_failure_tp(data):
        return {'inject_failure': True}

    for i in range(prefixes_len):
        # clear redis storage from the previous tests
        fallback_queue.clear(redis_store, fallback_queue.STATUS_EVENT_QUEUE)

        mocked_time.set(times[i])
        await taxi_driver_status.invalidate_caches(clean_update=True)

        update_drv_statuses = _make_request_items(
            2, order_id_prefix=order_id_prefixes[i], order_provider=0,
        )
        expected_events = _make_expected_items(
            2, order_id_prefixes[i], times[i],
        )
        response = await taxi_driver_status.post(
            'v1/internal/status/bulk',
            data=json.dumps({'items': update_drv_statuses}),
        )
        assert response.status_code == 200
        redis_result = fallback_queue.read_events(
            redis_store, fallback_queue.STATUS_EVENT_QUEUE,
        )
        assert expected_events == fallback_queue.to_comparable_status_repr(
            redis_result,
        )
