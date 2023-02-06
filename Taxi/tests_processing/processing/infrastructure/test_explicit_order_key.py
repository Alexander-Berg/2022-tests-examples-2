import pytest


@pytest.mark.processing_queue_config(
    'explicit_order_key.yaml', scope='testsuite', queue='example',
)
@pytest.mark.experiments3(filename='use_ydb.json')
@pytest.mark.experiments3(filename='ydb_flow.json')
async def test_ydb_explicit_order_key(processing, ydb):
    queue = processing.testsuite.example
    item_id = '1234'
    order_ids = [2, 57, 179]
    event_ids = []
    for order_id in order_ids:
        event_id = await queue.send_event(item_id, {'order-key': order_id})
        event_ids.append(event_id)

    events = await queue.events(item_id)
    ordered_event_ids = [event['event_id'] for event in events['events']]
    assert event_ids == ordered_event_ids
