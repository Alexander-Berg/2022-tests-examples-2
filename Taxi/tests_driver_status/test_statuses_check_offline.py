import datetime

import pytest

# pylint: disable=import-only-modules
from tests_driver_status.enum_constants import ACTIVE_ORDER_STATUSES
from tests_driver_status.enum_constants import OrderStatus
# pylint: enable=import-only-modules
import tests_driver_status.pg_helpers as pg_helpers


ACTIVE_ORDERS_PG_ARRAY = '\'{{{}}}\'::ds.order_status[]'.format(
    ','.join(map('"{}"'.format, ACTIVE_ORDER_STATUSES)),
)


async def _run_worker(taxi_driver_status):
    await taxi_driver_status.run_task(
        'worker-statuses-check-offline.testsuite',
    )


def _get_statuses_count(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('SELECT count(*) FROM ds.statuses')
    return cursor.fetchone()[0]


def _get_updated_count(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT count(*) FROM ds.statuses '
        'WHERE source = \'periodical-updater\'',
    )
    return cursor.fetchone()[0]


def _get_offline_count(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT count(*) FROM ds.statuses WHERE status = \'offline\'',
    )
    return cursor.fetchone()[0]


def _get_orders_count(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('SELECT count(*) FROM ds.orders')
    return cursor.fetchone()[0]


# 'SELECT count(*) FROM ds.orders WHERE status = \'transporting\'',
def _get_active_orders_count(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT count(*) FROM ds.orders WHERE status = ANY({})'.format(
            ACTIVE_ORDERS_PG_ARRAY,
        ),
    )
    return cursor.fetchone()[0]


def _get_finished_orders_count(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT count(*) FROM ds.orders WHERE status = \'complete\'',
    )
    return cursor.fetchone()[0]


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            id='worker disabled',
            marks=[
                pytest.mark.config(
                    DRIVER_STATUS_WORKER_DRIVERS_CHECKER={
                        '__default__': {
                            'enabled': True,
                            'older_than_sec': 1800,
                            'batch_size': 1000,
                            'batches_count': 3,
                            'parallel_requests': 8,
                            'client_request_size': 30,
                        },
                        'worker-statuses-check-offline': {
                            'enabled': False,
                            'older_than_sec': 1800,
                            'batch_size': 1000,
                            'batches_count': 3,
                            'parallel_requests': 8,
                            'client_request_size': 30,
                        },
                    },
                ),
            ],
        ),
    ],
)
async def test_worker_disabled(taxi_driver_status, pgsql, mocked_time):
    now = datetime.datetime.now(datetime.timezone.utc)
    mocked_time.set(now)

    pg_helpers.run_in_transaction(
        pgsql,
        [
            pg_helpers.make_drivers_insert_query(now, 0, 1),
            pg_helpers.make_statuses_insert_query(
                'online', 'service', now, 0, 1,
            ),
            pg_helpers.make_orders_insert_query(
                OrderStatus.kDriving, now, 0, 1,
            ),
        ],
    )

    await _run_worker(taxi_driver_status)
    assert _get_statuses_count(pgsql) == 1
    assert _get_updated_count(pgsql) == 0
    assert _get_offline_count(pgsql) == 0
    assert _get_orders_count(pgsql) == 1
    assert _get_active_orders_count(pgsql) == 1
    assert _get_finished_orders_count(pgsql) == 0

    mocked_time.sleep(1900)
    await _run_worker(taxi_driver_status)
    assert _get_statuses_count(pgsql) == 1
    assert _get_updated_count(pgsql) == 0
    assert _get_offline_count(pgsql) == 0
    assert _get_orders_count(pgsql) == 1
    assert _get_active_orders_count(pgsql) == 1
    assert _get_finished_orders_count(pgsql) == 0


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.config(
    DRIVER_STATUS_WORKER_TTL_CLEANER={
        '__default__': {'batch_size': 10, 'ttl_hours': 100500},
    },
)
@pytest.mark.parametrize(
    'drivers_count',
    [
        pytest.param(1, id='1 driver'),
        pytest.param(30, id='30 drivers (max drivers in request to DA)'),
        pytest.param(31, id='31 drivers (max drivers in request to DA + 1)'),
        pytest.param(240, id='240 drivers (30 * 8 parallel requests to DA)'),
        pytest.param(
            241, id='241 drivers (30 * 8 parallel requests to DA + 1)',
        ),
        pytest.param(1000, id='1000 drivers (batch size)'),
        pytest.param(1001, id='1001 drivers (batch size + 1)'),
        # corner case (batch size * batch count) may fail sometimes
        # due to driver_checker's check time detection and
        # stop checking conditions
    ],
)
async def test_statuses_check_offline(
        mockserver, taxi_driver_status, pgsql, mocked_time, drivers_count,
):
    @mockserver.json_handler(
        '/driver-authorizer/driver/sessions/bulk_retrieve',
    )
    def _mock_driver_authorizer(request):
        answer = {'sessions': []}
        for driver in request.json.get('drivers'):
            park_id = driver['park_id']
            uuid = driver['uuid']
            idx = int(uuid[len('driverid') :])
            status = 'ok'
            if idx % 3 == 0:
                status = 'not_found'
            answer['sessions'].append(
                {
                    'client_id': 'taximeter',
                    'park_id': park_id,
                    'uuid': uuid,
                    'driver_app_profile_id': '',
                    'status': status,
                },
            )

        return mockserver.make_response(json=answer, status=200)

    await taxi_driver_status.enable_testpoints()

    now = datetime.datetime.now(datetime.timezone.utc)
    mocked_time.set(now)

    pg_helpers.run_in_transaction(
        pgsql,
        [
            pg_helpers.make_drivers_insert_query(now, 0, drivers_count),
            pg_helpers.make_statuses_insert_query(
                'online', 'service', now, 0, drivers_count,
            ),
            pg_helpers.make_orders_insert_query(
                OrderStatus.kDriving, now, 0, drivers_count,
            ),
        ],
    )

    await _run_worker(taxi_driver_status)
    assert _get_statuses_count(pgsql) == drivers_count
    assert _get_updated_count(pgsql) == 0
    assert _get_offline_count(pgsql) == 0
    assert _get_orders_count(pgsql) == drivers_count
    assert _get_active_orders_count(pgsql) == drivers_count
    assert _get_finished_orders_count(pgsql) == 0

    mocked_time.sleep(1900)
    await _run_worker(taxi_driver_status)
    expected_offline = 1 + (drivers_count - 1) // 3
    assert _get_statuses_count(pgsql) == drivers_count
    assert _get_updated_count(pgsql) == drivers_count
    assert _get_offline_count(pgsql) == expected_offline
    assert _get_orders_count(pgsql) == drivers_count
    assert _get_active_orders_count(pgsql) == drivers_count - expected_offline
    assert _get_finished_orders_count(pgsql) == expected_offline
