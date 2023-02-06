async def test_tvmkeys(taxi_rate_limiter_proxy):
    response = await taxi_rate_limiter_proxy.get('tvmkeys')
    assert response.status_code == 200
    assert response.content
