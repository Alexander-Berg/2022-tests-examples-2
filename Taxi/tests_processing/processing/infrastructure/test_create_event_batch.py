import pytest


# A message to the people of 5022. You must be noticed that this test
# is not passing anymore. Don't panic, this is expected behavior.
# A little action required from you: just replace 5022 to 6022
# (update this disclaimer as well) and everything will back to normal.
# Best wishes and have a nice and productive workday!
_PAST = '1970-01-01T00:00:00.000Z'
_FUTURE = '5022-01-01T00:00:00.000Z'


@pytest.mark.processing_queue_config(
    'delta.yaml', scope='testsuite', queue='delta',
)
@pytest.mark.processing_queue_config(
    'omicron.yaml', scope='testsuite', queue='omicron',
)
@pytest.mark.parametrize('payload', [None, {'foo': 'bar'}])
@pytest.mark.parametrize('due', [None, _PAST, _FUTURE])
async def test_create_event_batch_happy_path(taxi_processing, payload, due):
    request_body = {
        'events': [
            {'queue': 'delta', 'item-id': '0000', 'idempotency-token': '0000'},
            {'queue': 'delta', 'item-id': '1111', 'idempotency-token': '1111'},
            {
                'queue': 'omicron',
                'item-id': '2222',
                'idempotency-token': '2222',
            },
        ],
    }
    if payload:
        for event in request_body['events']:
            event.update({'payload': payload})
    if due:
        for event in request_body['events']:
            event.update({'due': due})
    event_ids = []
    for _ in range(3):
        # repeat calls to ensure idempotency
        response = await taxi_processing.post(
            '/v1/testsuite/create-event-batch', json=request_body,
        )
        assert response.status_code == 200
        event_ids = response.json()['event_ids']
        assert len(event_ids) == len(request_body['events'])

    visible = []
    for event in request_body['events']:
        queue = event['queue']
        item_id = event['item-id']
        response = await taxi_processing.get(
            f'/v1/testsuite/{queue}/events?item_id={item_id}'
            f'&allow_restore=false',
        )
        assert response.status_code == 200
        events = response.json()['events']
        visible += events

    if due == _FUTURE:
        assert not visible
    else:
        assert [i['event_id'] for i in visible] == event_ids
        assert [i.get('payload') for i in visible] == [
            i.get('payload') for i in request_body['events']
        ]


@pytest.mark.processing_queue_config(
    'delta.yaml', scope='testsuite', queue='delta',
)
async def test_create_event_batch_bad_queue(taxi_processing):
    request_body = {
        'events': [
            {'queue': 'delta', 'item-id': '0000', 'idempotency-token': '0000'},
            {'queue': 'foo', 'item-id': '1111', 'idempotency-token': '1111'},
        ],
    }
    response = await taxi_processing.post(
        '/v1/testsuite/create-event-batch', json=request_body,
    )
    assert response.status_code == 400
    response = await taxi_processing.get(
        f'/v1/testsuite/delta/events?item_id=0000&allow_restore=false',
    )
    assert response.status_code == 200
    assert not response.json()['events']


@pytest.mark.processing_queue_config(
    'delta.yaml', scope='testsuite', queue='delta',
)
@pytest.mark.config(
    PROCESSING_DISABLED_QUEUES=[{'scope': 'testsuite', 'queue': 'delta'}],
)
async def test_create_event_batch_disabled(taxi_processing):
    request_body = {
        'events': [
            {'queue': 'delta', 'item-id': '0000', 'idempotency-token': '0000'},
        ],
    }
    response = await taxi_processing.post(
        '/v1/testsuite/create-event-batch', json=request_body,
    )
    assert response.status_code == 503


@pytest.mark.processing_queue_config(
    'delta.yaml', scope='testsuite', queue='delta',
)
@pytest.mark.experiments3(filename='use_ydb.json')
@pytest.mark.experiments3(filename='ydb_flow.json')
async def test_create_event_batch_explicit_order_key(taxi_processing):
    order_ids = [2, 57, 179]
    request_body = {
        'events': [
            {
                'queue': 'delta',
                'item-id': '0000',
                'idempotency-token': '%s' % str(order_id),
                'payload': {'order_key': order_id},
            }
            for order_id in order_ids
        ],
    }
    handle_response = await taxi_processing.post(
        '/v1/testsuite/create-event-batch', json=request_body,
    )
    event_ids = handle_response.json()['event_ids']
    assert handle_response.status_code == 200
    response = await taxi_processing.get(
        f'/v1/testsuite/delta/events?item_id=0000',
    )
    assert response.status_code == 200
    events = response.json()['events']
    ordered_event_ids = [event['event_id'] for event in events]
    assert event_ids == ordered_event_ids
