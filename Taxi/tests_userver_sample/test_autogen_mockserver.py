async def test_mockserver_ok(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    def _handler(request):
        return {}

    response = await taxi_userver_sample.get('autogen/mockserver/test')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


async def test_mockserver_invalid_nonjson(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    def _handler(request):
        return ''

    response = await taxi_userver_sample.get('autogen/mockserver/test')
    assert response.status_code == 200
    assert response.json()['status'] == 'error'


async def test_mockserver_invalid_schema(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    def _handler(request):
        return {'field1': 1}

    response = await taxi_userver_sample.get('autogen/mockserver/test')
    assert response.status_code == 200
    assert response.json()['status'] == 'error'


async def test_mockserver_timeout_error(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    async def _handler(request):
        raise mockserver.TimeoutError()

    response = await taxi_userver_sample.get('autogen/mockserver/test')
    assert response.status_code == 200
    assert response.json() == {
        'status': 'timeout_error',
        'message': (
            'Error in \'GET /autogen/empty\': Timeout happened, url: '
            + mockserver.base_url
            + 'userver-sample/autogen/empty'
        ),
    }


async def test_mockserver_network_error(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    def _handler(request):
        raise mockserver.NetworkError()

    response = await taxi_userver_sample.get('autogen/mockserver/test')
    assert response.status_code == 200
    assert response.json() == {
        'status': 'error',
        'message': (
            'Error in \'GET /autogen/empty\': '
            'Network problem, curl error: Couldn\'t connect to server, url: '
            + mockserver.base_url
            + 'userver-sample/autogen/empty'
        ),
    }
