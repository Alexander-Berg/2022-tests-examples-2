import pytest

from taxi_tests.daemons import service_client


@pytest.fixture
def taxi_protocol(mockserver, service_client_options):
    return service_client.Client(
        mockserver.base_url + 'test_protocol/',
        service_headers={mockserver.trace_id_header: mockserver.trace_id},
        **service_client_options,
    )


@pytest.fixture
def mockserver_client(mockserver, service_client_options):
    return service_client.Client(
        mockserver.base_url,
        service_headers={mockserver.trace_id_header: mockserver.trace_id},
        **service_client_options,
    )


@pytest.fixture
def dummy_service(mockserver, mockserver_client):
    @mockserver.json_handler('/test_protocol/foo')
    def _foo_handler(request):
        if request.json['id'] == 'foo':
            return {'name': 'foo bar'}
        return mockserver.make_response(status=404, json={'code': 'not-found'})

    @mockserver.json_handler('/test_protocol/bar')
    async def _bar_handler(request):
        response = await mockserver_client.get('/yamlmocks/simple')
        assert response.status_code == 200
        return response.json()


@pytest.fixture
def mark_mock(request, mockserver):
    foo_marker = request.node.get_closest_marker('foo')

    @mockserver.json_handler('/test_protocol/mark')
    def _mark_handler(request):
        return {'value': foo_marker.args[0]}


@pytest.fixture
def header_mock(mockserver):
    @mockserver.json_handler('/test_protocol/header/return')
    def _handler_return(request):
        return {'value': request.headers.get('x-testsuite-header')}

    @mockserver.json_handler('/test_protocol/header/set')
    def _handler_set(request):
        return mockserver.make_response(
            headers={'x-testsuite-header': request.json['value']},
        )
