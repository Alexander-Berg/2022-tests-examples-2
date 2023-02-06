import pytest


@pytest.mark.processing_queue_config(
    'queue.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_secdist_access(processing, testpoint, use_ydb, use_fast_flow):
    @testpoint('default-testpoint')
    def default_testpoint(data):
        assert data['extra-data'] == 'bar'

    event_id = await processing.testsuite.example.send_event(
        item_id='123', payload={}, idempotency_token='foo',
    )
    assert event_id
    assert default_testpoint.times_called == 1
