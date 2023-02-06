#  ->  test-service       ->  _handler       ->  test-service    ->  test
async def test_contents_no_content_type(taxi_test_service, mockserver):
    @mockserver.json_handler('/test-service/echo-no-body')
    async def _handler(request):
        return mockserver.make_response()

    response = await taxi_test_service.get('/echo-no-body')
    assert _handler.times_called == 1
    assert response.status_code == 200
