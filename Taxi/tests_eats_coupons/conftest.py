# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import pytest

from eats_coupons_plugins import *  # noqa: F403 F401

from . import utils

YANDEX_UID = '555'
APP_NAME = 'android'
PHONE_ID = 'abcde'
DATETIME = '2021-05-20T00:00:00+00:00'
DATETIME_FRACTION = '2021-05-20T00:00:00.123+00:00'

HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Idempotency-Token': 'update-token',
    'X-Request-Language': 'ru',
    'X-Request-Application': f'app_name={APP_NAME}',
    'X-Yandex-Uid': YANDEX_UID,
    'X-YaTaxi-PhoneId': PHONE_ID,
    'X-Eats-User': (
        'user_id=1,personal_phone_id=2,personal_email_id=3,partner_user_id=4'
    ),
}

HEADERS_PASSPRT_EMPTY = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Idempotency-Token': 'update-token',
    'X-Request-Language': 'ru',
    'X-Request-Application': f'app_name={APP_NAME}',
    'X-YaTaxi-PhoneId': PHONE_ID,
    'X-Eats-User': (
        'user_id=1,personal_phone_id=2,personal_email_id=3,partner_user_id=4'
    ),
}


def make_counter(cnt: utils.StatsCounter):
    properties = []
    if cnt.brand_id:
        properties.append({'name': 'brand_id', 'value': cnt.brand_id})

    properties.append({'name': 'business_type', 'value': cnt.business})

    return {
        'properties': properties,
        'value': cnt.counter,
        'first_order_at': '2019-12-11T09:00:00+0000',
        'last_order_at': '2020-12-11T09:00:00+0000',
    }


@pytest.fixture
def mock_order_stats(mockserver):
    class Context:
        yandex_uids = [YANDEX_UID]
        order_stats_client = None
        exp_identities_cnt = 3
        orders_cnt = [utils.StatsCounter(5)]

    context = Context()

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _mock_order_stats(request):
        body = request.json
        assert (
            len(body['identities']) == context.exp_identities_cnt
        )  # device, eater, phone
        while len(context.orders_cnt) < context.exp_identities_cnt:
            context.orders_cnt.append(utils.StatsCounter(0))
        return mockserver.make_response(
            json={
                'data': [
                    {
                        'identity': {'type': 'eater_id', 'value': '1'},
                        'counters': [make_counter(cnt)],
                    }
                    for cnt in context.orders_cnt
                ],
            },
        )

    context.order_stats_client = _mock_order_stats
    return context


@pytest.fixture(name='eats_coupons_cursor')
def get_eats_coupons_cursor(pgsql):
    return pgsql['eats_coupons'].dict_cursor()


@pytest.fixture
def mock_core_client(mockserver):
    class Context:
        yandex_uids = [YANDEX_UID]
        mock_core_stats = None

    context = Context()

    @mockserver.json_handler('/eats-core-promocodes/get-stat')
    def _mock_core_stats(request):
        body = request.json
        assert set(body['yandex_uids']) == set(context.yandex_uids)
        if body['type'] == 'order-sequence':
            return mockserver.make_response(
                json={'data': {'counters': [{'value': 3}]}},
            )
        if body['type'] == 'orders-in-services-and-apps':
            return mockserver.make_response(
                json={'data': {'counters': [{'value': 0}]}},
            )
        if body['type'] == 'orders-in-places':
            return mockserver.make_response(
                json={'data': {'counters': [{'value': 0}]}},
            )
        if body['type'] == 'orders-in-brands':
            return mockserver.make_response(
                json={'data': {'counters': [{'value': 0}]}},
            )
        if body['type'] == 'orders':
            return mockserver.make_response(
                json={'data': {'counters': [{'value': 0}]}},
            )
        return mockserver.make_response(status=400)

    context.mock_core_stats = _mock_core_stats
    return context


DEFAULT_REQUEST = {
    'yandex_uid': 'uid',
    'application_name': 'app',
    'brand_name': 'brand',
    'token': 'token&',
    'promocode_type': 'welcome',
    'value': 30,
    'reason': {
        'default_value': 'default_value_if_key_not_found',
        'tanker_key': 'tanker_key',
        'tanker_args': [
            {'key': 'key1', 'value': 'value1'},
            {'key': 'key2', 'value': 'value2'},
        ],
    },
    'expire_at': DATETIME,
    'conditions': {
        'country': 'rus',
        'refund_type': 'percent',
        'brand_ids': [4, 2, 5, 7, 1],
    },
}

PATH = '/internal/generate'

PROMOCODE_DESCRIPTION = {
    'series_and_conditions': [
        {
            'series': 'series1',
            'value': 30,
            'conditions': {
                'refund_type': 'percent',
                'country': 'rus',
                'brand_ids': [4, 2, 5, 1, 7],
            },
        },
        {
            'series': 'series2',
            'value': 100,
            'conditions': {
                'refund_type': 'fixed',
                'country': 'rus',
                'brand_ids': [4, 2, 5, 1, 7],
            },
        },
        {
            'series': 'series3',
            'value': 10,
            'conditions': {
                'refund_type': 'percent',
                'country': 'rus',
                'brand_ids': [4, 2, 5, 1, 7],
                'other1': [4, 2, 3],
                'other2': ['hello', 'world'],
                'other3': 123,
                'other4': 'Hello world',
            },
        },
    ],
}


class RequestParams:
    def __init__(self, promo_num, value, promocode):
        self.promo_num = promo_num
        self.value = value
        self.promocode = promocode


class ResponseParams:
    def __init__(self, code, message='msg'):
        self.code = code
        self.message = message


class Context:
    def __init__(self):
        self.params = RequestParams(0, 10, 'welcome')

    def set_params(self, params):
        self.params = params


@pytest.fixture
def request_context():
    return Context()


@pytest.fixture
def response_context():
    return Context()


@pytest.fixture
def mock_coupons_client(mockserver, request_context):
    @mockserver.json_handler('/coupons/internal/generate')
    def _mock_coupons(request):
        assert request.json == {
            'yandex_uid': DEFAULT_REQUEST['yandex_uid'],
            'application_name': DEFAULT_REQUEST['application_name'],
            'brand_name': DEFAULT_REQUEST['brand_name'],
            'token': DEFAULT_REQUEST['token'],
            'series_id': PROMOCODE_DESCRIPTION['series_and_conditions'][
                request_context.params.promo_num
            ]['series'],
            'value': request_context.params.value,
            'reason': DEFAULT_REQUEST['reason'],
            'expire_at': DEFAULT_REQUEST['expire_at'],
        }
        return {
            'promocode': request_context.params.promocode,
            'promocode_params': {
                'value': request_context.params.value,
                'expire_at': DEFAULT_REQUEST['expire_at'],
                'currency_code': 'RUB',
            },
        }


@pytest.fixture
def mock_coupons_response_proxy(request, mockserver, response_context):
    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons/v1/couponcheck')
    def _mock_coupons_check(request):
        return mockserver.make_response(
            status=response_context.params.code,
            json={
                'code': str(response_context.params.code),
                'message': response_context.params.message,
            },
        )

    @mockserver.json_handler('/coupons/internal/coupon_finish')
    def _mock_coupons_finish(request):
        return mockserver.make_response(
            status=response_context.params.code,
            json={
                'code': str(response_context.params.code),
                'message': response_context.params.message,
            },
        )

    @mockserver.json_handler('/coupons/v1/couponreserve')
    def _mock_coupons_reserve(request):
        return mockserver.make_response(
            status=response_context.params.code,
            json={
                'code': str(response_context.params.code),
                'message': response_context.params.message,
            },
        )

    @mockserver.json_handler('/coupons/internal/couponlist')
    def _mock_coupons_list(request):
        return mockserver.make_response(
            status=response_context.params.code,
            json={
                'code': str(response_context.params.code),
                'message': response_context.params.message,
            },
        )

    @mockserver.json_handler('/coupons/internal/generate')
    def _mock_coupons_generate(request):
        return mockserver.make_response(
            status=response_context.params.code,
            json={
                'code': str(response_context.params.code),
                'message': response_context.params.message,
            },
        )


def get_eats_cart_response(
        load_json,
        brand_id=None,
        place_id=None,
        shipping_type=None,
        cart_total=None,
        place_menu_items=None,
):
    default_eats_cart_response = load_json('default_eats_cart_response.json')
    if brand_id:
        assert False
    if place_id:
        default_eats_cart_response['place']['id'] = place_id
    if shipping_type:
        default_eats_cart_response['shipping_type'] = shipping_type
    if cart_total:
        default_eats_cart_response['total'] = cart_total
    if place_menu_items:
        assert False
    return default_eats_cart_response
