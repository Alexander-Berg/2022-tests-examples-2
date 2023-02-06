import pytest

from tests_processing import util


@pytest.mark.processing_queue_config(
    'failed-handler.yaml',
    bad_handler_url=util.UrlMock('/bad-handle'),
    scope='failed_handler_test',
    queue='example',
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
async def test_handler_failure(
        processing, testpoint, mockserver, use_ydb, use_fast_flow,
):
    queue = processing.failed_handler_test.example

    @mockserver.json_handler('/bad-handle')
    def bad_handler(request):
        return mockserver.make_response('internal error', status=500)

    final_shared_state = await queue.handle_single_event(
        '1233456',
        payload={},
        prev_state={},
        curr_state={},
        pipeline='default-pipeline',
        stage_id='fail-the-handler-stage',
    )
    assert final_shared_state['request-enabled'] is False
    assert bad_handler.times_called != 0
