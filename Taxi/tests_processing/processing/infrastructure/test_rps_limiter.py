import pytest
from tests_processing import util

SET_TESTSUITE_TIMEOUTS = pytest.mark.config(
    STATISTICS_CLIENT_QOS={'__default__': {'attempts': 1, 'timeout-ms': 1000}},
    STATISTICS_RPS_LIMITER_PER_LIMITER_SETTINGS={
        '__default__': {'wait_request_duration': 2000},
    },
)

RESOURCE_NAME = 'broken-resource'
RESOURCE_STAT_UUID = f'testsuite.example.{RESOURCE_NAME}'
THROTTLE_FALLBACK = f'resource.{RESOURCE_STAT_UUID}.fallback.throttle'
RETRIES_FALLBACK = f'resource.{RESOURCE_STAT_UUID}.fallback.retries'


@pytest.mark.parametrize(
    'is_single_pipeline',
    [
        pytest.param(
            False,
            marks=[
                pytest.mark.processing_queue_config(
                    'handler.yaml',
                    broken_resource_url=util.UrlMock('/broken-resource'),
                    scope='testsuite',
                    queue='example',
                ),
            ],
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.processing_pipeline_config(
                    'handler-single-pipeline.yaml',
                    broken_resource_url=util.UrlMock('/broken-resource'),
                    scope='testsuite',
                    single_pipeline='example',
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'fallbacks, limiter_budget, fired',
    [
        ([THROTTLE_FALLBACK], 0, 'throttle'),
        ([THROTTLE_FALLBACK], 2, 'throttle'),
        ([THROTTLE_FALLBACK], 10, 'throttle'),
        ([RETRIES_FALLBACK], 10, 'retries'),
        ([THROTTLE_FALLBACK, RETRIES_FALLBACK], 2, 'all'),
        ([THROTTLE_FALLBACK, RETRIES_FALLBACK], 10, 'all'),
    ],
)
@SET_TESTSUITE_TIMEOUTS
@pytest.mark.config(
    BROKEN_RESOURCE_QOS={'__default__': {'attempts': 5, 'timeout-ms': 1000}},
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
async def test_rps_limiter_throttle_and_retries(
        taxi_processing,
        fallbacks,
        limiter_budget,
        fired,
        mockserver,
        rps_limiter,
        processing,
        statistics,
        testpoint,
        use_ydb,
        use_fast_flow,
        is_single_pipeline,
):
    statistics.fallbacks = fallbacks
    await taxi_processing.invalidate_caches()

    rps_limiter.set_budget(RESOURCE_NAME, limiter_budget)

    @mockserver.json_handler('/broken-resource')
    def mock_upstream(request):
        return mockserver.make_response(status=500)

    @testpoint('Sequencer::LimiterThrottleRequest')
    def throttle_branch(data):
        pass

    @testpoint('Sequencer::LimiterRetriesRequest')
    def retries_branch(data):
        pass

    iterations = 5
    for i in range(iterations):
        item_id = str(i + 1)
        if is_single_pipeline:
            await processing.testsuite.example.run_pipeline(
                item_id, payload={},
            )
        else:
            await processing.testsuite.example.send_event(item_id, payload={})

    if fired == 'throttle':
        assert mock_upstream.times_called == 5 * min(
            iterations, limiter_budget,
        )
        assert throttle_branch.times_called == iterations - min(
            iterations, limiter_budget,
        )
    if fired == 'retries':
        assert mock_upstream.times_called == iterations
        assert retries_branch.times_called == iterations
    if fired == 'all':
        assert mock_upstream.times_called == min(iterations, limiter_budget)
        assert retries_branch.times_called == iterations
        assert throttle_branch.times_called == iterations - min(
            iterations, limiter_budget,
        )
