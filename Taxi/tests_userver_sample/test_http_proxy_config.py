import aiohttp

import testsuite

#  ->  userver-sample       ->  _handler       ->  userver-sample     ->  test
async def test_config_update_after_broken_proxy(
        taxi_userver_sample, taxi_config, mockserver,
):
    @mockserver.json_handler('/userver-sample/openapi/empty_response_body')
    async def _handler(request):
        return mockserver.make_response(b'', 204)

    taxi_config.set_values({'USERVER_HTTP_PROXY': '/bad-proxy'})
    try:
        # At least the second should fail:
        await taxi_userver_sample.invalidate_caches()
        await taxi_userver_sample.get('/openapi/empty_response_body')
        assert False, 'Service is not in a broken state'
    except (
        testsuite.utils.http.HttpResponseError,
        aiohttp.client_exceptions.ClientResponseError,
    ):
        pass
    assert _handler.times_called == 0, 'HTTP client should be broken'

    taxi_config.set_values({'USERVER_HTTP_PROXY': ''})
    # Now everything should work fine:

    response = await taxi_userver_sample.get('/openapi/empty_response_body')
    assert _handler.times_called == 1
    assert response.status_code == 204
    assert response.content == b''

    await taxi_userver_sample.invalidate_caches()
