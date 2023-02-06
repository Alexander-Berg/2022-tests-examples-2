import pytest
# pylint: disable=import-error
from yamaps_tools import driving as yamaps_driving  # noqa: F401 C5521

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from umlaas_grocery_eta_plugins import *  # noqa: F403 F401

from tests_umlaas_grocery_eta import consts


@pytest.fixture(autouse=True)
def grocery_depot_stats(mockserver, load_json):
    @mockserver.json_handler(
        '/grocery-dispatch-tracking/internal'
        '/grocery-dispatch-tracking/v1/depot-statistics',
    )
    def _grocery_depot_stats(request):
        requested_ids = request.json['legacy_depot_ids']
        response = load_json('grocery_dispatch_tracking_response.json')
        return {
            'depot_statistics': [
                stats
                for stats in response['depot_statistics']
                if stats['legacy_depot_id'] in requested_ids
            ],
        }


@pytest.fixture(autouse=True)
def grocery_surge(mockserver, load_json):
    @mockserver.json_handler('/grocery-surge/internal/v1/surge/depot_state')
    def _depot_state_handler(request):
        return load_json('grocery_surge_depot_state_response.json')


@pytest.fixture(autouse=True)
def _mock_grocery_checkins(mockserver, load_json):
    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v1/shifts/shifts-info',
    )
    def _mock(request):
        return load_json('grocery_checkins_shifts_info_response.json')


@pytest.fixture(name='maps_router')
def mock_maps_router(mockserver):
    @mockserver.handler('/maps-router/v2/summary')
    def _mock_maps_router(request):
        data = {'time': 27 * 60, 'distance': 15200}
        return mockserver.make_response(
            response=yamaps_driving.proto_driving_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    return _mock_maps_router


@pytest.fixture(name='grocery_routing')
def mock_grocery_routing(mockserver):
    @mockserver.json_handler(
        '/grocery-routing/internal/grocery-routing/v1/route',
    )
    def _get_route(request):
        assert request.json == {
            'source': {
                'lon': consts.DEPOT_LOCATION[0],
                'lat': consts.DEPOT_LOCATION[1],
            },
            'destination': {
                'lon': consts.USER_LOCATION[0],
                'lat': consts.USER_LOCATION[1],
            },
            'transport_type': 'pedestrian',
        }
        return {'distance': 13200, 'eta': 55 * consts.MINUTE}

    return _get_route
