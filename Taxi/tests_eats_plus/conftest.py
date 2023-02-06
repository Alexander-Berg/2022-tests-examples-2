# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_catalog_storage_cache import (  # noqa: F403 F401
    eats_catalog_storage_cache,  # noqa: F403 F401
)
from eats_plus_plugins import *  # noqa: F403 F401

EATS_DISCOUNTS_MATCH = [
    {
        'subquery_id': 'offer_0',
        'place_cashback': {
            'menu_value': {'value_type': 'fraction', 'value': '10.0'},
        },
        'yandex_cashback': {
            'menu_value': {'value_type': 'fraction', 'value': '5.0'},
        },
    },
]


EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT = [
    {
        'id': 1,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [37.525496503606774, 55.75568074159372]},
        'country': {
            'id': 1,
            'code': 'abc',
            'name': 'USSR',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'store',
        'type': 'native',
    },
    {
        'id': 2,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [37.525496503606774, 55.75568074159372]},
        'country': {
            'id': 1,
            'code': 'abc',
            'name': 'USSR',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'store',
        'type': 'native',
    },
    {
        'id': 3,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [37.525496503606774, 55.75568074159372]},
        'country': {
            'id': 1,
            'code': 'abc',
            'name': 'USSR',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'store',
        'type': 'native',
    },
    {
        'id': 4,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [37.525496503606774, 55.75568074159372]},
        'country': {
            'id': 1,
            'code': 'abc',
            'name': 'USSR',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'store',
        'type': 'native',
    },
    {
        'id': 5,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [37.525496503606774, 55.75568074159372]},
        'country': {
            'id': 1,
            'code': 'abc',
            'name': 'USSR',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'store',
        'type': 'native',
    },
    {
        'id': 6,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [37.525496503606774, 55.75568074159372]},
        'country': {
            'id': 1,
            'code': 'abc',
            'name': 'USSR',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'store',
        'type': 'native',
    },
    {
        'id': 8,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [37.525496503606774, 55.75568074159372]},
        'country': {
            'id': 1,
            'code': 'abc',
            'name': 'USSR',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'store',
        'type': 'native',
    },
    {
        'id': 45,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [37.567595, 55.743064]},
        'country': {
            'id': 1,
            'code': 'abc',
            'name': 'USSR',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'store',
        'type': 'native',
    },
    {
        'id': 78,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [37.525496503606774, 55.75568074159372]},
        'country': {
            'id': 1,
            'code': 'abc',
            'name': 'USSR',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'store',
        'type': 'native',
    },
]


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture fo service cache',
    )
    config.addinivalue_line(
        'markers',
        'eats_plus_regions_cache: [eats_plus_regions_cache] '
        'fixture fo regions cache',
    )
    config.addinivalue_line(
        'markers',
        'eats_discounts_match: [eats_discounts_match] '
        'fixture for eats-discounts mock',
    )


@pytest.fixture(name='passport_blackbox')
def passport_blackbox(mockserver):
    def fixture(has_plus=None, has_cashback=None):
        @mockserver.json_handler('/blackbox')
        def _mock_blackbox(json_request):
            uid = json_request.args['uid']
            return {
                'users': [
                    {
                        'uid': {'value': uid},
                        'attributes': {
                            '1015': '1' if has_plus else '0',
                            '1025': '1' if has_cashback else '0',
                        },
                    },
                ],
            }

    return fixture


@pytest.fixture(name='eats_eaters', autouse=True)
def eats_eaters(mockserver):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eats_eaters(json_request):
        uid = json_request.json['passport_uid']
        return {
            'eater': {
                'id': f'eater-{uid}',
                'uuid': 'eater-uuid',
                'passport_uid': uid,
                'passport_uid_type': 'portal',
                'personal_phone_id': 'personal_phone_id',
                'personal_email_id': 'personal_email_id',
                'created_at': '2021-05-28T10:12:00+0000',
                'updated_at': '2021-05-29T11:33:00+0000',
                'client_type': 'common',
                'type': 'native',
                'name': 'Антуан Вендеттов ',
            },
        }

    return _mock_eats_eaters


@pytest.fixture(name='eats_core_orders_stats')
def eats_core_orders_stats(mockserver):
    def fixture(has_orders=False, additional_orders=None):
        @mockserver.json_handler(
            '/eats-orders-stats/server/api/v1/order/stats',
        )
        def _mock_eats_core(json_request):
            eater_id = json_request.json['eater_ids'][0]
            stats = []
            if has_orders:
                stats = [
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business': 'restaurant',
                        'orders_count': 1,
                    },
                ]
            if additional_orders:
                stats.extend(additional_orders)
            return {'eaters_stats': [{'eater_id': eater_id, 'stats': stats}]}

    return fixture


@pytest.fixture(name='eats_order_stats')
def eats_order_stats(mockserver, request):
    def fixture(has_orders=True, overrided_counters=None):
        @mockserver.json_handler(
            '/eats-order-stats/internal/eats-order-stats/v1/orders',
        )
        def _mock_eats_order_stats(json_request):
            counters = []
            identity = json_request.json['identities'][0]
            if has_orders:
                counters = [
                    {
                        'first_order_at': '2021-05-28T10:12:00+0000',
                        'last_order_at': '2021-05-29T11:33:00+0000',
                        'properties': [
                            {'name': 'brand_id', 'value': '1'},
                            {'name': 'place_id', 'value': '1'},
                            {'name': 'business_type', 'value': 'restaurant'},
                        ],
                        'value': 5,
                    },
                ]
            if overrided_counters:
                counters = overrided_counters

            return {'data': [{'counters': counters, 'identity': identity}]}

    return fixture


@pytest.fixture(name='plus_wallet')
def plus_wallet(mockserver):
    def fixture(balances):
        @mockserver.json_handler('plus-wallet/v1/balances')
        def _plus_balance(request):
            response = {'balances': []}
            for balance in balances.items():
                response['balances'].append(
                    {
                        'wallet_id': f'wallet_{balance[0]}',
                        'balance': f'{balance[1]}',
                        'currency': f'{balance[0]}',
                    },
                )
            return response

    return fixture


@pytest.fixture(name='eats_plus_regions_cache', autouse=True)
def service_cache(mockserver, request):
    marker = request.node.get_closest_marker('eats_plus_regions_cache')
    data = marker.args[0] if marker else []

    class ServiceCache:
        def __init__(self, data):
            self.data = data if data else []

        def updates(self):
            return self.data

    eats_plus_regions_cache = ServiceCache(data)

    @mockserver.json_handler('/eats-core/v1/export/regions')
    def _regions(_):
        data = eats_plus_regions_cache.updates()
        return {'payload': data}


@pytest.fixture(name='eats_discounts_match', autouse=True)
def eats_discounts_match(mockserver, request):
    marker = request.node.get_closest_marker('eats_discounts_match')
    data = marker.args[0] if marker else []

    class EatsDiscountsMatch:
        def __init__(self, data):
            self.data = data if data else []

        def updates(self):
            return self.data

    eats_discounts_match_data = EatsDiscountsMatch(data)

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_eats_discounts_match(json_request):
        data = eats_discounts_match_data.updates()
        hierarchy_names = {
            'place_cashback',
            'place_menu_cashback',
            'yandex_cashback',
            'yandex_menu_cashback',
        }

        match_results = dict()
        discount_id = 1
        for item in data:
            for hierarchy_name in hierarchy_names:
                cashback_value = item.get(hierarchy_name)
                if cashback_value is None:
                    continue
                result = match_results.get(hierarchy_name)
                if result is None:
                    result = dict()
                    result['hierarchy_name'] = hierarchy_name
                    result['discounts'] = []
                    result['subquery_results'] = []
                    result['discount_id'] = str(discount_id)
                    match_results[hierarchy_name] = result

                subquery_id = item['subquery_id']
                discount_name = 'plus_happy_hours'
                # this allows to test Plus promos
                # TODO rework entire fixture, now it looks poor
                if 'plus' in item['subquery_id']:
                    pieces = item['subquery_id'].split('_')
                    discount_name = '_'.join(pieces[1:])
                    subquery_id = pieces[0]

                result['discounts'].append(
                    {
                        'cashback_value': cashback_value,
                        'discount_meta': {'name': discount_name},
                        'discount_id': str(discount_id),
                    },
                )
                result['subquery_results'].append(
                    {'id': subquery_id, 'discount_id': str(discount_id)},
                )
                discount_id += 1
        return {'match_results': list(match_results.values())}

    return _mock_eats_discounts_match


@pytest.fixture(name='restapp_promo_cashback_settings', autouse=True)
def restapp_promo_cashback_settings(mockserver, request):
    @mockserver.json_handler(
        '/eats-restapp-promo/internal/'
        'eats-restapp-promo/v1/plus/'
        'cashback/settings',
    )
    def _mock_restapp_promo_cashback_settings(request):
        assert request.json.get('places_settings')
        for place_settings in request.json.get('places_settings'):
            if place_settings.get('place_has_plus'):
                assert place_settings.get(
                    'yandex_cashback',
                ) or place_settings.get('place_cashback')
        return mockserver.make_response(status=204)
