async def test_partial_defs(taxi_test_service, mockserver):
    @mockserver.json_handler(
        '/test-service/response-ref-usage/service-partial-defs',
    )
    async def _handler(request):
        return mockserver.make_response(json={'value': request.query['value']})

    response = await taxi_test_service.get(
        '/response-ref-usage/service-partial-defs', params={'value': 'foobar'},
    )
    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'value': 'foobar'}
