import pytest

from tests_processing import util  # noqa


@pytest.mark.processing_queue_config(
    'producer-queue.yaml', scope='testsuite', queue='producer',
)
@pytest.mark.processing_queue_config(
    'worker-queue.yaml',
    json_handler_url=util.UrlMock('/json-handler'),
    scope='testsuite',
    queue='worker',
)
async def test_create_event_handler(taxi_processing, processing):
    item_id = '1'
    await processing.testsuite.producer.send_event(
        item_id, payload={'worker': {'test': 'body'}}, expect_fail=False,
    )

    response = await taxi_processing.get(
        '/v1/testsuite/worker/events',
        params={'item_id': item_id, 'allow_restore': False},
    )
    assert response.status_code == 200
    events = response.json()['events']
    assert len(events) == 1
    assert events[0]['payload'] == {'test': 'body'}


@pytest.mark.processing_queue_config(
    'producer-batch-queue.yaml', scope='testsuite', queue='producer',
)
@pytest.mark.processing_queue_config(
    'worker-queue-0.yaml',
    json_handler_url=util.UrlMock('/json-handler'),
    scope='testsuite',
    queue='worker_0',
)
@pytest.mark.processing_queue_config(
    'worker-queue-1.yaml',
    json_handler_url=util.UrlMock('/json-handler'),
    scope='testsuite',
    queue='worker_1',
)
@pytest.mark.processing_queue_config(
    'worker-queue-2.yaml',
    json_handler_url=util.UrlMock('/json-handler'),
    scope='testsuite',
    queue='worker_2',
)
@pytest.mark.parametrize(
    'item_id,batch,success',
    [
        pytest.param(
            1,
            [
                {
                    'queue': f'worker_{idx}',
                    'item-id': '1',
                    'idempotency-token': f'1_{idx}',
                    'payload': {'counter': idx},
                }
                for idx in range(3)
            ],
            True,
            id='good-path',
        ),
        pytest.param(
            2,
            [
                {
                    'queue': f'worker_{idx}',
                    'item-id': '2',
                    'idempotency-token': f'planned-in-q{idx}',
                    'due': 'Q5',
                    'payload': {'counter': idx},
                }
                for idx in range(3)
            ],
            False,
            id='too-late',
        ),
    ],
)
async def test_create_batch_events_handler(
        taxi_processing, processing, item_id, batch, success,
):
    await processing.testsuite.producer.send_event(
        str(item_id), payload={'batch-events': batch}, expect_fail=not success,
    )

    global_order = []
    only_payload = lambda lst: [i['payload'] for i in lst]
    for idx in range(3):
        queue = f'worker_{idx}'
        resp_events = await taxi_processing.get(
            f'/v1/testsuite/{queue}/events',
            params={'item_id': item_id, 'allow_restore': False},
        )
        assert resp_events.status_code == 200
        events = resp_events.json()['events']
        global_order += events
        if success:
            partial_batch = [i for i in batch if i['queue'] == queue]
            assert len(events) == len(partial_batch)
            assert only_payload(events) == only_payload(partial_batch)
        else:
            assert events == []
    assert only_payload(global_order) == only_payload(batch if success else [])
