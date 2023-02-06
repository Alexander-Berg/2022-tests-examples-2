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
                if 'form' in mock_request:
                    expected_form = yamlcase_load_body(
                        mock_request['form'], allow_matching=True,
                    )
                    assert request.form == expected_form

                response = mock.get('response', {})
                if 'body' in response and 'form' in response:
                    raise RuntimeError(
                        '"body" and "form" parameters can not be used '
                        'at the same time in mockserver response',
                    )
                if 'body' not in response and 'form' not in response:
                    raise RuntimeError(
                        'One of "body" and "form" parameters must be set '
                        'in mockserver response',
                    )

                response_kwargs = {}
                if 'body' in response:
                    response_kwargs['json'] = yamlcase_load_body(
                        response['body'],
                    )
                if 'form' in response:
                    response_kwargs['form'] = yamlcase_load_body(
                        response['form'],
                    )

                return mockserver.make_response(
                    status=response.get('status', 200),
                    headers=response.get('headers'),
                    **response_kwargs,
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
