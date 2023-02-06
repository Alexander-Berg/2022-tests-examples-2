import pytest


HTTP_RETRIES = 5
DEFAULT_CLIENT_QOS = {'__default__': {'attempts': 1, 'timeout-ms': 100}}
RETRIES_CLIENT_QOS = {
    '__default__': {'attempts': HTTP_RETRIES, 'timeout-ms': 100},
}
USERVER_STATISTICS_PREFIX = 'handler.userver-sample./autogen/empty-get.'


@pytest.fixture(name='empty_echo_stats')
def _empty_echo_stats_impl(taxi_userver_sample, statistics):
    async def _empty_echo_stats(expect_http_code: int):
        async with statistics.capture(taxi_userver_sample) as capture:
            response = await taxi_userver_sample.get('external-echo-empty')
            assert response.status_code == expect_http_code

        return capture.statistics

    return _empty_echo_stats


@pytest.fixture(name='empty_echo_stats_fallback')
def _empty_echo_stats_fallback_impl(
        empty_echo_stats, taxi_userver_sample, statistics,
):
    async def _empty_echo_stats_fallback(expect_http_code: int):
        statistics.fallbacks = [USERVER_STATISTICS_PREFIX + 'fallback']
        await taxi_userver_sample.tests_control(invalidate_caches=True)
        return await empty_echo_stats(expect_http_code)

    return _empty_echo_stats_fallback


@pytest.mark.suspend_periodic_tasks('test-task-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_statistics_ok(empty_echo_stats, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    async def _handler(request):
        return {}

    stats = await empty_echo_stats(expect_http_code=200)
    assert stats[USERVER_STATISTICS_PREFIX + 'success'] == 1
    assert _handler.times_called == 1


@pytest.mark.config(USERVER_SAMPLE_CLIENT_QOS=DEFAULT_CLIENT_QOS)
@pytest.mark.suspend_periodic_tasks('test-task-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_statistics_network_error(empty_echo_stats, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    async def _handler(request):
        raise mockserver.NetworkError()

    stats = await empty_echo_stats(expect_http_code=500)
    assert stats[USERVER_STATISTICS_PREFIX + 'error'] == 1
    assert _handler.times_called == 1


@pytest.mark.config(USERVER_SAMPLE_CLIENT_QOS=DEFAULT_CLIENT_QOS)
@pytest.mark.suspend_periodic_tasks('test-task-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_statistics_timeout_error(empty_echo_stats, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    async def _handler(request):
        raise mockserver.TimeoutError()

    stats = await empty_echo_stats(expect_http_code=500)
    assert stats[USERVER_STATISTICS_PREFIX + 'error'] == 1
    assert stats[USERVER_STATISTICS_PREFIX + 'error.timeout'] == 1
    assert _handler.times_called == 1


@pytest.mark.config(USERVER_SAMPLE_CLIENT_QOS=RETRIES_CLIENT_QOS)
@pytest.mark.suspend_periodic_tasks('test-task-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_statistics_internal_server_error(empty_echo_stats, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    def _handler(request):
        return mockserver.make_response('Internal Server Error', status=500)

    stats = await empty_echo_stats(expect_http_code=500)
    assert stats[USERVER_STATISTICS_PREFIX + 'error'] == 1
    assert _handler.times_called == HTTP_RETRIES


@pytest.mark.config(USERVER_SAMPLE_CLIENT_QOS=RETRIES_CLIENT_QOS)
@pytest.mark.suspend_periodic_tasks('test-task-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_statistics_too_many_requests(empty_echo_stats, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    def _handler(request):
        return mockserver.make_response('Too Many Requests', status=429)

    # Code 429 is not in schema, but is propagated automatically
    stats = await empty_echo_stats(expect_http_code=429)
    assert stats[USERVER_STATISTICS_PREFIX + 'error'] == 1
    assert _handler.times_called == 1


@pytest.mark.config(USERVER_SAMPLE_CLIENT_QOS=RETRIES_CLIENT_QOS)
@pytest.mark.suspend_periodic_tasks('test-task-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_statistics_bad_request(empty_echo_stats, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    def _handler(request):
        return mockserver.make_response('Bad Request', status=400)

    # Code 400 is not in schema -> 500
    # We treat that case in stats as a success
    stats = await empty_echo_stats(expect_http_code=500)
    assert stats[USERVER_STATISTICS_PREFIX + 'success.4xx'] == 1
    assert _handler.times_called == 1


@pytest.mark.config(USERVER_SAMPLE_CLIENT_QOS=RETRIES_CLIENT_QOS)
@pytest.mark.suspend_periodic_tasks('test-task-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_statistics_fallback_on_internal_server_error(
        empty_echo_stats_fallback, mockserver,
):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    async def _handler(request):
        return mockserver.make_response('Internal Server Error', status=500)

    stats = await empty_echo_stats_fallback(expect_http_code=500)
    assert stats[USERVER_STATISTICS_PREFIX + 'error'] == 1
    assert _handler.times_called == 1


@pytest.mark.config(USERVER_SAMPLE_CLIENT_QOS=RETRIES_CLIENT_QOS)
@pytest.mark.suspend_periodic_tasks('test-task-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_statistics_fallback_on_timeout(
        empty_echo_stats_fallback, mockserver,
):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    async def _handler(request):
        raise mockserver.TimeoutError()

    stats = await empty_echo_stats_fallback(expect_http_code=500)
    assert stats[USERVER_STATISTICS_PREFIX + 'error'] == 1
    assert stats[USERVER_STATISTICS_PREFIX + 'error.timeout'] == 1
    assert _handler.times_called == 1


async def test_statistics_prefix(
        taxi_userver_sample, taxi_userver_sample_monitor,
):
    response = await taxi_userver_sample_monitor.get(
        '', params={'prefix': 'engine'},
    )
    assert response.status == 200
    # no extra keys
    assert set(response.json().keys()) == {'$version', 'engine'}

    response = await taxi_userver_sample_monitor.get(
        '', params={'prefix': 'engi'},
    )
    assert response.status == 200
    assert set(response.json().keys()) == {'$version', 'engine'}

    response = await taxi_userver_sample_monitor.get(
        '', params={'prefix': 'engine.x'},
    )
    assert response.status == 200
    assert set(response.json().keys()) == {'$version', 'engine'}
