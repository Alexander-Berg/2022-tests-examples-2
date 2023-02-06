import pytest

from tests_processing import util


@pytest.mark.processing_queue_config(
    'handler.yaml',
    ignore_fallback_resource_url=util.UrlMock('/fallback'),
    scope='testsuite',
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
@pytest.mark.parametrize('ignore_fallback_activate', [False, True])
async def test_ignore_policy(
        stq,
        mockserver,
        testpoint,
        ignore_fallback_activate,
        mocked_time,
        processing,
        use_ydb,
        use_fast_flow,
):
    item_id = '1'

    @mockserver.json_handler('/fallback')
    def mock_fallback(request):
        if ignore_fallback_activate:
            return mockserver.make_response(status=500)
        return {'result': 'ok'}

    shared_state = await processing.testsuite.example.handle_single_event(
        item_id, payload={},
    )
    assert mock_fallback.times_called == 1
    if ignore_fallback_activate:
        assert shared_state['ignore-handler-result'] == {'result': 'fallback'}
    else:
        assert shared_state['ignore-handler-result'] == {'result': 'ok'}
