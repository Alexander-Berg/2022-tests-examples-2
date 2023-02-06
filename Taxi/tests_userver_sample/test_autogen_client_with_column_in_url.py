async def test_request_client_with_column_in_url(
        taxi_userver_sample, mockserver,
):
    @mockserver.json_handler('/test-client/url-with-column/test:simple')
    def _handler(request):
        return mockserver.make_response()

    response = await taxi_userver_sample.get(
        '/autogen/client-with-column-in-url',
    )
    assert response.status_code == 200
    assert _handler.times_called == 1


async def test_request_client_with_column_in_url_with_param(
        taxi_userver_sample, mockserver,
):
    @mockserver.json_handler(
        '/test-client/url-with-column-with-params/test:simple',
    )
    def _handler(request):
        return mockserver.make_response(
            json={
                'bodytest': request.json.get('bodytest'),
                'querytest': request.query.get('querytest'),
            },
        )

    response = await taxi_userver_sample.post(
        '/autogen/client-with-column-in-url-with-param',
        json={'bodytest': 'test_body'},
        params={'querytest': 'test_query'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'bodytest': 'test_body',
        'querytest': 'test_query',
    }
    assert _handler.times_called == 1
