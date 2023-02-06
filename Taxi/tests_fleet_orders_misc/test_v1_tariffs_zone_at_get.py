from tests_fleet_orders_misc import common

ENDPOINT = '/fleet/fleet-orders-misc/v1/tariffs/zone-at'


async def test_success(taxi_fleet_orders_misc, mockserver):
    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _mock_nearestzone(request):
        assert request.json == {'point': [0, 0]}
        return {'nearest_zone': 'berlin'}

    response = await taxi_fleet_orders_misc.get(
        ENDPOINT, headers=common.YA_USER_HEADERS, params={'lat': 0, 'lon': 0},
    )

    assert response.status_code == 200
    assert response.json() == {'zone_id': 'berlin'}


async def test_failure(taxi_fleet_orders_misc, mockserver):
    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _mock_nearestzone(request):
        assert request.json == {'point': [0, 0]}
        return mockserver.make_response(
            json={'error': {'message': 'Not found'}}, status=404,
        )

    response = await taxi_fleet_orders_misc.get(
        ENDPOINT, headers=common.YA_USER_HEADERS, params={'lat': 0, 'lon': 0},
    )

    assert response.status_code == 404
