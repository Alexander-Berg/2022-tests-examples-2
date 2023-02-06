ROUTE = '/v1/suggests/landings/paid-acquisition/cities'


async def test_tickets_create_simple_requests(taxi_hiring_api_web):
    response = await taxi_hiring_api_web.get(ROUTE)
    assert response.status == 200
    body = await response.json()
    assert body
    assert isinstance(body, list)
