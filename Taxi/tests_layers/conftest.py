# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from layers_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(autouse=True)
def mock_mt_stops(request, mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/masstransit/v2/stops')
    def handler_masstransit_stops(request):
        return {'stops': []}


@pytest.fixture(autouse=True)
def mock_userplaces(request, mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/userplaces/userplaces/list')
    def handler_userplaces(request):
        return {'places': []}


@pytest.fixture(autouse=True)
def mock_sdc_polygons_cache(request, mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/special-zones/zones/list')
    def handler_zones_list(request):
        return load_json('zones_list_response.json')


@pytest.fixture(autouse=True)
def mock_shuttle_routes_cache(request, mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/routes/list',
    )
    def handler_zones_list(request):
        return load_json('shuttle_routes_list_response.json')


@pytest.fixture(autouse=True)
def mock_wind(request, mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/wind/pf/server/v1/operatingAreas')
    def mock_operating_areas(request):
        assert request.headers['x-api-key'] == 'windapikey'
        return load_json('wind_areas.json')
