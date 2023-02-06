import pytest


@pytest.mark.parametrize('enable_fallback', [False, True])
async def test_statistics_fallback(
        taxi_api_proxy,
        resources,
        endpoints,
        statistics,
        mockserver,
        load_yaml,
        enable_fallback,
):
    @mockserver.json_handler('/mainland-service')
    def _mock_mainland_service(request):
        return {'result': 'mainland data'}

    @mockserver.json_handler('/reserve-service')
    def _mock_reserve_service(request):
        return {'result': 'reserve data'}

    # create resource
    await resources.safely_create_resource(
        resource_id='mainland-resource',
        url=mockserver.url('mainland-service'),
        method='post',
    )

    await resources.safely_create_resource(
        resource_id='reserve-resource',
        url=mockserver.url('reserve-service'),
        method='post',
    )

    # create an endpoint
    handler_def = load_yaml('fallback_handler.yaml')
    path = '/tests/api-proxy/handler-with-fallback'
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # perform parametrization
    expected_reponse = {'result': 'mainland data'}
    if enable_fallback:
        statistics.fallbacks = ['resource.mainland-resource.fallback']
        await taxi_api_proxy.invalidate_caches()
        expected_reponse = {'result': 'reserve data'}

    # call the handler
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == expected_reponse


@pytest.mark.parametrize('enable_fallback', [False, True])
async def test_statistics_send(
        taxi_api_proxy,
        resources,
        endpoints,
        mockserver,
        statistics,
        load_yaml,
        enable_fallback,
):
    still_alive = True

    @mockserver.json_handler('/foo')
    def _mock_foo(request):
        if still_alive:
            return {'foo': 'foo'}
        return mockserver.make_response('expected fail', status=500)

    # create resource
    await resources.safely_create_resource(
        resource_id='foo', url=mockserver.url('foo'), method='post',
    )

    # create an endpoint
    handler_def = load_yaml('send_handler.yaml')
    path = '/tests/api-proxy/handler-with-fallback'
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # make a call
    async with statistics.capture(taxi_api_proxy) as capture:
        response = await taxi_api_proxy.get(path)
        assert response.status_code == 200
        assert response.json() == {'foo': 'foo'}

        still_alive = False

        if enable_fallback:
            statistics.fallbacks = ['resource.foo.fallback']
            await taxi_api_proxy.invalidate_caches()

        response = await taxi_api_proxy.get(path)
        assert response.status_code == 500

        response = await taxi_api_proxy.get(path)
        assert response.status_code == 500

    if enable_fallback:
        assert capture.statistics['resource.foo.success'] == 1
    else:
        assert capture.statistics['resource.foo.success'] == 1
        assert capture.statistics['resource.foo.error.http.500'] == 2


@pytest.mark.parametrize('enable_fallback', [False, True])
async def test_statistics_retries_fallback(
        taxi_api_proxy,
        resources,
        endpoints,
        statistics,
        mockserver,
        load_yaml,
        enable_fallback,
):
    @mockserver.json_handler('/upstream')
    def upstream(request):
        return mockserver.make_response('expected fail', status=500)

    await resources.safely_create_resource(
        resource_id='upstream',
        url=mockserver.url('upstream'),
        method='get',
        max_retries=3,
    )

    # create an endpoint
    handler_def = load_yaml('retries_fallback_handler.yaml')
    await endpoints.safely_create_endpoint('/do', get_handler=handler_def)

    if enable_fallback:
        statistics.fallbacks = ['resource.upstream.fallback.retries']
        await taxi_api_proxy.invalidate_caches()

    # call the handler
    response = await taxi_api_proxy.get('/do')
    assert response.status_code == 200
    assert response.text == 'expected fail'
    if enable_fallback:
        assert upstream.times_called == 1
    else:
        assert upstream.times_called == 3
