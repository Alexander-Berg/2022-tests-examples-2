async def test_stream_ok(taxi_test_service, mockserver):
    @mockserver.json_handler('/tvm/echo')
    async def _handler(request):
        return mockserver.make_response(
            json={'some_field': 'some_value'}, status=200,
        )

    response = await taxi_test_service.get('/non-buffered-external-echo')
    assert response.status_code == 200
    assert _handler.times_called == 1
    assert response.json() == {'response': '{"some_field": "some_value"}'}


async def test_stream_fail(taxi_test_service, mockserver):
    @mockserver.json_handler('/tvm/echo')
    async def _handler(request):
        return mockserver.make_response('123456789012345', status=500)

    response = await taxi_test_service.get('/non-buffered-external-echo')
    assert response.status_code == 500
    assert _handler.times_called > 0
    assert response.json() == {'response': '123456789012345'}
