import pytest

from tests_fleet_orders_manager import common

ENDPOINT = 'fleet/fleet-orders-manager/v1/route'

GEOPOINTS = [
    [37.455434, 55.719436],
    [37.451695, 55.723917],
    [37.473896, 55.728358],
    [37.518952, 55.736290],
]

REQUEST_BODY = {'router': 'google', 'geopoints': GEOPOINTS}


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


@pytest.mark.parametrize(
    'router', [pytest.param('yandex'), pytest.param('google')],
)
async def test_routing(
        taxi_fleet_orders_manager, mockserver, load_binary, router,
):
    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        rll = _rll_to_array(request.args['rll'])
        assert rll == GEOPOINTS
        return mockserver.make_response(
            response=load_binary(
                'maps_response-37.455596,55.719463'
                '~37.451695,55.723917~'
                '37.473896,55.728358~'
                '37.518952,55.73629.pb',
            ),
            status=200,
            content_type='application/x-protobuf',
        )

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    request = {'router': router, 'geopoints': GEOPOINTS}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=request, headers=headers,
    )

    assert response.status_code == 200
    assert response.json()['track_points'] != []
    assert response.json()['duration'] > 0
    assert response.json()['distance'] > 0


@pytest.mark.parametrize(
    'router', [pytest.param('yandex'), pytest.param('google')],
)
async def test_routing_disabled(
        taxi_fleet_orders_manager, mockserver, load_binary, router,
):
    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        rll = _rll_to_array(request.args['rll'])
        assert rll == GEOPOINTS
        return mockserver.make_response(status=400)

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    request = {'router': router, 'geopoints': GEOPOINTS}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=request, headers=headers,
    )

    assert response.status_code == 500
