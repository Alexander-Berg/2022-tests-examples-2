# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines
import pytest

from tests_grocery_wms_gateway import consts

EVENT_URI_LIST = pytest.mark.parametrize('uri', ['/v1/event', '/v2/event'])


async def _get_total_event_count_metric(
        get_single_metric_by_label_values,
        taxi_grocery_wms_gateway_monitor,
        tag,
):
    metric = await get_single_metric_by_label_values(
        taxi_grocery_wms_gateway_monitor,
        sensor=tag,
        labels={'count': 'total'},
    )

    if metric is None:
        return 0

    return metric.value


async def _get_failed_event_count_metric(
        get_single_metric_by_label_values,
        taxi_grocery_wms_gateway_monitor,
        tag,
):
    metric = await get_single_metric_by_label_values(
        taxi_grocery_wms_gateway_monitor,
        sensor=tag,
        labels={'count': 'failed'},
    )

    if metric is None:
        return 0

    return metric.value


@EVENT_URI_LIST
async def test_basic(taxi_grocery_wms_gateway, testpoint, uri, grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    event_id = '7aad153a622a45b692b'

    response = await taxi_grocery_wms_gateway.post(
        uri,
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': '36139b364f0411ea86980050b6a4b5a0-grocery',
                    'event_id': event_id,
                    'type': 'request',
                    'timestamp': '2020-02-17T11:46:35+03:00',
                    'revision': 1,
                    'problems': [],
                },
            ],
        },
    )
    await completed_tp.wait_call()
    assert response.status_code == 200

    if uri == '/v1/event':
        assert response.json() == {'code': 'OK'}
    else:
        assert response.json() == {
            'code': 'OK',
            'details': {'results': [{'code': 'OK', 'event_id': event_id}]},
        }


@EVENT_URI_LIST
@pytest.mark.config(GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True)
@pytest.mark.parametrize('order_found', [True, False])
@pytest.mark.parametrize('successfully_sent', [True, False])
async def test_complete(
        taxi_grocery_wms_gateway,
        mockserver,
        testpoint,
        processing,
        uri,
        order_found,
        successfully_sent,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1,
        legacy_depot_id=consts.DEFAULT_DEPOT_ID,
        depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    order_id = '36139b364f0411ea86980050b6a4b5a0-grocery'
    eats_order_id = '352354-777333'
    updated_at_wms = '2020-02-17T08:46:35+00:00'
    updated_at_eda = '2020-02-17T08:46:35.000000Z'

    @mockserver.json_handler(
        '/eats-integration-api/menu/{}/status'.format(consts.DEFAULT_DEPOT_ID),
    )
    def mock_eats(request):
        assert request.json[0]['status'] == 'finish'
        assert request.json[0]['updated_at'] == updated_at_eda

        result_ok = {'result': 'OK'}
        result_400 = {'status_code': 400}

        return result_ok if successfully_sent else result_400

    @mockserver.json_handler('/grocery-orders/internal/v1/send-to-history')
    def mock_eats_order_history(request):
        assert request.json['event'] == 'complete'
        assert request.json['order_id'] == eats_order_id
        assert request.json['eda_event'] == 'PICKUP'

        return {'status_code': 200} if order_found else {'status_code': 404}

    event_id = '7aad153a622a45b692bc'
    event_id2 = '7aad153a622a45b692b'
    response = await taxi_grocery_wms_gateway.post(
        uri,
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': order_id,
                    'event_id': event_id,
                    'type': 'complete',
                    'timestamp': updated_at_wms,
                    'revision': 1,
                    'external_order_revision': '0',
                    'problems': [],
                },
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': eats_order_id,
                    'event_id': event_id2,
                    'type': 'complete',
                    'external_type': 'PICKUP',
                    'timestamp': updated_at_wms,
                    'revision': 1,
                    'external_order_revision': '1',
                    'problems': [],
                },
            ],
        },
    )
    await completed_tp.wait_call()
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    create_order_event = events[0]
    assert create_order_event.item_id == order_id
    assert create_order_event.payload == {
        'reason': 'setstate',
        'order_id': order_id,
        'state': 'assembled',
        'payload': {'success': True, 'order_revision': '0'},
    }

    assert mock_eats.times_called == 2
    assert mock_eats_order_history.times_called == 1

    if uri == '/v1/event':
        assert response.json() == {'code': 'OK'}
    else:
        assert response.json() == {
            'code': 'OK',
            'details': {
                'results': [
                    {'code': 'OK', 'event_id': event_id},
                    {'code': 'OK', 'event_id': event_id2},
                ],
            },
        }


@EVENT_URI_LIST
async def test_event_takes_max_revision(
        taxi_grocery_wms_gateway, mockserver, testpoint, uri, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1,
        legacy_depot_id=consts.DEFAULT_DEPOT_ID,
        depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    order_id = '36139b364f0411ea86980050b6a4b5a0-grocery'
    updated_at_wms = '2020-02-17T08:46:35+00:00'
    updated_at_eda = '2020-02-17T08:46:35.000000Z'

    @mockserver.json_handler(
        '/eats-integration-api/menu/{}/status'.format(consts.DEFAULT_DEPOT_ID),
    )
    def mock_eats(request):
        assert request.json == [
            {'id': order_id, 'status': 'finish', 'updated_at': updated_at_eda},
        ]

        return {'result': 'OK'}

    event_id = '7aad153a622a45b692bcc233'
    event_id2 = '7aad153a622a45b692b'
    response = await taxi_grocery_wms_gateway.post(
        uri,
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': order_id,
                    'event_id': event_id,
                    'type': 'request',
                    'timestamp': updated_at_wms,
                    'revision': 1,
                    'problems': [],
                },
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': order_id,
                    'event_id': event_id2,
                    'type': 'complete',
                    'timestamp': updated_at_wms,
                    'revision': 2,
                    'problems': [],
                },
            ],
        },
    )
    await completed_tp.wait_call()

    assert response.status_code == 200

    if uri == '/v1/event':
        assert mock_eats.times_called == 1

        assert response.json() == {'code': 'OK'}
    else:
        assert mock_eats.times_called == 0

        response = response.json()
        assert response['code'] == 'OK'
        results = response['details']['results']
        assert results[0]['code'] == 'OK'
        assert results[0]['event_id'] == event_id
        assert results[1]['code'] == 'WARNING'
        assert results[1]['event_id'] == event_id2


@EVENT_URI_LIST
@pytest.mark.parametrize('event_type', ['approving', 'processing'])
@pytest.mark.config(GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True)
async def test_approving_event(
        taxi_grocery_wms_gateway,
        mockserver,
        testpoint,
        processing,
        event_type,
        uri,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    eats_order_id = '352354-777333'
    order_id = '36139b364f0411ea86980050b6a4b5a0-grocery'

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    @mockserver.json_handler('/grocery-orders/internal/v1/send-to-history')
    def mock_eats_order_history(request):
        assert request.json['event'] == event_type
        assert request.json['order_id'] == eats_order_id
        assert request.json['eda_event'] == 'PLACE_CONFIRMED'

        return {'status_code': 200}

    await taxi_grocery_wms_gateway.invalidate_caches()

    event_id = '7aad153a622a45b692b'

    response = await taxi_grocery_wms_gateway.post(
        uri,
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': order_id,
                    'event_id': event_id,
                    'type': event_type,
                    'timestamp': '2020-02-17T11:46:35+03:00',
                    'revision': 1,
                    'external_order_revision': '0',
                    'problems': [],
                },
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': eats_order_id,
                    'event_id': event_id,
                    'type': event_type,
                    'external_type': 'PLACE_CONFIRMED',
                    'timestamp': '2020-02-17T11:46:35+03:00',
                    'revision': 1,
                    'problems': [],
                },
            ],
        },
    )
    await completed_tp.wait_call()

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    create_order_event = events[0]
    assert create_order_event.item_id == order_id
    assert create_order_event.payload == {
        'reason': 'setstate',
        'payload': {'problems': [], 'order_revision': '0'},
        'state': 'wms_accepting',
        'order_id': order_id,
    }

    assert mock_eats_order_history.times_called == 1

    if uri == '/v1/event':
        assert response.json() == {'code': 'OK'}
    else:
        assert response.json() == {
            'code': 'OK',
            'details': {
                'results': [
                    {'code': 'OK', 'event_id': event_id},
                    {'code': 'OK', 'event_id': event_id},
                ],
            },
        }


@EVENT_URI_LIST
@pytest.mark.config(GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True)
async def test_canceling_event(
        taxi_grocery_wms_gateway, testpoint, processing, uri, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    event_id = '7aad153a622a45b692b'
    order_id = '36139b364f0411ea86980050b6a4b5a0-grocery'
    response = await taxi_grocery_wms_gateway.post(
        uri,
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': order_id,
                    'event_id': event_id,
                    'type': 'canceled',
                    'timestamp': '2020-02-17T11:46:35+03:00',
                    'revision': 1,
                    'problems': [],
                },
            ],
        },
    )
    await completed_tp.wait_call()

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    create_order_event = events[0]
    assert create_order_event.item_id == order_id
    assert create_order_event.payload == {
        'payload': {'problems': []},
        'reason': 'setstate',
        'order_id': order_id,
        'state': 'wms_cancelled',
    }

    if uri == '/v1/event':
        assert response.json() == {'code': 'OK'}
    else:
        assert response.json() == {
            'code': 'OK',
            'details': {'results': [{'code': 'OK', 'event_id': event_id}]},
        }


@pytest.mark.parametrize('is_grocery', [True, False])
@EVENT_URI_LIST
@pytest.mark.config(GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True)
async def test_bad_response(
        taxi_grocery_wms_gateway,
        mockserver,
        testpoint,
        processing,
        uri,
        is_grocery,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    event_id = '7aad153a622a45b692b'
    grocery_order_id = '36139b364f0411ea86980050b6a4b5a0-grocery'
    eats_order_id = '352354-777333'

    if is_grocery:
        order_id = grocery_order_id

        @mockserver.json_handler(
            '/processing/v1/grocery/processing/create-event',
        )
        def mock_processing(request):
            return mockserver.make_response(
                status=400, json={'code': 'invalid_payload', 'message': ''},
            )

    else:
        order_id = eats_order_id

        @mockserver.json_handler('/grocery-orders/internal/v1/send-to-history')
        def mock_eats_order_history(request):
            return mockserver.make_response(status=500)

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        uri,
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': order_id,
                    'event_id': event_id,
                    'type': 'canceled',
                    'timestamp': '2020-02-17T11:46:35+03:00',
                    'revision': 1,
                    'problems': [],
                },
            ],
        },
    )
    await completed_tp.wait_call()

    assert response.status_code == 200

    if is_grocery:
        assert mock_processing.times_called == 1
    else:
        assert mock_eats_order_history.times_called == 1

    if uri == '/v1/event':
        assert response.json() == {'code': 'OK'}
    else:
        response = response.json()
        assert response['code'] == 'OK'
        results = response['details']['results']
        assert len(results) == 1
        assert results[0]['code'] == 'ERROR'
        assert results[0]['event_id'] == event_id


class ProcessingMockContext:
    def __init__(self):
        self.fail_at = -1
        self.times_called = 0

    def get_status(self):
        if self.times_called == self.fail_at:
            return 400
        self.times_called = self.times_called + 1
        return 200


@pytest.fixture
def processing_mock_context():
    return ProcessingMockContext()


@pytest.fixture
def mock_processing_stateful(mockserver, processing_mock_context):
    class MockProcessing:
        @mockserver.handler('/processing/v1/grocery/processing/create-event')
        @staticmethod
        async def processing_handler(request):
            status = processing_mock_context.get_status()
            if status == 400:
                json = {'code': 'invalid_payload', 'message': ''}
            else:
                json = {'event_id': ''}
            return mockserver.make_response(json=json, status=status)

    return MockProcessing()


@pytest.mark.parametrize('fail_at', [0, 1, 2, 3])
@EVENT_URI_LIST
@pytest.mark.config(GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True)
@pytest.mark.config(GROCERY_WMS_GATEWAY_EVENT_MAX_SEQUENTIAL_TASK_COUNT=1000)
async def test_processing_bad_response(
        taxi_grocery_wms_gateway,
        mockserver,
        testpoint,
        mock_processing_stateful,
        processing_mock_context,
        uri,
        fail_at,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    event_id = '7aad153a622a45b692b'
    grocery_order_id = '36139b364f0411ea86980050b6a4b5a0-grocery'
    event_count = 3

    await taxi_grocery_wms_gateway.invalidate_caches()

    processing_mock_context.fail_at = fail_at

    response = await taxi_grocery_wms_gateway.post(
        uri,
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': grocery_order_id,
                    'event_id': event_id + str(i),
                    'type': 'processing',
                    'timestamp': '2020-02-17T11:46:35+03:00',
                    'revision': 1,
                    'problems': [],
                }
                for i in range(event_count)
            ],
        },
    )
    await completed_tp.wait_call()

    assert response.status_code == 200

    if uri == '/v1/event':
        assert response.json() == {'code': 'OK'}
    else:
        response = response.json()
        assert response['code'] == 'OK'
        results = response['details']['results']
        assert event_count == len(results)
        for i in range(event_count):
            result = results[i]
            assert result['event_id'] == event_id + str(i)
            if i < fail_at:
                assert result['code'] == 'OK'
            else:
                assert result['code'] == 'ERROR'


class HistoryMockContext:
    def __init__(self):
        self.fail_at = -1
        self.times_called = 0

    def get_status(self):
        if self.times_called == self.fail_at:
            return 400
        self.times_called = self.times_called + 1
        return 200


@pytest.fixture
def history_mock_context():
    return HistoryMockContext()


@pytest.fixture
def mock_history_stateful(mockserver, history_mock_context):
    class MockHistory:
        @mockserver.handler('/grocery-orders/internal/v1/send-to-history')
        @staticmethod
        async def history_handler(request):
            status = history_mock_context.get_status()
            return mockserver.make_response(status=status)

    return MockHistory()


@pytest.mark.parametrize('fail_at', [0, 1, 2, 3])
@EVENT_URI_LIST
@pytest.mark.config(GROCERY_WMS_GATEWAY_EVENT_MAX_SEQUENTIAL_TASK_COUNT=1000)
async def test_history_bad_response(
        taxi_grocery_wms_gateway,
        mockserver,
        testpoint,
        mock_history_stateful,
        history_mock_context,
        uri,
        fail_at,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    event_id = '7aad153a622a45b692b'
    eats_order_id = '352354-777333'
    event_count = 3

    await taxi_grocery_wms_gateway.invalidate_caches()

    history_mock_context.fail_at = fail_at

    response = await taxi_grocery_wms_gateway.post(
        uri,
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': eats_order_id,
                    'event_id': event_id + str(i),
                    'type': 'processing',
                    'timestamp': '2020-02-17T11:46:35+03:00',
                    'revision': 1,
                    'problems': [],
                }
                for i in range(event_count)
            ],
        },
    )
    await completed_tp.wait_call()

    assert response.status_code == 200

    if uri == '/v1/event':
        assert response.json() == {'code': 'OK'}
    else:
        response = response.json()
        assert response['code'] == 'OK'
        results = response['details']['results']
        assert event_count == len(results)
        for i in range(event_count):
            result = results[i]
            assert result['event_id'] == event_id + str(i)
            if i < fail_at:
                assert result['code'] == 'OK'
            else:
                assert result['code'] == 'ERROR'


@EVENT_URI_LIST
async def test_default_max_sequential_task_count_cap(
        taxi_grocery_wms_gateway, mockserver, testpoint, uri, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    event_id = '7aad153a622a45b692b'
    eats_order_id = '352354-777333'
    event_count = 4

    @mockserver.json_handler('/grocery-orders/internal/v1/send-to-history')
    def mock_eats_order_history(request):
        assert request.json['event'] == 'processing'
        assert request.json['order_id'] == eats_order_id

        return {}

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        uri,
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': eats_order_id,
                    'event_id': event_id + str(i),
                    'type': 'processing',
                    'timestamp': '2020-02-17T11:46:35+03:00',
                    'revision': 1,
                    'problems': [],
                }
                for i in range(event_count)
            ],
        },
    )
    await completed_tp.wait_call()

    assert response.status_code == 200

    if uri == '/v1/event':
        assert mock_eats_order_history.times_called == event_count

        assert response.json() == {'code': 'OK'}
    else:
        assert mock_eats_order_history.times_called == 1

        response = response.json()
        assert response['code'] == 'OK'
        results = response['details']['results']
        assert event_count == len(results)
        for i in range(event_count):
            result = results[i]
            assert result['event_id'] == event_id + str(i)
            if i == 0:
                assert result['code'] == 'OK'
            else:
                assert result['code'] == 'WARNING'


@EVENT_URI_LIST
@pytest.mark.config(GROCERY_WMS_GATEWAY_EVENT_MAX_SEQUENTIAL_TASK_COUNT=3)
async def test_max_sequential_task_count_cap(
        taxi_grocery_wms_gateway, mockserver, testpoint, uri, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    event_id = '7aad153a622a45b692b'
    eats_order_id = '352354-777333'
    event_count = 4

    @mockserver.json_handler('/grocery-orders/internal/v1/send-to-history')
    def mock_eats_order_history(request):
        assert request.json['event'] == 'processing'
        assert request.json['order_id'] == eats_order_id

        return {}

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        uri,
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': eats_order_id,
                    'event_id': event_id + str(i),
                    'type': 'processing',
                    'timestamp': '2020-02-17T11:46:35+03:00',
                    'revision': 1,
                    'problems': [],
                }
                for i in range(event_count)
            ],
        },
    )
    await completed_tp.wait_call()

    assert response.status_code == 200

    if uri == '/v1/event':
        assert mock_eats_order_history.times_called == event_count

        assert response.json() == {'code': 'OK'}
    else:
        assert mock_eats_order_history.times_called == 3

        response = response.json()
        assert response['code'] == 'OK'
        results = response['details']['results']
        assert event_count == len(results)
        for i in range(event_count):
            result = results[i]
            assert result['event_id'] == event_id + str(i)
            if i < 3:
                assert result['code'] == 'OK'
            else:
                assert result['code'] == 'WARNING'


@pytest.mark.config(GROCERY_WMS_GATEWAY_EVENT_MAX_SEQUENTIAL_TASK_COUNT=1000)
@pytest.mark.config(GROCERY_WMS_GATEWAY_EVENT_MAX_TASK_COUNT=3)
async def test_v2_max_task_count_cap(
        taxi_grocery_wms_gateway, mockserver, testpoint, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    event_id = '7aad153a622a45b692b'
    eats_order_id = '352354-777333'
    event_count = 4

    @mockserver.json_handler('/grocery-orders/internal/v1/send-to-history')
    def mock_eats_order_history(request):
        assert request.json['event'] == 'processing'
        assert request.json['order_id'] == eats_order_id

        return {}

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v2/event',
        headers={'X-Yandex-UID': '1234'},
        json={
            'events': [
                {
                    'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                    'external_id': eats_order_id,
                    'event_id': event_id + str(i),
                    'type': 'processing',
                    'timestamp': '2020-02-17T11:46:35+03:00',
                    'revision': 1,
                    'problems': [],
                }
                for i in range(event_count)
            ],
        },
    )
    await completed_tp.wait_call()

    assert response.status_code == 200

    assert mock_eats_order_history.times_called == 3

    response = response.json()
    assert response['code'] == 'OK'
    results = response['details']['results']
    assert event_count == len(results)
    for i in range(event_count):
        result = results[i]
        assert result['event_id'] == event_id + str(i)
        if i < 3:
            assert result['code'] == 'OK'
        else:
            assert result['code'] == 'WARNING'


@pytest.mark.parametrize(
    'uri, metric_tag',
    [
        ('/v1/event', 'grocery_wms_gateway_event_post_v1'),
        ('/v2/event', 'grocery_wms_gateway_event_post_v2'),
    ],
)
@pytest.mark.parametrize(
    'order_id, event_id',
    [
        ('361312364f0411ea86980050b6a4b5a0-grocery', '7aad123a622a45b692bc'),
        ('352313-777333', '6aad133a622a45b692bc'),
    ],
)
@pytest.mark.config(GROCERY_WMS_GATEWAY_PROCESSING_ENABLED=True)
async def test_event_count_metric_added(
        taxi_grocery_wms_gateway,
        taxi_grocery_wms_gateway_monitor,
        event_id,
        testpoint,
        order_id,
        mockserver,
        get_single_metric_by_label_values,
        uri,
        metric_tag,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @testpoint('orders-events-processed')
    def completed_tp(data):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    response_ok = True

    @mockserver.json_handler('/processing/v1/grocery/processing/create-event')
    def mock_processing(request):
        if response_ok:
            return mockserver.make_response(
                status=200, json={'event_id': '123'},
            )
        return mockserver.make_response(
            status=400, json={'code': 'invalid_payload', 'message': ''},
        )

    @mockserver.json_handler('/grocery-orders/internal/v1/send-to-history')
    def mock_eats_order_history(request):
        if response_ok:
            return {}
        return mockserver.make_response(status=500)

    total_before = await _get_total_event_count_metric(
        get_single_metric_by_label_values,
        taxi_grocery_wms_gateway_monitor,
        metric_tag,
    )

    failed_before = await _get_failed_event_count_metric(
        get_single_metric_by_label_values,
        taxi_grocery_wms_gateway_monitor,
        metric_tag,
    )

    async def make_request():
        return await taxi_grocery_wms_gateway.post(
            uri,
            headers={'X-Yandex-UID': '1234'},
            json={
                'events': [
                    {
                        'store_id': consts.DEFAULT_WMS_DEPOT_ID,
                        'external_id': order_id,
                        'event_id': event_id,
                        'type': 'canceled',
                        'timestamp': '2020-02-17T11:46:35+03:00',
                        'revision': 1,
                        'problems': [],
                    },
                ],
            },
        )

    response = await make_request()

    await completed_tp.wait_call()

    total_after = await _get_total_event_count_metric(
        get_single_metric_by_label_values,
        taxi_grocery_wms_gateway_monitor,
        metric_tag,
    )

    failed_after = await _get_failed_event_count_metric(
        get_single_metric_by_label_values,
        taxi_grocery_wms_gateway_monitor,
        metric_tag,
    )

    assert response.status_code == 200

    if uri == '/v1/event':
        assert response.json() == {'code': 'OK'}
    else:
        assert response.json() == {
            'code': 'OK',
            'details': {'results': [{'code': 'OK', 'event_id': event_id}]},
        }

    assert total_after - total_before == 1
    assert failed_after - failed_before == 0

    response_ok = False

    total_before = await _get_total_event_count_metric(
        get_single_metric_by_label_values,
        taxi_grocery_wms_gateway_monitor,
        metric_tag,
    )

    failed_before = await _get_failed_event_count_metric(
        get_single_metric_by_label_values,
        taxi_grocery_wms_gateway_monitor,
        metric_tag,
    )

    response = await make_request()

    await completed_tp.wait_call()

    total_after = await _get_total_event_count_metric(
        get_single_metric_by_label_values,
        taxi_grocery_wms_gateway_monitor,
        metric_tag,
    )

    failed_after = await _get_failed_event_count_metric(
        get_single_metric_by_label_values,
        taxi_grocery_wms_gateway_monitor,
        metric_tag,
    )

    assert response.status_code == 200
    if uri == '/v1/event':
        assert response.json()['code'] == 'OK'
    else:
        assert response.json()['details']['results'][0]['code'] == 'ERROR'

    assert total_after - total_before == 1
    assert failed_after - failed_before == 1
    assert (
        mock_processing.times_called + mock_eats_order_history.times_called > 0
    )
