#  ->  test-service       ->  _handler       ->  test-service    ->  test
async def test_bodyless_response_with_headers(taxi_test_service, mockserver):
    @mockserver.json_handler(
        '/test-service/response-with-headers-without-body',
    )
    async def _handler(request):
        return mockserver.make_response(headers={'something': 'nothing'})

    response = await taxi_test_service.get(
        '/response-with-headers-without-body',
    )
    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.headers['something'] == 'nothing'
