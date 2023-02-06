# pylint: disable=too-many-lines
import decimal
import enum
import json
import typing

import pytest

from .models import cart

DEFAULT_CART_ID = 'a49609bd-741d-410e-9f04-476f46ad43c7'
DEFAULT_OFFER_ID = '01234567-741d-410e-9f04-476f46ad43c7'
CART_DEPOT_ID = 'depot-id'
CART_ID_KEY = 'cart-id'
CART_VERSION_KEY = 'cart-version'
CART_ITEMS_KEY = 'cart-items'
CART_ITEMS_V2_KEY = 'cart-items-v2'
CART_PAYMENT_METHOD_KEY = 'payment-method'
CART_PAYMENT_METHOD_DISCOUNT = 'payment-method-discount'
CART_PERSONAL_WALLET_ID = 'personal-wallet-id'
CART_DELIVERY_TYPE = 'delivery-type'
CART_DELIVERY_ZONE_TYPE = 'delivery-zone-type'
CART_CASHBACK_FLOW = 'cashback-flow'
CART_CASHBACK_TO_PAY = 'cashback-to-pay'
CART_ORDER_CONDITIONS = 'order_conditions'
CART_CHILD_CART_ID = 'child-cart-id'
CART_CORRECT_COPY_HANDLER = 'correct/copy'
CART_CORRECT_COMMIT_HANDLER = 'correct/commit'
CART_CREATE_HANDLER = 'create'
CART_SET_ORDER_ID_HANDLER = 'set-order-id'
CART_CHECKOUT_HANDLER = 'checkout'
CART_LIMITED_DISCOUNT_IDS = 'limited_discount_ids'
CART_VALID_UNTIL_KEY = 'valid_until'
CART_AVAILABLE_FOR_CHECKOUT_KEY = 'available_for_checkout'
CART_CHECKOUT_UNAVAILABLE_REASON_KEY = 'checkout_unavailable_reason'
CART_PROMOCODE_KEY = 'promocode'
CART_LAVKA_ITEMS_KEY = 'cart_lavka_items'
CART_DIFF_DATA_KEY = 'cart_diff_data'
CART_OFFER_ID_KEY = 'offer_id'
CART_SET_TIPS_HANDLER = 'set-tips'
CART_TIPS = 'tips'
ERROR_CODES = 'error-codes'
CART_LOGISTIC_TAGS = 'logistic_tags'
CART_RETRIEVE_RAW = 'cart_retrieve_raw'
MOCK_RESPONSE = 'mock_response'
ACTUAL_CART_HANDLER = 'actual-cart'
CART_CURRENCY_SETTINGS = 'currency_settings'


DEFAULT_ITEMS = [
    cart.GroceryCartItem(
        item_id='item-id-1',
        title='item-1-title',
        price='100.55',
        full_price='150',
        quantity='3',
        currency='RUB',
        vat='20',
        refunded_quantity='0',
        gross_weight=100,
        width=200,
        height=300,
        depth=400,
    ),
]


def _to_template(price):
    return f'{str(price)} $SIGN$$CURRENCY$'


DEFAULT_LAVKA_ITEMS = [
    {
        'id': 'item-id-1',
        'title': 'item-1-title',
        'subtitle': 'item-1-subtitle',
        'price': '99',
        'catalog_price': '99',
        'catalog_price_template': _to_template('99'),
        'catalog_total_price_template': _to_template('297'),
        'is_price_uncrossed': False,
        'full_catalog_price': '150',
        'full_catalog_price_template': _to_template('150'),
        'full_catalog_total_price_template': _to_template('450'),
        'cashback': '7',
        'catalog_cashback': '7',
        'quantity': '3',
        'quantity_limit': '10',
        'currency': 'RUB',
        'image_url_templates': ['cart_item_1.jpg'],
        'discount_label': 'some label',
    },
]

# equals 301.65 if DEFAULT_ITEMS didn't change
DEFAULT_CART_PRICE = sum(
    [
        decimal.Decimal(item.price) * decimal.Decimal(item.quantity)
        for item in DEFAULT_ITEMS
    ],
)


class Handler(enum.Enum):
    checkout = 'checkout'
    refund = 'refund'
    set_order_id = 'set-order-id'
    retrieve_raw = 'retrieve-raw'
    retrieve_list = 'retrieve-list'
    correct_copy = 'correct-copy'
    correct_commit = 'correct-commit'
    create = 'internal-create'
    drop = 'drop'
    retrieve = 'retrieve'
    restore = 'restore'
    update = 'update'
    set_tips = 'set-tips'


class GroceryCart:
    def set_promocode(
            self,
            *,
            code,
            valid,
            source='eats',
            discount='100',
            discount_type='fixed',
            tag=None,
            series_purpose=None,
    ):
        self._payload['promocode_checkout'] = {'code': code, 'valid': valid}
        self._payload['promocode_retrieve'] = {
            'code': code,
            'source': source,
            'discount': discount,
            'series_purpose': series_purpose,
            'discount_type': discount_type,
        }
        if tag is not None:
            self._payload['promocode_retrieve']['tag'] = tag

    def __init__(self):
        self._payload = {}
        self._payload[MOCK_RESPONSE] = {}
        self.refunded_items = None
        self.check_request_data = {}

    def set_depot_id(self, *, depot_id):
        self._payload[CART_DEPOT_ID] = depot_id

    def set_order_conditions(
            self,
            *,
            delivery_cost,
            max_eta: int = 55,
            min_eta: int = 15,
            total_time=None,
            pricing=None,
    ):
        self._payload[CART_ORDER_CONDITIONS] = {
            'delivery_cost': str(delivery_cost),
            'cost': str(delivery_cost),
            'max_eta': max_eta,
            'min_eta': min_eta,
        }
        if total_time is not None:
            self._payload[CART_ORDER_CONDITIONS]['total_time'] = total_time
        if pricing is not None:
            self._payload[CART_ORDER_CONDITIONS]['pricing'] = pricing

    def set_checkout_unavailable_reason(self, reason):
        self._payload[CART_AVAILABLE_FOR_CHECKOUT_KEY] = False
        self._payload[CART_CHECKOUT_UNAVAILABLE_REASON_KEY] = reason

    def set_cart_data(self, *, cart_id, cart_version=1):
        self._payload[CART_ID_KEY] = cart_id
        self._payload[CART_VERSION_KEY] = cart_version

    def set_error_code(self, *, handler, code):
        if ERROR_CODES not in self._payload:
            self._payload[ERROR_CODES] = {}
        self._payload[ERROR_CODES][handler] = code

    def get_error_code(self, *, handler):
        if (
                ERROR_CODES in self._payload
                and handler in self._payload[ERROR_CODES]
        ):
            return self._payload[ERROR_CODES][handler]
        return None

    def set_payment_method(self, payment_method, discount=None):
        self._payload[CART_PAYMENT_METHOD_KEY] = payment_method
        if discount is not None:
            self._payload[CART_PAYMENT_METHOD_DISCOUNT] = discount

    def set_personal_wallet_id(self, personal_wallet_id):
        self._payload[CART_PERSONAL_WALLET_ID] = personal_wallet_id

    def set_cashback_data(self, flow, cashback_to_pay=None):
        self._payload[CART_CASHBACK_FLOW] = flow
        self._payload[CART_CASHBACK_TO_PAY] = cashback_to_pay

    def get_cashback_to_pay(self):
        return self._payload.get(CART_CASHBACK_TO_PAY, None)

    def set_delivery_type(self, delivery_type):
        self._payload[CART_DELIVERY_TYPE] = delivery_type

    def set_limited_discount_ids(self, limited_discount_ids):
        self._payload[CART_LIMITED_DISCOUNT_IDS] = limited_discount_ids

    def set_child_cart_id(self, child_cart_id):
        self._payload[CART_CHILD_CART_ID] = child_cart_id

    def get_child_cart_id(self):
        return self._payload.get(CART_CHILD_CART_ID, None)

    def get_cart_id(self):
        return self._payload.get(CART_ID_KEY, None)

    def get_payment_method(self):
        return self._payload.get(CART_PAYMENT_METHOD_KEY, {})

    def get_items(self) -> typing.List[cart.GroceryCartItem]:
        return self._payload.get(CART_ITEMS_KEY, DEFAULT_ITEMS)

    def get_items_v2(self) -> typing.List[cart.GroceryCartItem]:
        return self._payload.get(CART_ITEMS_V2_KEY, None)

    def set_items(self, items: typing.List[cart.GroceryCartItem]):
        self._payload[CART_ITEMS_KEY] = items

    def set_items_v2(self, items: typing.List[cart.GroceryCartItemV2]):
        self._payload[CART_ITEMS_V2_KEY] = items

    def set_refunded_items(self, items):
        self.refunded_items = {}
        for item in items:
            self.refunded_items[item.item_id] = item.quantity

    def set_delivery_zone_type(self, zone):
        self._payload[CART_DELIVERY_ZONE_TYPE] = zone

    def set_delivery_log_tags(self, tags):
        self._payload[CART_LOGISTIC_TAGS] = tags

    def set_grocery_flow_version(self, flow_version):
        self._payload['flow_version'] = flow_version

    def set_correcting_type(self, correcting_type):
        if correcting_type is None:
            self._payload['correcting_type'] = 'remove'
        else:
            self._payload['correcting_type'] = correcting_type

    def set_correcting_items(self, correcting_items):
        self._payload['correcting_items'] = correcting_items

    def set_currency_settings(self, currency_settings):
        self._payload[CART_CURRENCY_SETTINGS] = currency_settings

    def get_correcting_items(self):
        return self._payload.get('correcting_items', None)

    def get_correcting_type(self):
        return self._payload.get('correcting_type', None)

    def set_client_price(self, client_price):
        self._payload['client_price'] = client_price

    def set_tips(self, tips):
        self._payload[CART_TIPS] = tips

    def set_diff_data(self, diff_data):
        self._payload[CART_DIFF_DATA_KEY] = diff_data

    def mock_response(self, handler: Handler, **kwargs):
        self._payload[MOCK_RESPONSE][handler] = {**kwargs}

    def get_json_raw(self):
        items = []
        fallback_items_v2 = []
        for item in self._payload.get(CART_ITEMS_KEY, DEFAULT_ITEMS):
            items.append(item.as_object())
            fallback_items_v2.append(item.as_object_v2())

        items_v2 = []
        cart_items_v2 = self._payload.get(CART_ITEMS_V2_KEY, None)
        if cart_items_v2 is not None:
            for item_v2 in cart_items_v2:
                items_v2.append(item_v2.as_object())
        else:
            items_v2 = fallback_items_v2

        delivery_zone_type = {}
        if CART_DELIVERY_ZONE_TYPE in self._payload:
            delivery_zone_type = {
                'delivery_zone_type': self._payload.get(
                    CART_DELIVERY_ZONE_TYPE,
                ),
            }

        promocode = {}
        if 'promocode_retrieve' in self._payload:
            promocode_payload = self._payload['promocode_retrieve']
            promocode = {
                'promocode': promocode_payload['code'],
                'promocode_source': promocode_payload['source'],
                'promocode_properties': {
                    'source': promocode_payload['source'],
                    'discount_value': promocode_payload['discount'],
                    'discount_type': promocode_payload['discount_type'],
                    'series_purpose': promocode_payload['series_purpose'],
                },
                'promocode_discount': promocode_payload['discount'],
            }
            if 'tag' in promocode_payload:
                promocode['promocode_properties']['tag'] = promocode_payload[
                    'tag'
                ]

        tags = {}
        if 'tags' in self._payload:
            tags[CART_LOGISTIC_TAGS] = self._payload['tags']

        return {
            'cart_id': self._payload.get(CART_ID_KEY, DEFAULT_CART_ID),
            'cart_version': self._payload.get(CART_VERSION_KEY, 0),
            'depot_id': self._payload.get(
                CART_DEPOT_ID, cart.DEFAULT_DEPOT_ID,
            ),
            'user_type': 'yandex_taxi',
            'user_id': 'user-id',
            'checked_out': True,
            'exists_order_id': False,
            'delivery_type': self._payload.get(
                CART_DELIVERY_TYPE, 'eats_dispatch',
            ),
            'items': items,
            'items_v2': items_v2,
            'payment_method_type': self._payload.get(
                CART_PAYMENT_METHOD_KEY, {},
            ).get('type'),
            'payment_method_id': self._payload.get(
                CART_PAYMENT_METHOD_KEY, {},
            ).get('id'),
            'payment_method_meta': self._payload.get(
                CART_PAYMENT_METHOD_KEY, {},
            ).get('meta'),
            'payment_method_discount': self._payload.get(
                CART_PAYMENT_METHOD_DISCOUNT, None,
            ),
            'personal_wallet_id': self._payload.get(
                CART_PERSONAL_WALLET_ID, None,
            ),
            'total_discount_template': '0 $SIGN$$CURRENCY$',
            'total_item_discounts_template': _to_template('0'),
            'total_promocode_discount_template': _to_template('0'),
            'items_full_price_template': _to_template('1000'),
            'items_price_template': _to_template('1000'),
            'full_total_template': _to_template('1500'),
            'client_price_template': _to_template('1000'),
            'delivery': self._payload.get(CART_ORDER_CONDITIONS, {}),
            'client_price': self._payload.get(
                'client_price',
                '7',  # changing number 7 should not affect on test passing
            ),
            'total_discount': '500',
            'limited_discount_ids': (
                self._payload.get(CART_LIMITED_DISCOUNT_IDS, None)
            ),
            'tips': self._payload.get(CART_TIPS, None),
            'currency_settings': self._payload.get(
                CART_CURRENCY_SETTINGS, None,
            ),
            **delivery_zone_type,
            **promocode,
            **tags,
            **self._payload[MOCK_RESPONSE].get(Handler.retrieve_raw, {}),
        }

    def get_json(self):
        order_conditions = {
            'delivery_cost': '100',
            'delivery_cost_template': _to_template('100'),
            'minimum_order_price': '200',
            'minimum_order_price_template': _to_template('200'),
            'max_eta': 25,
            'min_eta': 10,
        }

        requirements = {
            'next_delivery_cost': '50',
            'sum_to_next_delivery': '700',
            'next_delivery_threshold': '5000',
            'sum_to_min_order': '300',
            'next_delivery_cost_template': _to_template('50'),
            'sum_to_next_delivery_template': _to_template('700'),
            'next_delivery_threshold_template': _to_template('5000'),
            'sum_to_min_order_template': _to_template('300'),
        }

        discount_descriptions = []
        discount_descriptions.append(
            {
                'type': 'mastercard',
                'description_template': (
                    'Скидка $SIGN$50$CURRENCY$ по карте Mastercard'
                ),
                'discount_value': '50',
                'cart_description_template': (
                    'Скидка $SIGN$50$CURRENCY$ по карте Mastercard'
                ),
            },
        )

        cashback = {
            'amount_to_gain': '21',
            'available_for_payment': '0',
            'wallet_id': 'some-wallet-id',
            'full_payment': False,
        }

        cart_money_discount_applied = {
            'info_template': (
                'Скидка 100 $SIGN$$CURRENCY на заказ от 1000 $SIGN$$CURRENCY'
            ),
            'discount_template': _to_template('100'),
        }

        cart_money_discount_suggested = {
            'info_template': (
                'Скидка 200 $SIGN$$CURRENCY на заказ от 2000 $SIGN$$CURRENCY'
            ),
            'discount_template': _to_template('200'),
        }

        basic_cart_discount_applied = {
            'info_template': (
                'Скидка 300 $SIGN$$CURRENCY на заказ от 3000 $SIGN$$CURRENCY'
            ),
            'discount_template': _to_template('300'),
            'picture': 'basic_cart_discount_applied.jpg',
        }

        basic_cart_discount_suggested = {
            'info_template': (
                'Скидка 400 $SIGN$$CURRENCY на заказ от 4000 $SIGN$$CURRENCY'
            ),
            'picture': 'basic_cart_discount_suggested.jpg',
        }

        return {
            'cart_id': self._payload.get(CART_ID_KEY, DEFAULT_CART_ID),
            'offer_id': self._payload.get(CART_OFFER_ID_KEY, DEFAULT_OFFER_ID),
            'cart_version': self._payload.get(CART_VERSION_KEY, 0),
            'valid_until': self._payload.get(
                CART_VALID_UNTIL_KEY, '2020-10-18T13:00:42.109234+00:00',
            ),
            'available_for_checkout': self._payload.get(
                CART_AVAILABLE_FOR_CHECKOUT_KEY, True,
            ),
            'checkout_unavailable_reason': self._payload.get(
                CART_CHECKOUT_UNAVAILABLE_REASON_KEY, None,
            ),
            'hide_price_mismatch': False,
            'total_price_template': _to_template('1000'),
            'total_price_no_delivery_template': _to_template('900'),
            'discount_profit_template': _to_template('200'),
            'discount_profit_no_delivery_template': _to_template('100'),
            'basic_cart_money_discount_applied': cart_money_discount_applied,
            'basic_cart_money_discount_suggested': (
                cart_money_discount_suggested
            ),
            'basic_cart_discount_applied': basic_cart_discount_applied,
            'basic_cart_discount_suggested': basic_cart_discount_suggested,
            'full_price_template': _to_template('1200'),
            'full_price_no_delivery_template': _to_template('1100'),
            'discount_descriptions': discount_descriptions,
            'order_conditions': order_conditions,
            'items': self._payload.get(
                CART_LAVKA_ITEMS_KEY, DEFAULT_LAVKA_ITEMS,
            ),
            'requirements': requirements,
            'promocode': self._payload.get(CART_PROMOCODE_KEY, None),
            'delivery_type': self._payload.get(
                CART_DELIVERY_TYPE, 'eats_dispatch',
            ),
            'l10n': {'some_key': 'some_value'},
            'is_surge': True,
            'available_delivery_types': ['courier', 'rover'],
            'cashback': cashback,
            'order_flow_version': 'grocery_flow_v3',
            'next_idempotency_token': '01234567-abcd-ef00-9f04-476f46ad43c7',
            'currency_sign': '$',
            'diff_data': self._payload.get(CART_DIFF_DATA_KEY, None),
        }

    def get_json_checkout(self, request):
        items = []
        for item in self._payload.get(CART_ITEMS_KEY, DEFAULT_ITEMS):
            items.append(item.as_object())

        payment_method = {}
        if self._payload.get(CART_PAYMENT_METHOD_KEY, None) is not None:
            payment_method['payment_method'] = self._payload[
                CART_PAYMENT_METHOD_KEY
            ]

        if 'flow_version' in self._payload:
            if not self._payload['flow_version']:
                assert 'grocery_flow_version' not in request.json
            else:
                assert (
                    request.json['grocery_flow_version']
                    == self._payload['flow_version']
                )

        return {
            'depot_id': self._payload.get(
                CART_DEPOT_ID, cart.DEFAULT_DEPOT_ID,
            ),
            'items': items,
            'client_price': self._payload.get('client_price', '9000'),
            'total_discount': '0',
            **payment_method,
            'delivery_type': self._payload.get(CART_DELIVERY_TYPE, 'pickup'),
            'order_conditions': self._payload.get('order_conditions', None),
            'payment_method_discount': self._payload.get(
                CART_PAYMENT_METHOD_DISCOUNT, None,
            ),
            'personal_wallet_id': self._payload.get(
                CART_PERSONAL_WALLET_ID, None,
            ),
            'promocode': self._payload.get('promocode_checkout', None),
            'checkout_unavailable_reason': self._payload.get(
                'checkout_unavailable_reason', None,
            ),
            'cashback_flow': self._payload.get(CART_CASHBACK_FLOW, None),
            'delivery_zone_type': self._payload.get(
                CART_DELIVERY_ZONE_TYPE, None,
            ),
            'limited_discount_ids': self._payload.get(
                CART_LIMITED_DISCOUNT_IDS, None,
            ),
            **self._payload[MOCK_RESPONSE].get(Handler.checkout, {}),
        }


@pytest.fixture(name='grocery_cart')
def mock_grocery_cart(mockserver):
    carts = {}
    cart_by_order = {}
    default_cart = GroceryCart()
    cashback_info_response = {}
    cashback_info_request = {}

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/retrieve/raw')
    def mock_internal_retrieve_raw(request):
        _check_request(default_cart, request, Handler.retrieve_raw)

        code = default_cart.get_error_code(handler=CART_RETRIEVE_RAW)
        if code is not None:
            return mockserver.make_response(
                json.dumps({'code': 'NO_CODE', 'message': 'error-message'}),
                code,
            )

        cart_id = request.json.get('cart_id', None)
        if cart_id is None:
            cart_id = request.json.get('order_id', None)
        if cart_id in carts:
            code = carts[cart_id].get_error_code(handler=CART_RETRIEVE_RAW)
            if code is not None:
                return mockserver.make_response(
                    json.dumps(
                        {'code': 'NO_CODE', 'message': 'error-message'},
                    ),
                    code,
                )
            return carts[cart_id].get_json_raw()
        return default_cart.get_json_raw()

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/correct/copy')
    def mock_internal_correct_copy(request):
        _check_request(default_cart, request, Handler.correct_copy)

        code = default_cart.get_error_code(handler=CART_CORRECT_COPY_HANDLER)
        if code is not None:
            return mockserver.make_response(
                json.dumps({'code': 'NO_CODE', 'message': ''}), code,
            )

        assert (
            request.json['correcting_type']
            == default_cart.get_correcting_type()
        )

        correcting_items = default_cart.get_correcting_items()
        if correcting_items is not None:

            def item_to_str(item):
                return '{}-{}'.format(item['item_id'], item['new_quantity'])

            assert len(request.json['correcting_items']) == len(
                correcting_items,
            )
            assert sorted(
                [
                    item_to_str(item)
                    for item in request.json['correcting_items']
                ],
            ) == sorted([item_to_str(item) for item in correcting_items])

        return {
            'cart_version': request.json['correcting_cart_version'] + 1,
            'child_cart_id': default_cart.get_child_cart_id(),
        }

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/correct/commit')
    def mock_internal_correct_commit(request):
        _check_request(default_cart, request, Handler.correct_commit)

        assert (
            request.json.get('correcting_type', None)
            == default_cart.get_correcting_type()
        )

        code = default_cart.get_error_code(handler=CART_CORRECT_COMMIT_HANDLER)
        if code is not None:
            return mockserver.make_response(
                json.dumps({'code': 'NO_CODE', 'message': ''}), code,
            )

        return {'cart_version': request.json['cart_version'] + 1}

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/create')
    def mock_internal_create(request):
        _check_request(default_cart, request, Handler.create)

        code = default_cart.get_error_code(handler=CART_CREATE_HANDLER)
        if code is not None:
            return mockserver.make_response(
                json.dumps({'code': 'INVALID_ITEMS', 'message': ''}), code,
            )

        return {
            'cart_id': DEFAULT_CART_ID,
            'cart_version': 1,
            'offer_id': DEFAULT_OFFER_ID,
        }

    @mockserver.json_handler('/grocery-cart/internal/v2/cart/checkout')
    def mock_internal_checkout(request):
        _check_request(default_cart, request, Handler.checkout)

        if default_cart.get_cashback_to_pay() is not None:
            assert request.json == {}

        code = default_cart.get_error_code(handler=CART_CHECKOUT_HANDLER)
        if code is not None:
            return mockserver.make_response(
                json.dumps({'code': 'NO_CODE', 'message': ''}), code,
            )

        cart_id = request.json['cart_id']
        if cart_id in carts:
            return carts[cart_id].get_json_checkout(request)
        return default_cart.get_json_checkout(request)

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/set-order-id')
    def mock_set_order_id(request):
        _check_request(default_cart, request, Handler.set_order_id)

        code = default_cart.get_error_code(handler=CART_SET_ORDER_ID_HANDLER)
        if code is not None:
            return mockserver.make_response(
                json.dumps({'code': 'NO_CODE', 'message': ''}), code,
            )

        return {}

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/refund')
    def mock_internal_refund(request):
        _check_request(default_cart, request, Handler.refund)

        if default_cart.refunded_items:
            requested_items = request.json['item_refunds']
            assert len(requested_items) == len(default_cart.refunded_items)
            for requested_item in requested_items:
                assert (
                    requested_item['refunded_quantity']
                    == default_cart.refunded_items[requested_item['item_id']]
                )
        return {'depot_id': '', 'delivery_type': 'eats_dispatch'}

    @mockserver.json_handler('/grocery-cart/lavka/v1/cart/v1/drop')
    def mock_lavka_drop(request):
        _check_request(default_cart, request, Handler.drop)

        cart_id = request.json['cart_id']
        if cart_id in carts:
            return carts[cart_id].get_json_raw()
        return mockserver.make_response(
            json.dumps({'code': 'NO_CODE', 'message': 'Cart not found'}), 404,
        )

    @mockserver.json_handler('/grocery-cart/lavka/v1/cart/v1/retrieve')
    def mock_lavka_retrieve(request):
        _check_request(default_cart, request, Handler.retrieve)

        if 'cart_id' in request.json:
            cart_id = request.json['cart_id']
            if cart_id in carts:
                return carts[cart_id].get_json()
        return mockserver.make_response(
            json.dumps(
                {'code': 'CART_NOT_FOUND', 'message': 'Cart not found'},
            ),
            404,
        )

    @mockserver.json_handler('/grocery-cart/lavka/v1/cart/v1/restore')
    def mock_lavka_restore(request):
        _check_request(default_cart, request, Handler.restore)

        order_id = request.json['order_id']
        if order_id in cart_by_order:
            return cart_by_order[order_id].get_json()
        return mockserver.make_response(
            json.dumps({'code': 'NO_CODE', 'message': 'Cart not found'}), 404,
        )

    @mockserver.json_handler('/grocery-cart/lavka/v1/cart/v1/update')
    def mock_lavka_update(request):
        _check_request(default_cart, request, Handler.update)

        if 'cart_id' in request.json:
            cart_id = request.json['cart_id']
            if cart_id in carts:
                return carts[cart_id].get_json()
        return mockserver.make_response(
            json.dumps(
                {'code': 'CART_NOT_FOUND', 'message': 'Cart not found'},
            ),
            404,
        )

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/set-tips')
    def mock_internal_set_tips(request):
        _check_request(default_cart, request, Handler.set_tips)

        code = default_cart.get_error_code(handler=CART_SET_TIPS_HANDLER)
        if code is not None:
            return mockserver.make_response(
                json.dumps({'code': 'NO_CODE', 'message': ''}), code,
            )

        if 'cart_id' in request.json:
            cart_id = request.json['cart_id']
            if cart_id in carts:
                return {
                    'cart_id': request.json['cart_id'],
                    'tips': (
                        request.json['tips']
                        if 'tips' in request.json
                        else None
                    ),
                }

        return mockserver.make_response(
            json.dumps({'code': 'NO_CODE', 'message': 'Cart not found'}), 404,
        )

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/cashback-info')
    def _mock_cashback_info(request):
        if 'order_id' in cashback_info_request:
            assert (
                request.json['order_id'] == cashback_info_request['order_id']
            )

        if 'yt_lookup' in cashback_info_request:
            assert (
                request.json['yt_lookup'] == cashback_info_request['yt_lookup']
            )

        response = {
            'order_id': cashback_info_response['order_id'],
            'depot': {'franchise': cashback_info_response['franchise']},
            'items': cashback_info_response['items'],
        }

        if 'cashback_on_cart_percent' in cashback_info_response:
            response['cashback_on_cart_percent'] = cashback_info_response[
                'cashback_on_cart_percent'
            ]

        if 'cart_cashback_gain' in cashback_info_response:
            response['cart_cashback_gain'] = cashback_info_response[
                'cart_cashback_gain'
            ]

        return response

    @mockserver.json_handler(
        '/grocery-cart/internal/v2/cart/retrieve/actual-cart',
    )
    def _mock_actual_cart(request):
        _check_request(default_cart, request, None)

        code = default_cart.get_error_code(handler=ACTUAL_CART_HANDLER)
        if code is not None:
            return mockserver.make_response(
                json.dumps({'code': 'NO_CODE', 'message': ''}), code,
            )

        return {'cart_id': default_cart.get_cart_id()}

    class Context:
        @property
        def default_cart(self):
            return default_cart

        def add_cart(self, cart_id, order_id=None):
            assert cart_id not in carts
            cart_obj = GroceryCart()
            cart_obj.set_cart_data(cart_id=cart_id)
            carts[cart_id] = cart_obj
            if order_id is not None:
                cart_by_order[order_id] = cart_obj
            return cart_obj

        def get_cart(self, cart_id):
            return carts[cart_id]

        def get_or_create_cart(self, cart_id):
            if cart_id is None:
                return self.default_cart
            if cart_id in carts:
                return self.get_cart(cart_id)
            return self.add_cart(cart_id)

        def mock_response(self, handler: Handler, **kwargs):
            default_cart.mock_response(handler, **kwargs)

        def set_depot_id(self, *, depot_id):
            default_cart.set_depot_id(depot_id=depot_id)

        def set_promocode(
                self, *, code, valid, source='eats', discount='100', **kwargs,
        ):
            default_cart.set_promocode(
                code=code,
                valid=valid,
                source=source,
                discount=discount,
                **kwargs,
            )

        def set_order_conditions(
                self,
                *,
                delivery_cost,
                max_eta: int = 55,
                min_eta: int = 15,
                total_time=None,
                pricing=None,
        ):
            default_cart.set_order_conditions(
                delivery_cost=delivery_cost,
                max_eta=max_eta,
                min_eta=min_eta,
                total_time=total_time,
                pricing=pricing,
            )

        def set_checkout_unavailable_reason(self, reason):
            default_cart.set_checkout_unavailable_reason(reason=reason)

        def set_cart_data(self, *, cart_id, cart_version=1):
            default_cart.set_cart_data(
                cart_id=cart_id, cart_version=cart_version,
            )

        def set_cart_version(self, *, cart_id, cart_version):
            carts[cart_id].set_cart_data(
                cart_id=cart_id, cart_version=cart_version,
            )

        def set_payment_method(
                self, payment_method, discount=None, cart_id=None,
        ):
            self.get_or_create_cart(cart_id).set_payment_method(
                payment_method=payment_method, discount=discount,
            )

        def set_personal_wallet_id(self, personal_wallet_id):
            default_cart.set_personal_wallet_id(
                personal_wallet_id=personal_wallet_id,
            )

        def set_cashback_data(self, flow, cashback_to_pay=None):
            default_cart.set_cashback_data(flow)

        def set_delivery_type(self, delivery_type):
            default_cart.set_delivery_type(delivery_type=delivery_type)

        def set_limited_discount_ids(self, limited_discount_ids=None):
            default_cart.set_limited_discount_ids(
                limited_discount_ids=limited_discount_ids,
            )

        def set_child_cart_id(self, child_cart_id):
            default_cart.set_child_cart_id(child_cart_id=child_cart_id)

        def get_child_cart_id(self):
            return default_cart.get_child_cart_id()

        def check_refunded_items(self, items=None):
            if items:
                default_cart.set_refunded_items(items)
            else:
                default_cart.set_refunded_items(self.get_items())

        def get_payment_method(self):
            return default_cart.get_payment_method()

        def get_items(self) -> [cart.GroceryCartItem]:
            return default_cart.get_items()

        def get_items_v2(self) -> [cart.GroceryCartItemV2]:
            return default_cart.get_items_v2()

        def set_items(
                self, items: typing.List[cart.GroceryCartItem], cart_id=None,
        ):
            self.get_or_create_cart(cart_id).set_items(items)

        def set_items_v2(
                self, items: typing.List[cart.GroceryCartItemV2], cart_id=None,
        ):
            self.get_or_create_cart(cart_id).set_items_v2(items)

        def set_client_price(self, client_price, cart_id=None):
            self.get_or_create_cart(cart_id).set_client_price(client_price)

        def set_tips(self, tips):
            self.default_cart.set_tips(tips)

        def retrieve_times_called(self):
            return mock_internal_retrieve_raw.times_called

        def checkout_times_called(self):
            return mock_internal_checkout.times_called

        def set_order_id_times_called(self):
            return mock_set_order_id.times_called

        def internal_set_tips_called(self):
            return mock_internal_set_tips.times_called

        def set_delivery_zone_type(self, zone):
            default_cart.set_delivery_zone_type(zone)

        def set_logistic_tags(self, logistic_tags):
            default_cart.set_delivery_log_tags(logistic_tags)

        def set_grocery_flow_version(self, flow_version):
            default_cart.set_grocery_flow_version(flow_version)

        def set_correcting_items(self, correcting_items):
            default_cart.set_correcting_items(correcting_items)

        def set_correcting_type(self, correcting_type):
            default_cart.set_correcting_type(correcting_type)

        def set_currency_settings(self, currency_settings):
            default_cart.set_currency_settings(currency_settings)

        def check_cashback_info_request(self, **kwargs):
            cashback_info_request.update({**kwargs})

        def set_cashback_info_response(
                self,
                order_id,
                franchise=True,
                items=None,
                yt_lookup=None,
                cashback_on_cart_percent=None,
                cart_cashback_gain=None,
        ):
            cashback_info_response['order_id'] = order_id
            cashback_info_response['franchise'] = franchise
            cashback_info_response['items'] = [] if items is None else items
            if yt_lookup:
                cashback_info_response['yt_lookup'] = yt_lookup
            if cashback_on_cart_percent:
                cashback_info_response[
                    'cashback_on_cart_percent'
                ] = cashback_on_cart_percent
            if cart_cashback_gain:
                cashback_info_response[
                    'cart_cashback_gain'
                ] = cart_cashback_gain

        def flush_all(self):
            mock_internal_retrieve_raw.flush()
            mock_internal_checkout.flush()
            mock_set_order_id.flush()
            mock_internal_correct_copy.flush()
            mock_internal_correct_commit.flush()
            mock_internal_set_tips.flush()

        def refund_times_called(self):
            return mock_internal_refund.times_called

        def create_times_called(self):
            return mock_internal_create.times_called

        def correct_copy_times_called(self):
            return mock_internal_correct_copy.times_called

        def correct_commit_times_called(self):
            return mock_internal_correct_commit.times_called

        def mock_lavka_drop_times_called(self):
            return mock_lavka_drop.times_called

        def mock_retrieve_times_called(self):
            return mock_lavka_retrieve.times_called

        def mock_restore_times_called(self):
            return mock_lavka_restore.times_called

        def mock_update_times_called(self):
            return mock_lavka_update.times_called

        def set_correct_copy_error(self, code):
            default_cart.set_error_code(
                handler=CART_CORRECT_COPY_HANDLER, code=code,
            )

        def set_correct_commit_error(self, code):
            default_cart.set_error_code(
                handler=CART_CORRECT_COMMIT_HANDLER, code=code,
            )

        def set_set_order_id_error(self, code):  # lol
            default_cart.set_error_code(
                handler=CART_SET_ORDER_ID_HANDLER, code=code,
            )

        def set_create_error(self, code):
            default_cart.set_error_code(handler=CART_CREATE_HANDLER, code=code)

        def set_checkout_error(self, code):
            default_cart.set_error_code(
                handler=CART_CHECKOUT_HANDLER, code=code,
            )

        def set_actual_cart_error(self, code):
            default_cart.set_error_code(handler=ACTUAL_CART_HANDLER, code=code)

        def check_request(
                self,
                fields_to_check,
                headers=None,
                handler: typing.Optional[Handler] = None,
        ):
            if headers is None:
                headers = {}
            default_cart.check_request_data = {
                'fields': fields_to_check,
                'headers': headers,
                'handler': handler,
            }

        # pylint: disable=protected-access
        def _check_request(self, request, handler):
            data = default_cart.check_request_data
            if not data:
                return

            if data['handler'] is None or data['handler'] == handler:
                for field in data['fields']:
                    assert data['fields'][field] == request.json[field]

                for header in data['headers']:
                    assert data['headers'][header] == request.headers[header]

    context = Context()
    return context


def _check_request(cart_instance, request, handler):
    data = cart_instance.check_request_data
    if not data:
        return

    if data['handler'] is None or data['handler'] == handler:
        for field in data['fields']:
            if data['fields'][field] is not None:
                assert data['fields'][field] == request.json[field]
            else:
                assert field not in request.json

        for header in data['headers']:
            if data['headers'][header] is not None:
                assert data['headers'][header] == request.headers[header]
            else:
                assert header not in request.headers
