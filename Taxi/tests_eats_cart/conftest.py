import copy
import datetime

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_cart_plugins import *  # noqa: F403 F401

from . import utils


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture fo service cache',
    )
    config.addinivalue_line(
        'markers',
        'smart_prices_cache: [smart_prices_cache] ' 'fixture fo service cache',
    )
    config.addinivalue_line(
        'markers',
        'smart_prices_items: [smart_prices_items] ' 'fixture fo service cache',
    )


@pytest.fixture(name='eats_order_stats', autouse=True)
def eats_order_stats(mockserver):
    def fixture(
            has_orders=True,
            overrided_counters=None,
            place_id='1',
            brand_id='1',
    ):
        @mockserver.json_handler(
            '/eats-order-stats/internal/eats-order-stats/v1/orders',
        )
        def _mock_eats_order_stats(json_request):
            counters = []
            identity = json_request.json['identities'][0]
            groups = set(json_request.json['group_by'])

            if has_orders:
                counters = [
                    {
                        'first_order_at': '2021-05-28T10:12:00+0000',
                        'last_order_at': '2021-05-29T11:33:00+0000',
                        'properties': [
                            {'name': 'brand_id', 'value': brand_id},
                            {'name': 'place_id', 'value': place_id},
                            {'name': 'business_type', 'value': 'shop'},
                        ],
                        'value': 5,
                    },
                ]
                if 'delivery_type' in groups:
                    counters[0]['properties'].append(
                        {'name': 'delivery_type', 'value': 'native'},
                    )
            if overrided_counters:
                counters = overrided_counters

            return {'data': [{'counters': counters, 'identity': identity}]}

    return fixture


@pytest.fixture(name='mock_eats_core_couriers_stats', autouse=True)
def coriers_stats(mockserver, load_json):
    response = load_json('couriers_stats_expected_response.json')

    @mockserver.json_handler('/eats-core/v1/export/settings/couriers-stats')
    def eats_core(request):
        return response

    return eats_core


@pytest.fixture(name='mock_eats_core_regions_settings', autouse=True)
def regions_settings(mockserver, load_json):
    response = load_json('regions_settings.json')

    @mockserver.json_handler('/eats-core/v1/export/settings/regions-settings')
    def eats_core(request):
        return response

    return eats_core


@pytest.fixture(name='eats_cart_cursor')
def get_eats_cart_cursor(pgsql):
    return pgsql['eats_cart'].dict_cursor()


@pytest.fixture()
def db_insert(eats_cart_cursor):
    class Context:
        @staticmethod
        def cart(
                eater_id,
                place_id='1',
                place_slug='place1',
                place_business='restaurant',
                promo_subtotal=0,
                total=0,
                delivery_fee=0,
                service_fee=0,
                shipping_type='delivery',
                created_at='2021-04-03T01:12:21+03:00',
                updated_at='2021-04-03T01:12:31+03:00',
                deleted_at=None,
                revision=1,
        ):
            eats_cart_cursor.execute(
                'INSERT INTO eats_cart.carts '
                '(revision, eater_id, place_id, place_slug, place_business, '
                'promo_subtotal, total, delivery_fee, service_fee, '
                'shipping_type, created_at, updated_at, deleted_at) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
                'RETURNING id',
                (
                    revision,
                    eater_id,
                    place_id,
                    place_slug,
                    place_business,
                    promo_subtotal,
                    total,
                    delivery_fee,
                    service_fee,
                    shipping_type,
                    created_at,
                    updated_at,
                    deleted_at,
                ),
            )
            cart_id = eats_cart_cursor.fetchone()[0]
            Context.extra_fees(cart_id, 'delivery_fee', delivery_fee)
            Context.extra_fees(cart_id, 'service_fee', service_fee)
            Context.extra_fees(cart_id, 'assembly_fee', 0)
            return cart_id

        @staticmethod
        def eater_cart(eater_id, cart_id, offer_id='offer1'):
            eats_cart_cursor.execute(
                'INSERT INTO eats_cart.eater_cart '
                '(eater_id, cart_id, offer_id) '
                'VALUES (%s, %s, %s) '
                'RETURNING id::text',
                (eater_id, cart_id, offer_id),
            )
            return eats_cart_cursor.fetchone()[0]

        @staticmethod
        def cart_item(
                cart_id,
                place_menu_item_id,
                price=0,
                promo_price=None,
                quantity=1,
                created_at='2021-04-03T01:12:21+03:00',
                is_auto=False,
        ):
            eats_cart_cursor.execute(
                'INSERT INTO eats_cart.cart_items '
                '(cart_id, place_menu_item_id, price, '
                'promo_price, quantity, created_at, is_auto) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s) '
                'RETURNING id',
                (
                    cart_id,
                    place_menu_item_id,
                    price,
                    promo_price,
                    quantity,
                    created_at,
                    is_auto,
                ),
            )
            return eats_cart_cursor.fetchone()[0]

        @staticmethod
        def item_option(
                cart_item_id: int,
                option_id: str,
                price=0,
                promo_price=None,
                quantity=1,
                created_at='2021-04-03T01:12:21+03:00',
        ):
            eats_cart_cursor.execute(
                'INSERT INTO eats_cart.cart_item_options '
                '(cart_item_id, option_id, price, '
                'promo_price, quantity, created_at) '
                'VALUES (%s, %s, %s, %s, %s, %s) '
                'RETURNING id',
                (
                    cart_item_id,
                    option_id,
                    price,
                    promo_price,
                    quantity,
                    created_at,
                ),
            )
            return eats_cart_cursor.fetchone()[0]

        @staticmethod
        def extra_fees(cart_id, fee_type, amount):
            eats_cart_cursor.execute(
                'INSERT INTO eats_cart.extra_fees '
                '(cart_id, type, amount) '
                'VALUES (%s, %s, %s) '
                'ON CONFLICT (cart_id, type) DO UPDATE SET '
                'amount = %s '
                'RETURNING id',
                (cart_id, fee_type, amount, amount),
            )
            return eats_cart_cursor.fetchone()[0]

        @staticmethod
        def item_discount(
                cart_item_id: int,
                promo_id: str,
                promo_type_id: str,
                name='name',
                picture_uri='picture_uri',
        ):
            eats_cart_cursor.execute(
                'INSERT INTO eats_cart.cart_item_discounts '
                '(cart_item_id, promo_id, promo_type_id, name, picture_uri) '
                'VALUES (%s, %s, %s, %s, %s) '
                'RETURNING id',
                (cart_item_id, promo_id, promo_type_id, name, picture_uri),
            )
            return eats_cart_cursor.fetchone()[0]

    return Context()


def make_discount_resp(json):
    total = 0
    items = []
    for item in json['items']:
        resp_item = item.copy()
        options_price = 0
        for option in resp_item['options']:
            option['promo_price'] = None
            options_price += float(option['price']) * option['quantity']
        total += (float(item['price']) + options_price) * item['quantity']
        resp_item['promo_type'] = None
        resp_item['promo_price'] = None
        items.append(resp_item)
    response = {'total': str(round(total, 2)), 'promos': [], 'items': items}
    return response


@pytest.fixture(name='local_services')
def _local_services(mockserver, load_json):
    class Context:
        available_discounts = False
        core_items_request = ['232323']
        core_items_response = load_json('eats_core_menu_items.json')
        core_items_status = 200
        eats_products_items_request = None
        eats_products_items_response = {
            'error': 'place_menu_items_not_found',
            'message': '232323',
        }
        eats_restaurant_menu_items_request = ['232323']
        eats_restaurant_menu_items_response = {
            'error': 'place_menu_items_not_found',
            'message': '232323',
        }
        core_discounts_response = None
        eats_discounts_response = None
        eats_catalog_storage_response = None
        eats_customer_slots_response = None
        request_params = utils.get_params()
        place_slugs = set(('place1',))
        delivery_zone = 10800
        catalog_place_response = load_json('eats_catalog_internal_place.json')
        catalog_place_status = 200
        mock_eda_delivery_price = None
        delivery_price_response = {}
        delivery_price_status = 500
        delivery_price_assertion = utils.do_nothing
        mock_eats_core_menu = None
        mock_eats_products_menu = None
        mocke_eats_restaurant_menu_items = None
        mock_eats_catalog = None
        mock_eats_core_discount = None
        plus_checkout_response = dict(status=204, json={})
        plus_checkout_request = {}
        mock_plus_checkout_cashback = None
        plus_response = dict(status=204, json={})
        plus_request = None
        mock_plus_cashback = None
        mock_match_discounts = None
        mock_eats_catalog_storage = None
        mock_eats_core_set_location = None
        mock_slots_validate_time = None
        mock_eats_tags = None
        cart_eta = None

        catalog_place_id = None

        def set_place_slug(self, place_slug):
            self.place_slugs = set((place_slug,))
            self.core_items_response['place_slug'] = place_slug

        def set_available_discounts(self, available):
            self.available_discounts = available

        def set_params(self, params):
            self.request_params = params

        def set_plus_checkout_response(self, *, status, json, **kwargs):
            self.plus_checkout_response = dict(
                status=status, json=json, **kwargs,
            )

        def set_plus_response(self, *, status, json, **kwargs):
            self.plus_response = dict(status=status, json=json, **kwargs)

        def set_core_promo_types(self, menu_item_id, promo_types):
            for entry in self.core_items_response['place_menu_items']:
                if entry['id'] == menu_item_id:
                    entry['promoTypes'].extend(promo_types)
                    break
            else:
                raise ValueError(
                    f'No item with id {menu_item_id} '
                    'found in eats-core response',
                )

    context = Context()

    def _get_utc_time(date_time):
        delivery_time = utils.to_datetime(date_time)
        return delivery_time.astimezone(datetime.timezone.utc).isoformat()

    @mockserver.json_handler(
        '/eats-core-place-menu/internal-api/v1/place/menu/get-cart-discounts',
    )
    def _mock_eats_core_discount(request):
        if not context.available_discounts:
            return mockserver.make_response('Error', 500)

        if context.core_discounts_response:
            return context.core_discounts_response
        return make_discount_resp(request.json)

    @mockserver.json_handler(
        '/eats-core-place-menu/internal-api/v1/set-location',
    )
    def _mock_eats_core_set_location(request):
        req_location = request.json['location']
        if 'latitude' in context.request_params:
            assert 'latitude' in req_location
            assert (
                req_location['latitude'] == context.request_params['latitude']
            )
        if 'longitude' in context.request_params:
            assert 'longitude' in req_location
            assert (
                req_location['longitude']
                == context.request_params['longitude']
            )
        if 'deliveryTime' in context.request_params:
            assert request.json['delivery_time'] == _get_utc_time(
                context.request_params['deliveryTime'],
            )
        else:
            assert 'delivery_time' not in request.json
        return mockserver.make_response('Not found', 404)

    @mockserver.json_handler(
        '/eats-core-place-menu/internal-api/v1/place/menu/get-items',
    )
    def _mock_eats_core_menu(request):
        for item in request.json['items']:
            assert item in context.core_items_request

        if context.core_items_status == 200:
            resp_items_info = context.core_items_response.copy()
            place_menu_items_arr = []
            for item in resp_items_info['place_menu_items']:
                if str(item['id']) in request.json['items']:
                    place_menu_items_arr.append(item)

            resp_items_info['place_menu_items'] = place_menu_items_arr
            return resp_items_info

        return mockserver.make_response(
            json=context.core_items_response, status=context.core_items_status,
        )

    @mockserver.json_handler('/eats-products/api/v2/menu/get-items')
    def _mock_eats_products_menu(request):
        expected_items = (
            context.eats_products_items_request
            if context.eats_products_items_request
            else context.core_items_request
        )
        for item in request.json['items']:
            assert item in expected_items

        if (
                context.core_items_status == 200
                and 'place_menu_items' in context.eats_products_items_response
        ):
            resp_items_info = context.eats_products_items_response.copy()
            place_menu_items_arr = []
            for item in resp_items_info['place_menu_items']:
                if str(item['id']) in request.json['items']:
                    place_menu_items_arr.append(item)

            resp_items_info['place_menu_items'] = place_menu_items_arr
            return resp_items_info

        return mockserver.make_response(
            json=context.eats_products_items_response,
            status=context.core_items_status,
        )

    @mockserver.json_handler(
        '/eats-restaurant-menu/internal/v1/menu/get-items',
    )
    def _mock_eats_restaurant_menu_items(request):
        if 'place_menu_items' in context.eats_restaurant_menu_items_response:
            resp_items_info = (
                context.eats_restaurant_menu_items_response.copy()
            )
            return resp_items_info
        return mockserver.make_response(
            json=context.eats_restaurant_menu_items_response, status=200,
        )

    @mockserver.json_handler('/eats-catalog/internal/v1/place')
    def _mock_eats_catalog(request):
        assert request.json['slug'] in context.place_slugs
        del request.json['slug']
        expected_request = {
            'shipping_type': context.request_params['shippingType'],
            'disable_pricing': True,
        }
        if ('longitude' in context.request_params) and (
                'latitude' in context.request_params
        ):
            expected_request['position'] = [
                context.request_params['longitude'],
                context.request_params['latitude'],
            ]
        if 'deliveryTime' in context.request_params:
            expected_request['delivery_time'] = _get_utc_time(
                context.request_params['deliveryTime'],
            )
        assert request.json == expected_request
        return mockserver.make_response(
            json=context.catalog_place_response,
            status=context.catalog_place_status,
        )

    @mockserver.json_handler(
        '/eda-delivery-price/internal/v1/cart-delivery-price-surge',
    )
    def _mock_eda_delivery_price(request):
        if context.delivery_price_assertion:
            context.delivery_price_assertion(request)
        return mockserver.make_response(
            json=context.delivery_price_response,
            status=context.delivery_price_status,
        )

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/checkout/cashback',
    )
    def _mock_plus_checkout_cashback(request):
        request_json = copy.deepcopy(request.json)
        del request_json['order_id']
        rexpected_json = copy.deepcopy(context.plus_checkout_request)
        del rexpected_json['order_id']
        assert request_json == rexpected_json
        return mockserver.make_response(**context.plus_checkout_response)

    @mockserver.json_handler('/eats-plus/internal/eats-plus/v1/cart/cashback')
    def _mock_plus_cashback(request):
        if context.plus_request:
            assert request.json == context.plus_request
        plus_cart_response = copy.deepcopy(context.plus_response)
        if plus_cart_response.get('cashback_outcome_details'):
            del plus_cart_response['cashback_outcome_details']
        return mockserver.make_response(**plus_cart_response)

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_match_discounts(request):
        assert request.json['common_conditions']['conditions']['tag']
        assert request.json['common_conditions']['conditions']['country']
        return context.eats_discounts_response

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage(request):
        assert context.catalog_place_id in request.json['place_ids']
        return context.eats_catalog_storage_response

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _mock_eats_tags(request):
        assert request.json.get('match', [])
        assert [
            item.get('type') in ['user_id', 'personal_phone_id']
            for item in request.json['match']
        ]
        return mockserver.make_response(
            status=200, json={'tags': ['tag1', '2tag', '3tag3', '1234']},
        )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eta')
    def _mock_cart_eta(request):
        assert request.query['request_type'] == 'default'
        assert request.query['service_name'] == 'eats-cart'

        predicted_times = []

        for requested_time in request.json['requested_times']:
            place_id = str(requested_time['place']['id'])
            times = (
                context.cart_eta.get(place_id) if context.cart_eta else None
            )
            if times is None:
                predicted_times.append(
                    {
                        'id': int(place_id),
                        'times': {
                            'total_time': 110,
                            'cooking_time': 5,
                            'delivery_time': 5,
                            'boundaries': {'min': 25, 'max': 35},
                        },
                    },
                )
                # TODO(EDAJAM-435): Переделать просчёт ETA в testsuite
            else:
                predicted_times.append(
                    {
                        'id': times.place_id,
                        'times': {
                            'total_time': times.total_time,
                            'cooking_time': times.cooking_time,
                            'delivery_time': times.delivery_time,
                            'boundaries': {
                                'min': times.boundaries_min,
                                'max': times.boundaries_max,
                            },
                        },
                    },
                )

        return {
            'exp_list': [],
            'request_id': 'request_id',
            'provider': 'testsuite',
            'predicted_times': predicted_times,
        }

    @mockserver.json_handler(
        '/eats-customer-slots/api/v1/order/validate-delivery-time',
    )
    def _mock_slots_validate_time(request):
        return context.eats_customer_slots_response

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _mock_order_stats(request):
        return mockserver.make_response('Not found', 404)

    @mockserver.json_handler('/eda-delivery-price/v1/user-promo')
    def _eda_delivery_price_user_promo(request):
        return mockserver.make_response('error', status=500)

    context.mock_eats_core_menu = _mock_eats_core_menu
    context.mock_eats_products_menu = _mock_eats_products_menu
    context.mock_eats_catalog = _mock_eats_catalog
    context.mocke_eats_restaurant_menu_items = _mock_eats_restaurant_menu_items
    context.mock_eats_core_discount = _mock_eats_core_discount
    context.mock_plus_checkout_cashback = _mock_plus_checkout_cashback
    context.mock_plus_cashback = _mock_plus_cashback
    context.mock_match_discounts = _mock_match_discounts
    context.mock_eats_catalog_storage = _mock_eats_catalog_storage
    context.mock_eats_core_set_location = _mock_eats_core_set_location
    context.mock_slots_validate_time = _mock_slots_validate_time
    context.mock_eda_delivery_price = _mock_eda_delivery_price
    context.mock_eats_tags = _mock_eats_tags
    return context
