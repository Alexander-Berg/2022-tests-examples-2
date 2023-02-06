TEST_DATA = {'value': 'message111'}


async def test_echo_simple(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/echo-extra-client')
    def _handler(request):
        return mockserver.make_response(json={'value': request.query['value']})

    response = await taxi_userver_sample.get(
        'autogen/echo-extra-client', params=TEST_DATA,
    )
    assert response.status_code == 200
    assert response.json() == TEST_DATA
    assert _handler.times_called == 1


async def test_echo_new_value(taxi_userver_sample, mockserver, taxi_config):
    @mockserver.json_handler('/userver-sample/autogen/echo-extra-client')
    def _default_handler(request):
        return mockserver.make_response(json={'value': request.query['value']})

    @mockserver.json_handler('/other-service/autogen/echo-extra-client')
    def _new_handler(request):
        return mockserver.make_response(json={'value': request.query['value']})

    response = await taxi_userver_sample.get(
        'autogen/echo-extra-client', params=TEST_DATA,
    )
    assert response.status_code == 200
    assert response.json() == TEST_DATA
    assert _default_handler.times_called == 1
    assert _new_handler.times_called == 0

    taxi_config.set_values(
        {
            'USERVER_SAMPLE_EXTRA_CLIENT': {
                'base_url': mockserver.url('/other-service'),
                'tvm_name': 'userver-sample',
            },
        },
    )
    await taxi_userver_sample.invalidate_caches()

    response = await taxi_userver_sample.get(
        'autogen/echo-extra-client', params=TEST_DATA,
    )
    assert response.status_code == 200
    assert response.json() == TEST_DATA
    assert _default_handler.times_called == 1  # no new calls
    assert _new_handler.times_called == 1
