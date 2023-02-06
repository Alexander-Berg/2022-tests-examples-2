import pytest
from tests_processing import util


API_CACHE_TESTSUITE_TIMEOUT = pytest.mark.config(
    API_CACHE_CLIENT_QOS={'__default__': {'attempts': 1, 'timeout-ms': 5000}},
)


@pytest.mark.parametrize(
    'caching_type',
    [
        pytest.param(
            'resource',
            marks=[
                pytest.mark.processing_queue_config(
                    'handler.yaml',
                    cached_resource_url=util.UrlMock('/resource'),
                    scope='testsuite',
                    queue='example',
                ),
            ],
        ),
        pytest.param(
            'request',
            marks=[
                pytest.mark.processing_queue_config(
                    'req-handler.yaml',
                    cached_resource_url=util.UrlMock('/resource'),
                    scope='testsuite',
                    queue='example',
                ),
            ],
        ),
    ],
)
@API_CACHE_TESTSUITE_TIMEOUT
async def test_simple_caching(mockserver, api_cache, processing, caching_type):
    item_id = '1'

    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return {'value': 'test'}

    await processing.testsuite.example.send_event(item_id, payload={})
    assert test_resource.times_called == 1
    await api_cache.check_requests(
        mockserver.base_url + 'resource:get', get=True, put=True,
    )

    await processing.testsuite.example.send_event(item_id, payload={})
    assert test_resource.times_called == 1
    await api_cache.check_requests(
        mockserver.base_url + 'resource:get', get=True,
    )


@pytest.mark.parametrize(
    'caching_type',
    [
        pytest.param(
            'resource',
            marks=[
                pytest.mark.processing_queue_config(
                    'handler.yaml',
                    cached_resource_url=util.UrlMock('/resource'),
                    scope='testsuite',
                    queue='example',
                ),
                pytest.mark.processing_queue_config(
                    'handler-2.yaml',
                    cached_resource_url=util.UrlMock('/resource'),
                    scope='testsuite',
                    queue='another',
                ),
            ],
        ),
        pytest.param(
            'request',
            marks=[
                pytest.mark.processing_queue_config(
                    'req-handler.yaml',
                    cached_resource_url=util.UrlMock('/resource'),
                    scope='testsuite',
                    queue='example',
                ),
                pytest.mark.processing_queue_config(
                    'req-handler-2.yaml',
                    cached_resource_url=util.UrlMock('/resource'),
                    scope='testsuite',
                    queue='another',
                ),
            ],
        ),
    ],
)
@API_CACHE_TESTSUITE_TIMEOUT
async def test_caching_two_queues(
        mockserver, api_cache, processing, caching_type,
):
    item_id = '1'

    @mockserver.json_handler('/resource')
    def test_resource(request):
        assert request.method == 'GET'
        return {'value': 'test'}

    await processing.testsuite.example.send_event(item_id, payload={})
    assert test_resource.times_called == 1
    await api_cache.check_requests(
        mockserver.base_url + 'resource:get', get=True, put=True,
    )

    await processing.testsuite.example.send_event(item_id, payload={})
    assert test_resource.times_called == 1
    await api_cache.check_requests(
        mockserver.base_url + 'resource:get', get=True,
    )

    await processing.testsuite.another.send_event(item_id, payload={})
    assert test_resource.times_called == 2
    await api_cache.check_requests(
        mockserver.base_url + 'resource:get', get=True, put=True,
    )

    await processing.testsuite.another.send_event(item_id, payload={})
    assert test_resource.times_called == 2
    await api_cache.check_requests(
        mockserver.base_url + 'resource:get', get=True,
    )
