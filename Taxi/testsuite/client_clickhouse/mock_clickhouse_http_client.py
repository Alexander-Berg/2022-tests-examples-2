import pytest


@pytest.fixture(name='clickhouse_http_client_mock')
def mock_clickhouse_http_client(mockserver):
    class Context:
        def __init__(self):
            self._response = {'__default__': '{}'}

        def set_response(self, request, response):
            self._response[request] = response

        def response(self, request):
            if request in self._response:
                return self._response[request]
            return self._response['__default__']

    context = Context()
    # periodic tasks of distlocks service use it as external service
    # pylint: disable=unused-variable
    @mockserver.handler('/clickhouse-http-client')
    def execute_query(request):
        return mockserver.make_response(
            context.response(request.get_data()), 200,
        )

    return context
