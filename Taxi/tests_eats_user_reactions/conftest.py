# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_user_reactions_plugins import *  # noqa: F403 F401

CATALOG_STORAGE_SEARCH_URL = (
    '/eats-catalog-storage/internal/'
    'eats-catalog-storage/v1/search/places-zones-ids'
)
CATALOG_STORAGE_PLACES_URL = (
    '/eats-catalog-storage/internal/'
    'eats-catalog-storage/v1/places/retrieve-by-ids'
)
CATALOG_STORAGE_SEARCH_RESPONSE_JSON = {
    'ids': [{'place_id': 123, 'zone_ids': []}],
}
CATALOG_STORAGE_PLACES_RESPONSE_JSON = {
    'places': [
        {
            'id': 123,
            'revision_id': 10,
            'updated_at': '2020-03-02T20:47:44.338Z',
            'brand': {
                'id': 222,
                'name': 'brand_name',
                'slug': 'brand_slug',
                'picture_scale_type': 'aspect_fit',
            },
        },
    ],
    'not_found_place_ids': [],
}


@pytest.fixture
def mock_catalog_storage_search(mockserver):
    @mockserver.json_handler(CATALOG_STORAGE_SEARCH_URL)
    def _mock_catalog_storage_search(request):
        return mockserver.make_response(
            json=CATALOG_STORAGE_SEARCH_RESPONSE_JSON, status=200,
        )


@pytest.fixture
def mock_catalog_storage_search_500(mockserver):
    @mockserver.json_handler(CATALOG_STORAGE_SEARCH_URL)
    def _mock_catalog_storage_search_500(request):
        return mockserver.make_response(
            json={'code': '500', 'message': 'Internal Server Error'},
            status=500,
        )


@pytest.fixture
def mock_catalog_search_empty(mockserver):
    @mockserver.json_handler(CATALOG_STORAGE_SEARCH_URL)
    def _mock_catalog_search_empty(request):
        return mockserver.make_response(json={'ids': []}, status=200)


@pytest.fixture
def mock_catalog_storage_places(mockserver):
    @mockserver.json_handler(CATALOG_STORAGE_PLACES_URL)
    def _mock_catalog_storage_places(request):
        return mockserver.make_response(
            json=CATALOG_STORAGE_PLACES_RESPONSE_JSON, status=200,
        )


@pytest.fixture
def mock_catalog_storage_places_500(mockserver):
    @mockserver.json_handler(CATALOG_STORAGE_PLACES_URL)
    def _mock_catalog_storage_places_500(request):
        return mockserver.make_response(
            json={'code': '500', 'message': 'Internal Server Error'},
            status=500,
        )


@pytest.fixture
def mock_catalog_places_empty(mockserver):
    @mockserver.json_handler(CATALOG_STORAGE_PLACES_URL)
    def _mock_catalog_places_empty(request):
        return mockserver.make_response(
            json={'places': [], 'not_found_place_ids': []}, status=200,
        )
