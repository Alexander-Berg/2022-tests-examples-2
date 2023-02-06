# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from persuggest_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture
def service_client_default_headers():
    return {
        'User-Agent': 'yandex-taxi/3.18.0.7675 Android/6.0 (testenv client)',
        'Accept-Language': 'en',
    }


@pytest.fixture(autouse=True)
def _mock_core(mockserver, load_json):
    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_graph(request):
        return {'adjusted': []}


@pytest.fixture(autouse=True)
def _mock_regions(mockserver, load_json):
    @mockserver.json_handler('/eats-core/v1/export/regions')
    def _mock_core(request):
        return load_json('eats_regions_response.json')


@pytest.fixture(autouse=True)
def _mock_catalog_polygons(mockserver, load_json):
    @mockserver.json_handler('/eda-catalog/v1/catalog-polygons')
    def _mock_catalog(request):
        responses = load_json('eda_catalog_polygons_response.json')
        region_id = request.query.get('eatsRegionId')
        return responses[region_id]


@pytest.fixture
def yamaps_wrapper(load_json, yamaps):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        geo_objects = load_json('yamaps_geo_objects.json')['geo_objects']
        if 'uri' in request.args:
            for addr in geo_objects:
                if addr['uri'] == request.args['uri']:
                    return [addr]
            return []
        if 'll' in request.args:
            for addr in geo_objects:
                if addr['ll'] == request.args['ll']:
                    return [addr]
        return []


@pytest.fixture(autouse=True)
def _mock_umlaas_geo(mockserver):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}


@pytest.fixture(autouse=True)
def territories_countries_list(mockserver, load_json):
    @mockserver.json_handler('/territories/v1/countries/list')
    def mock_countries_list(request):
        request.get_data()
        return load_json('countries.json')

    return mock_countries_list
