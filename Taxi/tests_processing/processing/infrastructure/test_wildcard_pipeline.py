import pytest


@pytest.mark.processing_queue_config(
    'handler.yaml', scope='testsuite', queue='example',
)
async def test_ignore_policy(processing):
    item_id = '1'

    shared_state = await processing.testsuite.example.handle_single_event(
        item_id, payload={},
    )
    assert shared_state['handler-result'] == {'result': 'some-data'}
