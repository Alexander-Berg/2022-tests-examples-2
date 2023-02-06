# pylint: disable=redefined-outer-name
import datetime

import pytest

from tests_grocery_wms_gateway import consts


@pytest.fixture(name='event_post_requests_mock', autouse=True)
def _mock_custom_processing(mockserver):
    class Context:
        def __init__(self):
            self.mock_ok = False

        def times_processing_called(self):
            return (
                mock_processing.times_called
                + mock_eats_order_history.times_called
            )

    context = Context()

    @mockserver.json_handler('/processing/v1/grocery/processing/create-event')
    def mock_processing(request):
        if context.mock_ok:
            return mockserver.make_response(
                status=200, json={'event_id': '123'},
            )
        return mockserver.make_response(
            status=400, json={'code': 'invalid_payload', 'message': ''},
        )

    @mockserver.json_handler('/grocery-orders/internal/v1/send-to-history')
    def mock_eats_order_history(request):
        if context.mock_ok:
            return {}
        return mockserver.make_response(status=500)

    return context


async def _make_request(
        taxi_grocery_wms_gateway,
        order_id,
        event_id,
        timestamp='2020-02-17T11:46:35+03:00',
):
    response = await taxi_grocery_wms_gateway.post(
        '/v2/event',
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': order_id,
                    'event_id': event_id,
                    'type': 'canceled',
                    'timestamp': timestamp,
                    'revision': 1,
                    'problems': [],
                },
            ],
        },
    )
    return response


async def _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
):
    metric = await get_single_metric_by_label_values(
        taxi_grocery_wms_gateway_monitor,
        sensor='grocery_wms_gateway_failed_cache_size',
        labels={'cache_size': 'elements'},
    )

    if metric is None:
        return 0

    return metric.value


async def _get_was_failed_events(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
):
    metric025 = await get_single_metric_by_label_values(
        taxi_grocery_wms_gateway_monitor,
        sensor='grocery_wms_gateway_was_failed_events',
        labels={'request_event_type': 'canceled', 'gap_size': 'ok_after_0.25'},
    )
    if metric025 is None:
        return 0

    return metric025.value


async def _get_force_skipped_events_count(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
):
    metric = await get_single_metric_by_label_values(
        taxi_grocery_wms_gateway_monitor,
        sensor='grocery_wms_gateway_force_skipped_events',
        labels={'request_event_type': 'canceled'},
    )

    if metric is None:
        return 0

    return metric.value


@pytest.mark.parametrize(
    'order_id, event_id, success',
    [
        (
            '36139b364f0411ea86980050b6a4b5a0-grocery',
            '7aad153a622a45b692bc',
            True,
        ),
        ('352354-777333', '6aad153a622a45b692bc', True),
        (
            '36139b364f0411ea86980050b6a4b5a1-grocery',
            '71ad153a622a45b692bc',
            False,
        ),
        ('352354-777334', '61ad153a622a45b692bc', False),
    ],
)
@pytest.mark.config(GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True)
async def test_cache_creation(
        taxi_grocery_wms_gateway,
        taxi_grocery_wms_gateway_monitor,
        event_id,
        testpoint,
        order_id,
        get_single_metric_by_label_values,
        success,
        event_post_requests_mock,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    pre_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    event_post_requests_mock.mock_ok = success

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )

    await completed_tp.wait_call()

    assert response.status_code == 200

    post_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    response = response.json()
    assert response['code'] == 'OK'
    results = response['details']['results']
    assert len(results) == 1
    assert results[0]['event_id'] == event_id

    if success:
        assert (post_metric - pre_metric) == 0
        assert results[0]['code'] == 'OK'
    else:
        assert (post_metric - pre_metric) == 1
        assert results[0]['code'] == 'ERROR'


@pytest.mark.parametrize(
    'order_id, event_id',
    [
        ('36139b364f0411ea86980050b6a4b5a0-grocery', '81ad153a622a45b692bc'),
        ('352354-777333', '82ad153a622a45b692bc'),
    ],
)
@pytest.mark.config(GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True)
async def test_no_duplicates(
        taxi_grocery_wms_gateway,
        taxi_grocery_wms_gateway_monitor,
        event_post_requests_mock,
        event_id,
        testpoint,
        order_id,
        get_single_metric_by_label_values,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    pre_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    event_post_requests_mock.mock_ok = False

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )

    await completed_tp.wait_call()

    post_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    assert (post_metric - pre_metric) == 1

    assert response.status_code == 200
    response = response.json()
    assert response['code'] == 'OK'
    results = response['details']['results']
    assert len(results) == 1
    assert results[0]['event_id'] == event_id
    assert results[0]['code'] == 'ERROR'

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )

    await completed_tp.wait_call()

    assert (post_metric - pre_metric) == 1

    assert response.status_code == 200
    response = response.json()
    assert response['code'] == 'OK'
    results = response['details']['results']
    assert len(results) == 1
    assert results[0]['event_id'] == event_id
    assert results[0]['code'] == 'ERROR'


@pytest.mark.parametrize(
    'order_id, event_id',
    [
        ('36139b364f0411ea86980050b6a4b5a0-grocery', '812d153a622a45b692bc'),
        ('352354-777333', '823d153a622a45b692bc'),
    ],
)
@pytest.mark.config(GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True)
async def test_metric_added_ok_after_error(
        taxi_grocery_wms_gateway,
        taxi_grocery_wms_gateway_monitor,
        event_post_requests_mock,
        event_id,
        testpoint,
        order_id,
        get_single_metric_by_label_values,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    pre_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )
    pre_metric_ok_events = await _get_was_failed_events(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    event_post_requests_mock.mock_ok = False

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )

    await completed_tp.wait_call()

    assert response.status_code == 200

    post_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    response = response.json()
    assert response['code'] == 'OK'
    results = response['details']['results']
    assert len(results) == 1
    assert results[0]['event_id'] == event_id
    assert results[0]['code'] == 'ERROR'
    assert (post_metric - pre_metric) == 1

    event_post_requests_mock.mock_ok = True

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )

    await completed_tp.wait_call()

    post_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )
    post_metric_ok_events = await _get_was_failed_events(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    response = response.json()
    assert response['code'] == 'OK'
    results = response['details']['results']
    assert len(results) == 1
    assert results[0]['event_id'] == event_id
    assert results[0]['code'] == 'OK'
    assert (post_metric - pre_metric) == 1
    assert (post_metric_ok_events - pre_metric_ok_events) == 1


@pytest.mark.parametrize(
    'order_id, event_id',
    [
        ('12345b364f0411ea86980050b6a4b5a0-grocery', '1234563a622a45b692bc'),
        ('123454-777333', '1234553a622a45b692bc'),
    ],
)
@pytest.mark.config(GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True)
@pytest.mark.config(
    GROCERY_WMS_GATEWAY_FAILED_REQUEST_CACHE_FORCE_OK_AFTER_SECONDS=5,
)
async def test_force_after_sec(
        taxi_grocery_wms_gateway,
        taxi_grocery_wms_gateway_monitor,
        event_post_requests_mock,
        event_id,
        testpoint,
        order_id,
        get_single_metric_by_label_values,
        mocked_time,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    initial_cache_size_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )
    initial_force_skipped_metric = await _get_force_skipped_events_count(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    event_post_requests_mock.mock_ok = False

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )

    await completed_tp.wait_call()

    after_cache_size_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )
    after_force_skipped_metric = await _get_force_skipped_events_count(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    assert after_cache_size_metric - initial_cache_size_metric == 1
    assert after_force_skipped_metric - initial_force_skipped_metric == 0
    assert response.status_code == 200
    assert response.json()['details']['results'][0]['code'] == 'ERROR'

    mocked_time.sleep(7)
    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )

    await completed_tp.wait_call()

    after_cache_size_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )
    after_force_skipped_metric = await _get_force_skipped_events_count(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    assert after_cache_size_metric - initial_cache_size_metric == 1
    assert after_force_skipped_metric - initial_force_skipped_metric == 1
    assert response.status_code == 200
    assert response.json()['details']['results'][0]['code'] == 'OK'


@pytest.mark.parametrize(
    'order_id, event_id, offset',
    [
        (
            '82345b364f0411ea86980050b6a4b5a0-grocery',
            '8234563a622a45b692bc',
            0,
        ),
        ('823454-777333', '8234553a622a45b693bc', 1000),
    ],
)
@pytest.mark.config(GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True)
@pytest.mark.config(
    GROCERY_WMS_GATEWAY_FAILED_REQUEST_CACHE_SWAP_AFTER_SECONDS=10,
)
async def test_cache_clear(
        taxi_grocery_wms_gateway,
        taxi_grocery_wms_gateway_monitor,
        event_post_requests_mock,
        event_id,
        testpoint,
        order_id,
        get_single_metric_by_label_values,
        mocked_time,
        offset,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    await taxi_grocery_wms_gateway.invalidate_caches()

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    mocked_time.sleep(offset)
    await taxi_grocery_wms_gateway.invalidate_caches()

    event_post_requests_mock.mock_ok = True

    mocked_time.sleep(50)
    await taxi_grocery_wms_gateway.invalidate_caches()
    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )
    await completed_tp.wait_call()

    mocked_time.sleep(50)
    await taxi_grocery_wms_gateway.invalidate_caches()
    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )
    await completed_tp.wait_call()

    initial_cache_size_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    event_post_requests_mock.mock_ok = False

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )

    await completed_tp.wait_call()

    after_cache_size_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    assert after_cache_size_metric - initial_cache_size_metric == 1
    assert response.status_code == 200
    assert response.json()['details']['results'][0]['code'] == 'ERROR'

    mocked_time.sleep(50)
    await taxi_grocery_wms_gateway.invalidate_caches()

    event_post_requests_mock.mock_ok = True

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )
    await completed_tp.wait_call()

    after_cache_size_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    assert after_cache_size_metric - initial_cache_size_metric == 1
    assert response.status_code == 200
    assert response.json()['details']['results'][0]['code'] == 'OK'

    mocked_time.sleep(50)
    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id,
    )
    await completed_tp.wait_call()

    after_cache_size_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    assert after_cache_size_metric == 0
    assert response.status_code == 200
    assert response.json()['details']['results'][0]['code'] == 'OK'


@pytest.mark.parametrize(
    'order_id, event_id',
    [
        ('12345b364f0411ea86980050b6a4b5a0-grocery', '1234563a622a45b692bc'),
        ('223454-777333', '2234553a622a45b693bc'),
    ],
)
@pytest.mark.config(
    GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True,
    GROCERY_WMS_GATEWAY_FAILED_REQUEST_CACHE_USE_REQUEST_TIME=True,
    GROCERY_WMS_GATEWAY_FAILED_REQUEST_CACHE_FORCE_OK_AFTER_SECONDS=10,
)
async def test_use_request_time_clear(
        taxi_grocery_wms_gateway,
        taxi_grocery_wms_gateway_monitor,
        event_post_requests_mock,
        event_id,
        testpoint,
        order_id,
        get_single_metric_by_label_values,
        mocked_time,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    initial_cache_size_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )
    initial_force_skipped_metric = await _get_force_skipped_events_count(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    event_post_requests_mock.mock_ok = False

    request_time = (
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(seconds=-15)
    ).isoformat()

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id, request_time,
    )

    await completed_tp.wait_call()

    after_cache_size_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )
    after_force_skipped_metric = await _get_force_skipped_events_count(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    assert after_cache_size_metric - initial_cache_size_metric == 1
    assert after_force_skipped_metric - initial_force_skipped_metric == 0

    assert response.status_code == 200
    assert response.json()['details']['results'][0]['code'] == 'ERROR'
    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await _make_request(
        taxi_grocery_wms_gateway, order_id, event_id, request_time,
    )

    await completed_tp.wait_call()

    after_cache_size_metric = await _get_cache_size(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )
    after_force_skipped_metric = await _get_force_skipped_events_count(
        get_single_metric_by_label_values, taxi_grocery_wms_gateway_monitor,
    )

    assert after_cache_size_metric - initial_cache_size_metric == 1
    assert after_force_skipped_metric - initial_force_skipped_metric == 1
    assert response.status_code == 200
    assert response.json()['details']['results'][0]['code'] == 'OK'
