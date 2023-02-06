import pytest

from tests_grocery_cart.plugins import keys


DEFAULT_QUANTITY = 1

UPDATE_IDEMPOTENCY_TOKEN = 'update-token'
APPLY_PROMOCODE_IDEMPOTENCY_TOKEN = 'promocode-token'
PROMOCODES_LIST_IDEMPOTENCY_TOKEN = 'promocodes-list-token'

SELECT_CART_SQL = """
    SELECT cart_id, cart_version, checked_out, updated,
    idempotency_token, promocode, user_type, user_id, session,
    payment_method_type, payment_method_id, payment_method_meta,
    status, delivery_type, cashback_flow, delivery_cost, child_cart_id,
    tips_amount, tips_amount_type,
    depot_id, timeslot_start, timeslot_end, timeslot_request_kind,
    personal_phone_id, yandex_uid, bound_uids, bound_sessions,
    anonym_id
    FROM cart.carts WHERE cart_id = %s
"""
SELECT_CHECKOUT_DATA_SQL = """
    SELECT cart_id, promocode_discount,
    calculation_log, items_pricing, cashback_to_pay, service_fee
    FROM cart.checkout_data where cart_id = %s
"""
SELECT_ITEMS_SQL = """
    SELECT
        item_id, price, quantity, status, reserved, vat, currency,
        refunded_quantity, cashback, is_expiring, supplier_tin
    FROM cart.cart_items WHERE cart_id = %s
"""
UPSERT_ITEM_SQL = """
    INSERT INTO cart.cart_items
    (cart_id, item_id, price, quantity, currency, reserved)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (cart_id, item_id)
    DO UPDATE
    SET
        price = excluded.price,
        quantity = excluded.quantity,
        currency = excluded.currency,
        reserved = excluded.reserved
"""

SET_ITEMS_PRICING_FIELD_SQL = """
UPDATE cart.checkout_data SET
    items_pricing = %s
WHERE cart_id = %s
"""

SELECT_PROMOCODE_SQL = """
    SELECT cart_id, promocode, currency, source, valid, discount,
     error_code, properties
    FROM cart.cart_promocode WHERE cart_id = %s
"""

YANDEX_UID = 'some_uid'
SET_CART_PROPERTY = 'UPDATE cart.carts SET {} = %s WHERE cart_id = %s'
TAXI_HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Idempotency-Token': UPDATE_IDEMPOTENCY_TOKEN,
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-Yandex-UID': YANDEX_UID,
}

EDATAXI_HEADERS = {
    'X-YaTaxi-User': 'eats_user_id=123',
    'X-Yandex-UID': 'some_other_uid',
    'X-YaTaxi-Bound-Uids': 'some_uid',
    'X-YaTaxi-Session': 'eats:123',
    'X-Idempotency-Token': UPDATE_IDEMPOTENCY_TOKEN,
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
}

CASHBACK_HEADERS = {
    'X-YaTaxi-Pass-Flags': 'ya-plus',
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Idempotency-Token': UPDATE_IDEMPOTENCY_TOKEN,
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-Yandex-UID': YANDEX_UID,
}

GROCERY_ORDER_FLOW_VERSION_CONFIG = pytest.mark.experiments3(
    name='grocery_order_flow_version',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always',
            'predicate': {'type': 'true'},
            'value': {'flow_version': 'grocery_flow_v1'},
        },
    ],
    default_value={},
    is_config=True,
)

GROCERY_ORDER_CYCLE_ENABLED = pytest.mark.experiments3(
    name='grocery_order_cycle_enabled',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'always',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)


class CartHttpError(Exception):
    def __init__(self, response):
        super().__init__(f'Cart status code {response.status_code}')
        self.status_code = response.status_code
        self.response_json = response.json()


def add_delivery_conditions(
        experiments3, delivery, surge=False, enable_newbies=False,
):

    basic_clause = {
        'title': 'Always enabled',
        'predicate': {'type': 'true'},
        'value': {
            'data': [
                {
                    'payload': {
                        'surge': surge,
                        'delivery_conditions': [
                            {
                                'order_cost': '0',
                                'delivery_cost': delivery['cost'],
                            },
                            {
                                'order_cost': delivery['next_threshold'],
                                'delivery_cost': delivery['next_cost'],
                            },
                        ],
                    },
                    'timetable': [
                        {
                            'to': '00:00',
                            'from': '00:00',
                            'day_type': 'everyday',
                        },
                    ],
                },
            ],
            'enabled': True,
        },
    }

    newbie_clause = {
        'title': 'Newbies enabled',
        'predicate': {
            'init': {
                'value': 1,
                'arg_name': 'user_orders_completed',
                'arg_type': 'int',
            },
            'type': 'lt',
        },
        'value': {
            'data': [
                {
                    'payload': {
                        'surge': False,
                        'delivery_conditions': [
                            {'order_cost': '0', 'delivery_cost': '0'},
                        ],
                    },
                    'timetable': [
                        {
                            'to': '00:00',
                            'from': '00:00',
                            'day_type': 'everyday',
                        },
                    ],
                },
            ],
            'enabled': True,
        },
    }
    clauses = [basic_clause]
    if enable_newbies:
        clauses.insert(0, newbie_clause)

    experiments3.add_config(
        name='grocery-surge-delivery-conditions',
        consumers=['grocery-surge-client/surge'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=clauses,
    )


def create_offer(
        offers,
        experiments3,
        grocery_surge,
        depot_id='0',
        offer_id='some_offer_id',
        delivery=None,
        min_eta=None,
        max_eta=None,
        minimum_order=None,
        is_surge=False,
        offer_time=None,
        name='calc_surge_grocery_v1',
        delivery_type='pedestrian',
):
    if offer_time is None:
        offer_time = keys.TS_NOW
    offers.add_offer(
        offer_id=offer_id, params={}, payload={'request_time': offer_time},
    )
    grocery_surge.add_record(
        legacy_depot_id=depot_id,
        timestamp=offer_time,
        pipeline=name,
        load_level=0,
        delivery_types=[delivery_type],
    )
    if delivery is not None:
        payload = {
            'delivery_cost': delivery['cost'],
            'surge': is_surge,
            'next_delivery_cost': delivery['next_cost'],
            'next_delivery_threshold': delivery['next_threshold'],
        }
        if min_eta is not None:
            payload['min_eta_minutes'] = min_eta
        if max_eta is not None:
            payload['max_eta_minutes'] = max_eta
        if minimum_order is not None:
            payload['minimum_order'] = minimum_order
        experiments3.add_config(
            name='grocery-p13n-surge',
            consumers=['grocery-surge-client/surge'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {
                        'data': [
                            {
                                'payload': payload,
                                'timetable': [
                                    {
                                        'to': '00:00',
                                        'from': '00:00',
                                        'day_type': 'everyday',
                                    },
                                ],
                            },
                        ],
                    },
                },
            ],
        )


def default_on_modifiers_request(orders_count=None):
    def _inner(headers, body):
        if orders_count is not None:
            assert body['orders_count'] == orders_count
        return True

    return _inner
