import uuid

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
async def test_reflections(processing, testpoint, use_ydb, use_fast_flow):
    @testpoint('default-testpoint')
    def default_testpoint(data):
        assert data['extra-data']['handler-data'] == {
            'name': 'default-handler',
            'is_fallbacking': False,
        }
        assert data['extra-data']['stage-data'] == {
            'name': 'default-stage',
            'is_fallbacking': False,
        }
        assert data['extra-data']['pipeline-data'] == {
            'name': 'default-pipeline',
            'is_fallbacking': False,
        }
        try:
            tracing = data['extra-data']['tracing-data']
            uuid.UUID(tracing['link'])
        except ValueError:
            assert False

    event_id = await processing.testsuite.example.send_event(
        item_id='123', payload={}, idempotency_token='foo',
    )

    assert event_id
    assert default_testpoint.times_called == 1
