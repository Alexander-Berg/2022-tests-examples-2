import pytest

from tests_processing import util

# pylint: disable=redefined-outer-name
@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]


@pytest.mark.processing_queue_config(
    'handler.yaml',
    fallback_resource_url=util.UrlMock('/fallback'),
    scope='testsuite',
    queue='example',
)
@pytest.mark.parametrize('failing_at_handler', [True, False])
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
async def test_send_statistics(
        stq,
        mockserver,
        failing_at_handler,
        processing,
        statistics,
        taxi_processing,
        use_ydb,
        use_fast_flow,
):
    item_id = '1'

    @mockserver.json_handler('/fallback')
    def mock_fallback(request):
        if failing_at_handler:
            return mockserver.make_response(status=500)
        return {'result': 'ok'}

    async with statistics.capture(taxi_processing) as capture:
        await processing.testsuite.example.send_event(
            item_id, payload={}, expect_fail=failing_at_handler,
        )

    for param in [
            'processing.pipeline.testsuite.example.default-pipeline',
            'processing.stage.testsuite.example.stage-1',
            'processing.handler.testsuite.example.fallback-handler',
    ]:
        assert (
            capture.statistics.get(f'{param}.success', 0) != failing_at_handler
        )
        assert (
            capture.statistics.get(f'{param}.error', 0) == failing_at_handler
        )
    assert mock_fallback.times_called == 1
