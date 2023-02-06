import math


async def test_proxies_grocery_api_startup(taxi_grocery_market_gw, mockserver):
    """ Проксирует ответ от grocery-api:/startup """

    # Где-то в Москве
    lat = 55.70
    lon = 37.50

    json_to_proxy = {
        'exists': True,
        'available': False,
        'demo_lavka': {'location': [lon, lat], 'uri': 'some-uri'},
        'coming_soon': True,
        'depot_id': '12345',
        'onboarding': False,
    }

    @mockserver.json_handler('/grocery-api/lavka/v1/api/v1/startup')
    def _mock_grocery_api_startup(request):
        assert math.isclose(float(request.args['latitude']), lat)
        assert math.isclose(float(request.args['longitude']), lon)

        return mockserver.make_response(
            json=json_to_proxy,
            headers={},
            content_type='application/json',
            status=200,
        )

    response = await taxi_grocery_market_gw.post(
        f'/lavka/v1/market-gw/v1/startup?latitude={lat}&longitude={lon}',
        headers={},
    )

    assert _mock_grocery_api_startup.times_called == 1
    assert response.json() == json_to_proxy
