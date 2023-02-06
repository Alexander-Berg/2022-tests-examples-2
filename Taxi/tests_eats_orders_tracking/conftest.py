# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_orders_tracking_plugins import *  # noqa: F403 F401


URL_STORAGE_SEARCH_PLACES = (
    '/eats-catalog-storage/internal/eats-catalog-storage/v1/search/places/list'
)


def get_default_points_eta_response():
    return {
        'id': 'temp_id',
        'route_points': [
            {
                'id': 1,
                'address': {
                    'fullname': '1',
                    'coordinates': [37.8, 55.4],
                    'country': '1',
                    'city': '1',
                    'street': '1',
                    'building': '1',
                },
                'type': 'source',
                'visit_order': 1,
                'visit_status': 'arrived',
                'visited_at': {},
            },
            {
                'id': 2,
                'address': {
                    'fullname': '2',
                    'coordinates': [37.8, 55.4],
                    'country': '2',
                    'city': '2',
                    'street': '2',
                    'building': '2',
                },
                'type': 'destination',
                'visit_order': 2,
                'visit_status': 'pending',
                'visited_at': {'expected': '2020-10-28T18:28:00.00+00:00'},
            },
            {
                'id': 3,
                'address': {
                    'fullname': '3',
                    'coordinates': [40.8, 50.4],
                    'country': '3',
                    'city': '3',
                    'street': '3',
                    'building': '3',
                },
                'type': 'destination',
                'visit_order': 3,
                'visit_status': 'pending',
                'visited_at': {'expected': '2020-10-28T19:00:00.00+00:00'},
            },
        ],
    }


@pytest.fixture(name='make_tracking_headers')
def _make_tracking_headers():
    def _wrapper(eater_id):
        headers = {}
        headers['X-YaTaxi-User'] = 'eats_user_id=' + eater_id
        headers['X-Eats-User'] = 'user_id=' + eater_id
        return headers

    return _wrapper


@pytest.fixture(name='mock_storage_search_places')
def _mock_storage_search_places(mockserver, load_json):
    @mockserver.json_handler(URL_STORAGE_SEARCH_PLACES)
    def _handler_storage_search_places(request):
        assert len(request.json['place_ids']) == 1
        assert 'place_slugs' not in request.json
        place_id = request.json['place_ids'][0]

        mock_response = load_json('storage_response.json')
        mock_response['places'][0]['place_id'] = place_id
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_storage_search_places_empty')
def _mock_storage_search_places_empty(mockserver, load_json):
    @mockserver.json_handler(URL_STORAGE_SEARCH_PLACES)
    def _handler_storage_search_places_empty(request):
        assert len(request.json['place_ids']) == 1
        assert 'place_slugs' not in request.json
        place_id = request.json['place_ids'][0]

        mock_response = load_json('storage_empty_response.json')
        mock_response['not_found_place_ids'][0] = place_id
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_eats_personal_store')
def _mock_eats_personal_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _handler_eats_personal_store(request):
        phone_id = 'id_' + request.json['value']
        value = request.json['value']
        mock_response = {'id': phone_id, 'value': value}
        return mockserver.make_response(json=mock_response, status=200)

    return _handler_eats_personal_store


@pytest.fixture(name='mock_eats_personal')
def _mock_eats_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _handler_eats_personal(request):
        mock_response = {}
        mock_response['items'] = []
        phone = 123
        request_items = request.json['items']
        for request_item in request_items:
            item = {'id': request_item['id'], 'value': str(phone)}
            phone += 1
            mock_response['items'].append(item)
        return mockserver.make_response(json=mock_response, status=200)
