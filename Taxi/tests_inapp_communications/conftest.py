# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from inapp_communications_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(autouse=True)
def _promotions(mockserver):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return {
            'stories': [],
            'fullscreens': [],
            'cards': [],
            'notifications': [],
            'promos_on_map': [],
            'eda_banners': [],
            'deeplink_shortcuts': [],
            'promos_on_summary': [],
            'showcases': [],
        }


@pytest.fixture(autouse=True)
def _card_filter(mockserver):
    @mockserver.json_handler('/card-filter/v1/filteredcards')
    def _mock_card_filter(request):
        return {'available_cards': [], 'wallets': []}


@pytest.fixture(autouse=True)
def _tags(mockserver):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1']}


@pytest.fixture(autouse=True)
def _admin_images(mockserver):
    @mockserver.json_handler('/admin-images/internal/list')
    def _mock_internal_list(request):
        return {'limit': 1, 'offset': 0, 'total': 0, 'items': []}


@pytest.fixture(autouse=True)
def _archive(order_archive_mock):
    pass


@pytest.fixture(autouse=True)
def _taxi_tafiffs(mockserver):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _mock_tariffs_bulk_retrieve(request):
        return {'zones': []}


@pytest.fixture(autouse=True)
def _communications_audience(mockserver):
    def _init(campaigns):
        @mockserver.json_handler(
            '/communications-audience/communications-audience'
            '/v1/get_campaigns',
        )
        def _mock_get_campaigns(request):
            return mockserver.make_response(
                status=200, json={'campaigns': campaigns},
            )

        return _mock_get_campaigns

    return _init


@pytest.fixture(autouse=True)
def _user_api(mockserver):
    def init(device_id='test_id'):
        @mockserver.json_handler('/user-api/users/get')
        def _mock_get_authinfo(request):
            return mockserver.make_response(
                status=200,
                json={'metrica_device_id': device_id, 'id': 'llll'},
            )

        return _mock_get_authinfo

    return init


@pytest.fixture(autouse=True)
def _user_statistics(mockserver):
    @mockserver.json_handler('/user-statistics/v1/orders')
    def _mock_stats(request):
        return mockserver.make_response(status=200, json={'data': []})
