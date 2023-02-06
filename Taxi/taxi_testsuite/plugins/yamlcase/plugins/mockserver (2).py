import pytest

from .. import assertions


@pytest.fixture
def yamlcase_create_mockserver(
        request, mockserver, yamlcase_load_body, yamlcase_context,
):
    def create_mockserver_handler(mock):
        @mockserver.handler(mock['url'])
        def _handler(request):
            with yamlcase_context.context({'request': request}):
                mock_request = mock.get('request', {})
                if 'method' in mock_request:
                    assert request.method == mock_request['method']
                if 'headers' in mock_request:
                    assertions.assert_headers(
                        request.headers, mock_request['headers'],
                    )
                if 'query_params' in mock_request:
                    assertions.assert_query_params(
                        request.query_string, mock_request['query_params'],
                    )
                if 'body' in mock_request:
                    expected_body = yamlcase_load_body(
                        mock_request['body'], allow_matching=True,
                    )
                    assert request.json == expected_body
                response = mock.get('response', {})
                return mockserver.make_response(
                    status=response.get('status', 200),
                    json=yamlcase_load_body(response['body']),
                    headers=response.get('headers'),
                )

    for mock in request.node.mockserver_mocks:
        create_mockserver_handler(mock)


@pytest.fixture
def yamlcase_assertion_mockserver_called(mockserver):
    async def run_assertion(assertion):
        assert 'url' in assertion
        handler = mockserver.get_callqueue_for(assertion['url'])
        if 'times' in assertion:
            assert handler.times_called == assertion['times']
        else:
            assert handler.times_called > 0

    return run_assertion
