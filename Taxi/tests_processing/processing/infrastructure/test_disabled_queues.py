import pytest


@pytest.mark.config(
    PROCESSING_DISABLED_QUEUES=[{'scope': 'testsuite', 'queue': 'example'}],
)
@pytest.mark.processing_queue_config(
    'simple_example.yaml', scope='testsuite', queue='example',
)
async def test_handling_order_key(taxi_processing, pgsql):
    item_id = '123456789'
    resp = await taxi_processing.post(
        '/v1/testsuite/example/create-event',
        params={'item_id': item_id},
        headers={'X-Idempotency-Token': 'token'},
        json={},
    )
    assert resp.status_code == 503

    resp = await taxi_processing.get(
        '/v1/testsuite/example/events',
        params={'item_id': item_id},
        headers={},
        json={},
    )
    assert resp.status_code == 503
