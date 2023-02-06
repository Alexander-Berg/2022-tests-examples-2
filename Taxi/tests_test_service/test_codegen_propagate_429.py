async def test_propagate_429(taxi_test_service, mockserver):
    @mockserver.json_handler('/test-service/codegen/async-client')
    async def _handler(request):
        return mockserver.make_response(
            status=429,
            headers={
                'X-YaTaxi-Ratelimit-Reason': 'xyz',
                'X-yataxi-Ratelimited-By': 'mememe',  # Not Xxxx case
                'X-Garbage': 'foo',
            },
        )

    response = await taxi_test_service.get('/codegen/async-client')
    assert response.status_code == 429
    assert response.headers['X-YaTaxi-Ratelimit-Reason'] == 'xyz'
    assert response.headers['X-YaTaxi-Ratelimited-By'] == 'mememe'
    assert 'X-Garbage' not in response.headers
