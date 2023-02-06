import datetime

import pytest

import tests_eta_autoreorder.utils as utils

ALL_ORDER_IDS = (
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    'cccccccccccccccccccccccccccccccc',
    'aaa',
    'bbb',
    'ccc',
    'ddd',
)


@pytest.mark.config(ETA_AUTOREORDER_ORDER_PROCESSING_PERIOD=30)
@pytest.mark.now('2020-06-30T10:10:00+00:00')
async def test_reschedule_order_processing(
        taxi_eta_autoreorder, stq_runner, stq,
):
    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task', expect_fail=False,
    )
    assert stq.eta_autoreorder_run_order_processing.times_called == 1
    next_call = stq.eta_autoreorder_run_order_processing.next_call()
    assert next_call['id'] == 'test_task'
    assert next_call['eta'] == datetime.datetime(2020, 6, 30, 10, 10, 30)


@pytest.mark.config(ETA_AUTOREORDER_SERVICE_ENABLED=True)
@pytest.mark.config(ETA_AUTOREORDER_ORDER_IN_DATABASE_TTL=30)
@pytest.mark.pgsql('eta_autoreorder', files=['default_orders.sql'])
@pytest.mark.now('2020-01-01T12:35:30+00:00')
async def test_cleanup_in_order_processing(
        taxi_eta_autoreorder, stq_runner, stq,
):
    response = await taxi_eta_autoreorder.get('internal/orders')
    assert 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' in {
        order['id'] for order in response.json()
    }

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task', expect_fail=False,
    )
    await taxi_eta_autoreorder.invalidate_caches()

    response = await taxi_eta_autoreorder.get('internal/orders')
    assert response.status_code == 200
    assert 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' not in {
        order['id'] for order in response.json()
    }
    assert 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' in {
        order['id'] for order in response.json()
    }


@pytest.mark.now('2020-01-01T12:00:05')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='reorder_limit.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
)
async def test_order_core_handler_timeout(
        taxi_eta_autoreorder,
        stq_runner,
        testpoint,
        mockserver,
        load_json,
        pgsql,
        redis_store,
        now,
):
    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def mock_autoreorder(request, *args, **kwargs):
        raise mockserver.TimeoutError()

    @mockserver.json_handler('/driver-eta/driver-eta/v2/eta')
    def mock_driver_eta(request):
        return load_json('eta_response.json')

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('order_processing_order_core_client_timeout')
    def order_core_client_timeout(data):
        return data

    await taxi_eta_autoreorder.enable_testpoints()

    await utils.initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
    )

    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )

    await taxi_eta_autoreorder.invalidate_caches()

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )

    assert mock_autoreorder.times_called == 1
    assert mock_driver_eta.times_called == 1
    assert order_core_client_timeout.times_called == 1


@pytest.mark.now('2020-01-01T12:00:05')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.experiments3(filename='experiments3_call_autoreorder.json')
@pytest.mark.experiments3(filename='reorder_limit.json')
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True,
    ETA_AUTOREORDER_CALL_AUTOREORDER=True,
)
@pytest.mark.parametrize('is_disabled_by_time', [False, True])
async def test_reorder_time_limit(
        taxi_eta_autoreorder,
        stq_runner,
        testpoint,
        mockserver,
        load_json,
        pgsql,
        redis_store,
        now,
        mocked_time,
        is_disabled_by_time,
):
    @mockserver.handler('/order-core/internal/processing/v1/event/autoreorder')
    async def mock_autoreorder(request, *args, **kwargs):
        return mockserver.make_response('', status=200)

    @mockserver.json_handler('/driver-eta/driver-eta/v2/eta')
    def mock_driver_eta(request):
        return load_json('eta_response.json')

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    await taxi_eta_autoreorder.enable_testpoints()

    await utils.initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
    )

    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        order_ids=ALL_ORDER_IDS,
        cache_is_empty=False,
    )

    if is_disabled_by_time:
        mocked_time.sleep(200)

    await taxi_eta_autoreorder.invalidate_caches()

    await stq_runner.eta_autoreorder_run_order_processing.call(
        task_id='test_task',
    )

    if is_disabled_by_time:
        assert mock_autoreorder.times_called == 0
        assert mock_driver_eta.times_called == 0
    else:
        assert mock_autoreorder.times_called == 1
        assert mock_driver_eta.times_called == 1
