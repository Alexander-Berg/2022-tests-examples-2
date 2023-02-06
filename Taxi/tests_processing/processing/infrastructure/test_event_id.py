import pytest


@pytest.mark.processing_queue_config(
    'queue.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize(
    'legacy_id',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    PROCESSING_DETERMINISTIC_EVENT_ID={'testsuite': False},
                ),
            ],
        ),
    ],
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
async def test_event_id(
        processing, testpoint, legacy_id, use_ydb, use_fast_flow,
):
    idempotency_token = 'test_idempotency_token'
    event_id_old = await processing.testsuite.example.send_event(
        item_id='123', payload={}, idempotency_token=idempotency_token,
    )
    event_id_new = await processing.testsuite.example.send_event(
        item_id='123', payload={}, idempotency_token=idempotency_token,
    )
    event_id_newest = await processing.testsuite.example.send_event(
        item_id='123',
        payload={},
        idempotency_token=idempotency_token + '_new',
    )
    assert event_id_old == event_id_new
    assert event_id_new != event_id_newest
