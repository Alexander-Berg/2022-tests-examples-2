async def test_response(taxi_userver_sample, mockserver):
    @mockserver.json_handler(
        '/userver-sample/openapi/oneof-discriminator-response',
    )
    async def _mock(request):
        return {'type': 'object'}

    response = await taxi_userver_sample.get(
        '/openapi/oneof-discriminator-response',
    )
    assert response.status_code == 200
    assert response.json() == {'type': 'object'}
