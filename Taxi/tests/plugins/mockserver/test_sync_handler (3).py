import inspect

from taxi_tests import http


async def test_request_wrapper_attributes(mockserver, create_service_client):
    @mockserver.handler('/arbitrary/path', prefix=True)
    def handler(request: http.Request):
        assert request.method == 'POST'
        assert request.url == mockserver.base_url + 'arbitrary/path?k=v'
        assert request.path == '/arbitrary/path'
        assert request.query_string == b'k=v'
        assert request.get_data() == b'some data'
        assert len(request.args) == 1
        assert request.args['k'] == 'v'
        assert request.headers['arbitrary-header'] == 'value'

        return mockserver.make_response()

    client = create_service_client(
        mockserver.base_url, service_headers={'arbitrary-header': 'value'},
    )
    response = await client.post('arbitrary/path?k=v', data=b'some data')
    assert response.status_code == 200


async def test_response_attributes(mockserver, create_service_client):
    @mockserver.handler('/arbitrary/path')
    def handler(request):
        return mockserver.make_response(
            response='forbidden',
            status=403,
            headers={'arbitrary-header': 'value'},
        )

    client = create_service_client(mockserver.base_url)
    response = await client.post('arbitrary/path')
    assert response.status_code == 403
    assert response.headers['arbitrary-header'] == 'value'
    assert response.text == 'forbidden'


async def test_request_json(mockserver, create_service_client):
    @mockserver.handler('/arbitrary/path')
    def handler(request: http.Request):
        assert request.json == {'k': 'v'}
        return mockserver.make_response()

    client = create_service_client(mockserver.base_url)
    response = await client.post('arbitrary/path', data='{"k": "v"}')
    assert response.status_code == 200


async def test_response_json(mockserver, create_service_client):
    @mockserver.json_handler('/arbitrary/path')
    def handler(request):
        return {'k': 'v'}

    client = create_service_client(mockserver.base_url)
    response = await client.post('arbitrary/path')
    assert response.status_code == 200
    json_response = response.json()
    assert json_response == {'k': 'v'}


async def test_raw_request_parameter(mockserver, create_service_client):
    @mockserver.json_handler('/arbitrary/path', raw_request=True)
    async def handler(request):
        is_json_method_async = inspect.iscoroutinefunction(request.json)
        # the non-wrapped request has async json method.
        assert is_json_method_async
        return mockserver.make_response()

    client = create_service_client(mockserver.base_url)
    response = await client.post('arbitrary/path')
    assert response.status_code == 200


async def test_request_form(mockserver, create_service_client):
    @mockserver.json_handler('/arbitrary/path')
    async def handler(request):
        form = request.form
        assert form == {'key1': 'val1', 'key2': 'val2'}
        return mockserver.make_response()

    client = create_service_client(mockserver.base_url)
    response = await client.post(
        'arbitrary/path',
        headers={'content-type': 'application/x-www-form-urlencoded'},
        data='key1=val1&key2=val2',
    )
    assert response.status_code == 200
