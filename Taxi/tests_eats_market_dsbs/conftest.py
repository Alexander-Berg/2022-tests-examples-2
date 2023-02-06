# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_market_dsbs_plugins import *  # noqa: F403 F401


TASK_NAME = 'periodic-mapping'
EATS_URL = (
    '/eats-catalog-storage'
    + '/internal/eats-catalog-storage/v1/delivery_zones/retrieve-by-place-ids'
)


@pytest.fixture(name='mock_eats_catalog_storage_full')
def _mock_eats_catalog_storage(mockserver, load_json):
    @mockserver.json_handler(EATS_URL)
    def _handler(request):
        assert len(request.json['place_ids']) == 1
        # need to check containing name, polygon and enabled
        assert 'polygon' in request.json['projection']
        assert 'name' in request.json['projection']
        assert 'enabled' in request.json['projection']
        mock_response = load_json('full_response.json')
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_eats_catalog_storage_not_full')
def _mock_eats_catalog_storage_not_full(mockserver, load_json):
    @mockserver.json_handler(EATS_URL)
    def _handler(request):
        mock_response = load_json('not_full_response.json')  # enabled deleted
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_eats_catalog_storage_not_exist')
def _mock_eats_catalog_storage_not_exist(mockserver, load_json):
    @mockserver.json_handler(EATS_URL)
    def _handler(request):
        mock_response = load_json('not_exist_place_id_response.json')
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_market_nesu')
def _mock_market_nesu(mockserver, load_json):
    @mockserver.json_handler('/market-nesu/internal/partner/1/polygonal-zones')
    def _handler(request):
        current_request = request.json
        assert len(current_request) == 1
        current_object = current_request['zones'][0]['geo']
        expected_object = load_json('expected_request_to_market.json')[
            'zones'
        ][0]['geo']
        assert current_object['type'] == expected_object['type']
        assert current_object['enabled'] == expected_object['enabled']
        assert current_object['id'] == expected_object['id']
        assert current_object['name'] == expected_object['name']
        assert current_object['coordinates'] == expected_object['coordinates']
        return mockserver.make_response(status=200)
