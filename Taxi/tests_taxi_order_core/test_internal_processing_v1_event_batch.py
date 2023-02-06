import uuid

import bson
import pytest


@pytest.mark.now('2021-04-12T12:55:00Z')
async def test_events_batch(taxi_order_core, stq, now, mongodb, mockserver):
    @mockserver.json_handler('/processing/v1/taxi/orders/create-event')
    def mock_processing_post_event(request):
        return {'event_id': '123456'}

    mongodb.order_proc.update(
        {'_id': 'foo'}, {'$set': {'order_info.process_by_procaas': True}},
    )
    request = {}
    request['filter'] = {'order.status': 'pending'}
    request['events'] = [
        {
            'event_key': 'assign',
            'event_extra_payload': {'s': 'assigned', 'i': 0},
        },
        {
            'event_key': 'drive',
            'event_extra_payload': {'t': 'driving', 'i': 0},
        },
    ]
    request['extra_update'] = {
        '$set': {
            'performer.candidate_index': 0,
            'order.status': 'assigned',
            'order.taxi_status': 'driving',
        },
    }
    request['fields'] = [
        'order.status',
        'order.taxi_status',
        'performer.candidate_index',
        'order_info.statistics.status_updates',
    ]

    idempotency_token = uuid.uuid4().hex
    with stq.flushing():
        response = await taxi_order_core.post(
            '/internal/processing/v1/event-batch?order_id=foo',
            headers={
                'X-Idempotency-Token': idempotency_token,
                'Content-Type': 'application/bson',
            },
            data=bson.BSON.encode(request),
        )
        assert stq['processing'].times_called == 0

    assert response.status_code == 200
    proc: dict = bson.BSON.decode(response.content)
    assert proc
    assert 'order' in proc
    assert proc['order']['status'] == 'assigned'
    assert proc['order']['taxi_status'] == 'driving'
    assert proc['performer']['candidate_index'] == 0

    events = proc['order_info']['statistics']['status_updates']
    assert events[1:] == [
        {
            'c': now,
            'h': True,
            's': 'assigned',
            'q': 'assign',
            'i': 0,
            'x-idempotency-token': idempotency_token,
        },
        {
            'c': now,
            'h': True,
            't': 'driving',
            'q': 'drive',
            'i': 0,
            'x-idempotency-token': idempotency_token,
        },
    ]
    processing_event_request = mock_processing_post_event.next_call()[
        'request'
    ]
    assert processing_event_request.json == {
        'i': 0,
        'q': 'assign',
        's': 'assigned',
        'event-index': 1,
    }
    assert processing_event_request.headers['X-Idempotency-Token'] == 'foo_e1'

    processing_event_request = mock_processing_post_event.next_call()[
        'request'
    ]
    assert processing_event_request.json == {
        'i': 0,
        'q': 'drive',
        't': 'driving',
        'event-index': 2,
    }
    assert processing_event_request.headers['X-Idempotency-Token'] == 'foo_e2'
    assert mock_processing_post_event.times_called == 0


@pytest.mark.parametrize(
    'events,expected_code',
    [
        ([], 400),
        ([{'event_key': 'restart-processing'}], 200),
        ([{'event_key': 'restart-processing'}, {'event_key': 'a'}], 400),
        ([{'event_key': 'some'}], 200),
    ],
)
async def test_edge_cases(taxi_order_core, events, expected_code, mockserver):
    @mockserver.json_handler('/processing/v1/taxi/orders/create-event')
    def _mock_processing_create_event(request):
        return {'event_id': '123456'}

    @mockserver.json_handler('/processing/v1/taxi/orders/events')
    def _mock_processing_events(request):
        return {'events': []}

    params = {'order_id': 'foo'}
    response = await taxi_order_core.post(
        f'/internal/processing/v1/event-batch/',
        params=params,
        headers={
            'X-Idempotency-Token': 'abc',
            'Content-Type': 'application/bson',
        },
        data=bson.BSON.encode({'events': events}),
    )
    assert response.status_code == expected_code
