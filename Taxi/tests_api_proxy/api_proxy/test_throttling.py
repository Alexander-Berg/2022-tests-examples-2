import pytest

SET_TESTSUITE_TIMEOUTS = pytest.mark.config(
    STATISTICS_CLIENT_QOS={'__default__': {'attempts': 1, 'timeout-ms': 1000}},
    STATISTICS_RPS_LIMITER_PER_LIMITER_SETTINGS={
        '__default__': {'wait_request_duration': 2000},
    },
)


@pytest.mark.parametrize(
    'fallbacks, expected_result, limiter_budget, upstream_calls, '
    'throttle_requested',
    [
        ([], 'error', 10, 2, False),
        ([], 'error', 0, 2, False),
        (['resource.upstream.fallback'], 'fallback', 10, 0, False),
        (['resource.upstream.fallback'], 'fallback', 0, 0, False),
        (
            [
                'resource.upstream.fallback',
                'resource.upstream.fallback.throttle',
            ],
            'fallback',
            0,
            0,
            False,
        ),
        (['resource.upstream.fallback.throttle'], 'error', 10, 2, True),
        (['resource.upstream.fallback.throttle'], 'throttled', 0, 0, True),
    ],
)
@SET_TESTSUITE_TIMEOUTS
async def test_basic(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        load_yaml,
        mockserver,
        fallbacks,
        expected_result,
        limiter_budget,
        upstream_calls,
        statistics,
        throttle_requested,
):
    @mockserver.json_handler('/upstream')
    def mock_upstream(request):
        return mockserver.make_response(status=500)

    rps_limiter.set_budget('upstream', limiter_budget)
    statistics.fallbacks = fallbacks

    await resources.safely_create_resource(
        resource_id='upstream',
        url=mockserver.url('/upstream'),
        method='get',
        max_retries=2,
    )
    await endpoints.safely_create_endpoint(
        '/ep', get_handler=load_yaml('handler.yaml'),
    )

    response = await taxi_api_proxy.get('/ep')
    assert response.status_code == 200
    assert response.json() == {'result': expected_result}

    assert mock_upstream.times_called == upstream_calls

    if throttle_requested:
        await rps_limiter.wait_request(
            'api-proxy-resource-throttle-limiter', {'upstream'},
        )
    else:
        assert rps_limiter.call_count == 0
