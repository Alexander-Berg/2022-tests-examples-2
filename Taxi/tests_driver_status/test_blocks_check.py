# pylint: disable=global-statement
import datetime
import json

import pytest

import tests_driver_status.pg_helpers as pg_helpers


BLOCKED_REASONS = [
    'none',
    'by_driver',
    'fns_unbound',
    'driver_taximeter_disabled',
    'driver_balance_debt',
    'driver_blacklist',
    'car_blacklist',
    'driver_dkk',
    'driver_license_verification',
    'driver_sts',
    'driver_identity',
    'driver_biometry',
    'pending_park_order',
    'car_is_used',
]

BLOCKED_REASON = 'none'


async def _run_worker(taxi_driver_status):
    await taxi_driver_status.run_task('worker-blocks-check.testsuite')


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
                        'worker-blocks-check': {
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
async def test_worker_disabled(
        taxi_driver_status, mockserver, pgsql, mocked_time,
):
    @mockserver.json_handler('/taximeter-xservice/utils/driver-status-check')
    def _driver_status_check_handler(request):
        response = []
        for driver in request.json:
            response.append(
                {
                    'park_id': driver['park_id'],
                    'driver_id': driver['driver_id'],
                    'app_family': '',
                    'result': 'driver_blacklist',
                    'onlycard': False,
                    'providers': 2,
                    'integration_event': False,
                },
            )
        return mockserver.make_response(
            json.dumps(response), 200, content_type='application/json',
        )

    now = datetime.datetime.now(datetime.timezone.utc)
    mocked_time.set(now)

    pg_helpers.run_in_transaction(
        pgsql,
        [
            pg_helpers.make_drivers_insert_query(now, 0, 1),
            pg_helpers.make_statuses_insert_query(
                'online', 'service', now, 0, 1,
            ),
        ],
    )

    await _run_worker(taxi_driver_status)
    assert pg_helpers.get_blocks_count(pgsql) == 0

    mocked_time.sleep(1900)
    await _run_worker(taxi_driver_status)
    assert pg_helpers.get_blocks_count(pgsql) == 0


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.config(
    DRIVER_STATUS_WORKER_DRIVERS_CHECKER={
        '__default__': {
            'enabled': True,
            'older_than_sec': 1800,
            'batch_size': 1000,
            'batches_count': 3,
            'parallel_requests': 8,
            'client_request_size': 30,
        },
        'worker-blocks-check': {
            'enabled': True,
            'older_than_sec': 1800,
            'batch_size': 1000,
            'batches_count': 3,
            'parallel_requests': 8,
            'client_request_size': 100,
        },
    },
)
@pytest.mark.parametrize(
    'drivers_count',
    [
        pytest.param(1, id='1 driver'),
        pytest.param(
            100,
            id='100 drivers (max drivers in request to taximeter-xservice)',
        ),
        pytest.param(101, id='101 drivers (max drivers in request + 1)'),
        pytest.param(800, id='800 drivers (100 * 8 parallel requests)'),
        pytest.param(801, id='801 drivers (100 * 8 parallel requests + 1)'),
        pytest.param(1000, id='1000 drivers (batch size)'),
        pytest.param(1001, id='1001 drivers (batch size + 1)'),
        # corner case (batch size * batch count) may fail sometimes
        # due to driver_checker's check time detection and
        # stop checking conditions
    ],
)
async def test_blocks_check(
        mockserver, taxi_driver_status, pgsql, mocked_time, drivers_count,
):
    @mockserver.json_handler('/taximeter-xservice/utils/driver-status-check')
    def _driver_status_check_handler(request):
        response = []
        for driver in request.json:
            driver_id = driver['driver_id']
            idx = int(driver_id[len('driverid') :])
            response.append(
                {
                    'park_id': driver['park_id'],
                    'driver_id': driver_id,
                    'app_family': '',
                    'result': BLOCKED_REASONS[idx % len(BLOCKED_REASONS)],
                    'onlycard': False,
                    'providers': 2,
                    'integration_event': False,
                },
            )
        return mockserver.make_response(
            json.dumps(response), 200, content_type='application/json',
        )

    now = datetime.datetime.now(datetime.timezone.utc)
    mocked_time.set(now)

    pg_helpers.run_in_transaction(
        pgsql,
        [
            pg_helpers.make_drivers_insert_query(now, 0, drivers_count),
            pg_helpers.make_statuses_insert_query(
                'online', 'service', now, 0, drivers_count,
            ),
        ],
    )

    # ds.blocks_update is empty, worker will start immediately
    mocked_time.sleep(1)
    await _run_worker(taxi_driver_status)

    reasons_count = len(BLOCKED_REASONS)
    assert reasons_count > 0
    for i in range(reasons_count):
        reason = BLOCKED_REASONS[i]
        # 'none' and 'by_driver' won't be inserted as a new block
        if reason in ('none', 'by_driver'):
            expected_count = 0
        else:
            expected_count = 1 + (drivers_count - i - 1) // reasons_count
        assert pg_helpers.get_blocks_count(pgsql, reason) == expected_count


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_select_for_check(
        taxi_driver_status, mockserver, pgsql, mocked_time,
):
    @mockserver.json_handler('/taximeter-xservice/utils/driver-status-check')
    def _driver_status_check_handler(request):
        response = []
        for driver in request.json:
            response.append(
                {
                    'park_id': driver['park_id'],
                    'driver_id': driver['driver_id'],
                    'app_family': '',
                    'result': 'driver_blacklist',
                    'onlycard': False,
                    'providers': 2,
                    'integration_event': False,
                },
            )
        return mockserver.make_response(
            json.dumps(response), 200, content_type='application/json',
        )

    now = datetime.datetime.now(datetime.timezone.utc)
    mocked_time.set(now)

    # insert 20 drivers, pretend that:
    # - first 10 were updated recently (next update after 30 minutes)
    # - second 10 were never updated (next update immediately)
    pg_helpers.run_in_transaction(
        pgsql,
        [
            pg_helpers.make_drivers_insert_query(now, 0, 20),
            pg_helpers.make_statuses_insert_query(
                'online', 'service', now, 0, 20,
            ),
            pg_helpers.make_blocks_update_insert_query(now, 0, 10),
        ],
    )

    mocked_time.sleep(1)
    await _run_worker(taxi_driver_status)
    assert pg_helpers.get_blocks_count(pgsql) == 10

    mocked_time.sleep(1800)
    await _run_worker(taxi_driver_status)
    assert pg_helpers.get_blocks_count(pgsql) == 20


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_block_changes(
        taxi_driver_status, mockserver, pgsql, mocked_time,
):
    global BLOCKED_REASON
    BLOCKED_REASON = 'none'

    @mockserver.json_handler('/taximeter-xservice/utils/driver-status-check')
    def _driver_status_check_handler(request):
        global BLOCKED_REASON
        response = []
        for driver in request.json:
            response.append(
                {
                    'park_id': driver['park_id'],
                    'driver_id': driver['driver_id'],
                    'app_family': '',
                    'result': BLOCKED_REASON,
                    'onlycard': False,
                    'providers': 2,
                    'integration_event': False,
                },
            )
        return mockserver.make_response(
            json.dumps(response), 200, content_type='application/json',
        )

    now = datetime.datetime.now(datetime.timezone.utc)
    mocked_time.set(now)

    pg_helpers.run_in_transaction(
        pgsql,
        [
            pg_helpers.make_drivers_insert_query(now, 0, 1),
            pg_helpers.make_statuses_insert_query(
                'online', 'service', now, 0, 1,
            ),
        ],
    )

    # 'none' won't be inserted as a new block
    BLOCKED_REASON = 'none'
    mocked_time.sleep(1801)
    await _run_worker(taxi_driver_status)
    assert pg_helpers.get_blocks_count(pgsql, BLOCKED_REASON) == 0

    # real block will be inserted
    BLOCKED_REASON = 'fns_unbound'
    mocked_time.sleep(1801)
    await _run_worker(taxi_driver_status)
    assert pg_helpers.get_blocks_count(pgsql, BLOCKED_REASON) == 1

    # other real block will be updated
    BLOCKED_REASON = 'driver_taximeter_disabled'
    mocked_time.sleep(1801)
    await _run_worker(taxi_driver_status)
    assert pg_helpers.get_blocks_count(pgsql, BLOCKED_REASON) == 1

    # if a driver already has block, then it can be changed to 'none'
    # to propagate change to consumers' caches
    BLOCKED_REASON = 'none'
    mocked_time.sleep(1801)
    await _run_worker(taxi_driver_status)
    assert pg_helpers.get_blocks_count(pgsql, BLOCKED_REASON) == 1
