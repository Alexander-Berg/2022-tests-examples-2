import pytest

from tests_processing import util


@pytest.mark.processing_queue_config(
    'queue.yaml',
    scope='testsuite',
    queue='example',
    example_resource_url=util.UrlMock('/default-handle'),
)
@pytest.mark.parametrize(
    'resp_status,expected_result',
    [
        (200, {'error': False}),
        (409, {'error': True, 'catch-409': True}),
        (500, {'error': True, 'catch-409': False}),
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
async def test_multiselect_failure_policy_at_handler(
        processing,
        mockserver,
        resp_status,
        expected_result,
        use_ydb,
        use_fast_flow,
):
    queue = processing.testsuite.example

    @mockserver.json_handler('/default-handle')
    def default_handle(request):
        return mockserver.make_response('bar', status=resp_status)

    final_shared_state = await queue.handle_single_event(
        '1234567890',
        payload={},
        prev_state={},
        curr_state={},
        pipeline='default-pipeline',
        stage_id='default-stage',
    )
    assert final_shared_state == expected_result
    assert default_handle.times_called == 1
