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
async def test_idempotency_token_from_agl(
        processing, testpoint, use_ydb, use_fast_flow,
):
    idempotency_token = 'test_idempotenct_token'

    @testpoint('default-testpoint')
    def default_testpoint(data):
        assert data['extra-data']['idempotency-token'] == idempotency_token

    event_id = await processing.testsuite.example.send_event(
        item_id='123', payload={}, idempotency_token=idempotency_token,
    )
    assert event_id
    assert default_testpoint.times_called == 1
