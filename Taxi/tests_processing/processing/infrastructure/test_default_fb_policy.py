import pytest

from tests_processing import util


@pytest.mark.processing_queue_config(
    'default.yaml',
    scope='testsuite',
    queue='example',
    fallback_resource_url=util.UrlMock('/fallback'),
)
@pytest.mark.parametrize('fallback_activate', [False, True])
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
async def test_default_fb_policy(
        stq,
        mockserver,
        testpoint,
        fallback_activate,
        mocked_time,
        processing,
        use_ydb,
        use_fast_flow,
):
    item_id = '1'

    @mockserver.json_handler('/fallback')
    def mock_fallback(request):
        if fallback_activate:
            return mockserver.make_response(status=500)
        return {'result': 'ok'}

    shared_state = await processing.testsuite.example.handle_single_event(
        item_id, payload={},
    )
    assert mock_fallback.times_called == 1

    if fallback_activate:
        assert shared_state['default-handler-result'] == {'result': 'fallback'}
    else:
        assert shared_state['default-handler-result'] == {'result': 'ok'}


@pytest.mark.processing_queue_config(
    'custom.yaml',
    scope='testsuite',
    queue='example',
    fallback_resource_url=util.UrlMock('/fallback'),
)
@pytest.mark.parametrize('fallback_activate', [False, True])
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
async def test_custom_fb_policy(
        stq,
        mockserver,
        testpoint,
        fallback_activate,
        mocked_time,
        processing,
        use_ydb,
        use_fast_flow,
):
    item_id = '1'

    @mockserver.json_handler('/fallback')
    def mock_fallback(request):
        if fallback_activate:
            return mockserver.make_response(status=500)
        return {'result': 'ok'}

    shared_state = await processing.testsuite.example.handle_single_event(
        item_id, payload={},
    )
    assert mock_fallback.times_called == 1

    if fallback_activate:
        assert shared_state['custom-handler-result'] == {'result': 'fallback'}
    else:
        assert shared_state['custom-handler-result'] == {'result': 'ok'}


@pytest.mark.processing_queue_config(
    'on-fallbacking.yaml', scope='testsuite', queue='example',
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
async def test_default_on_fb(
        stq, processing, statistics, taxi_processing, use_ydb, use_fast_flow,
):
    statistics.fallbacks = [
        'processing.handler.testsuite.example.default-on-fb.fallback',
        'processing.handler.testsuite.example.custom-on-fb.fallback',
    ]
    await taxi_processing.invalidate_caches()

    item_id = '1'
    shared_state = await processing.testsuite.example.handle_single_event(
        item_id, payload={},
    )
    assert not shared_state.get('default-handler-called', False)
    assert shared_state.get('custom-handler-called', False)
