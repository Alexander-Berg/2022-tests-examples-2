async def test_429(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    async def _mock_autogen_empty(request):
        return mockserver.make_response(status=429)

    response = await taxi_userver_sample.get('external-echo-empty')
    assert response.status_code == 429
    assert response.json() == {'code': '429', 'message': 'Too Many Requests'}


async def test_400_no(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/empty')
    async def _mock_autogen_empty(request):
        return mockserver.make_response(status=400)

    response = await taxi_userver_sample.get('external-echo-empty')
    assert response.status_code == 500
