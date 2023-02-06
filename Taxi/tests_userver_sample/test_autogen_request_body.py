async def test_array(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/request-body/array')
    def _handler(request):
        return mockserver.make_response(json=request.json)

    response = await taxi_userver_sample.post(
        'autogen/request-body/array', json=['foo', 'bar'],
    )

    assert response.status_code == 200
    assert response.json() == ['foo', 'bar']
    assert _handler.times_called == 1
