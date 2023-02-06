import enum

import pytest

ORDER_NR_ID = 'id1'
ORDER_NR_ID_GROCERY = '11111222223333344444555556666677-grocery'
YA_UID = '3456723'

CLAIM_ID = '54321'
PLACE_ID = '222325'
PLACE_SLUG = 'aaa-bbb'
PLACE_NAME = 'Магнит'
CITY = 'Москва'
PLACE_ADDRESS = 'ул. Абвгд, д. 0'
BRAND_ID = '1'
BRAND_SLUG = 'abc'
BRAND_NAME = 'Магнит'
COURIER_PHONE = {'phone': '+7(800)5553535', 'ext': '1234', 'ttl_seconds': 3600}
APPLICATION = 'go'
PERSONAL_PHONE_ID = 'personal_phone_id'
SAMPLE_TIME = '2021-08-06 12:42:12'
SAMPLE_TIME_CONVERTED = '2021-08-06T12:42:12+00:00'
SAMPLE_TIME_CONVERTED_MS = '2021-08-06T12:42:12.123+00:00'
SAMPLE_TIME_CONVERTED_FOR_BDU_ORDERS = '06 Августа 15:42, 2021'
STRING_DELIMETER = '\',\''


GROCERY_FEEDBACK = {
    'order_nr': '11111222223333344444555556666677-grocery',
    'status': 'wait',
    'has_feedback': False,
}


class StatusForCustomer(enum.IntEnum):
    awaiting_payment = 1
    confirmed = 2
    cooking = 3
    in_delivery = 4
    arrived_to_customer = 5
    delivered = 6
    cancelled = 7
    auto_complete = 8


def core_type(bus_type):
    if bus_type == 'eats':
        return 'restaurant'
    if bus_type == 'shop':
        return 'retail'
    if bus_type == 'grocery':
        return 'grocery'
    return bus_type


def get_auth_headers(
        eater_id='21',
        phone_id='phone123',
        email_id='email456',
        platform='platform',
        version='version',
):
    return {
        'X-YaTaxi-Session': 'eats:in',
        'X-Eats-User': (
            f'user_id={eater_id},'
            f'personal_phone_id={phone_id},'
            f'personal_email_id={email_id}'
        ),
        'X-Yandex-UID': YA_UID,
        'x-platform': platform,
        'x-app-version': version,
    }


def generate_donations(amounts):
    donations = {}
    for order_id, [value, status] in amounts.items():
        donations[order_id] = {
            'status': status,
            'amount_info': {
                'amount': value,
                'currency_code': 'RUB',
                'currency_sign': '₽',
            },
        }
    return donations


def generate_order_hist_donations(amounts):
    donations = {}
    for order_id, [value, status] in amounts.items():
        donations[order_id] = {
            'status': status,
            'amount': value,
            'currency_rules': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
        }
    return donations


def generate_brands_response(exp_order_ids, donations, grocery_orders=None):
    brands_response = []
    for i in range(2):
        elem = {}
        elem['brand'] = 'eats'
        elem['orders'] = []
        if i == 1:
            elem['brand'] = 'lavka'
            if grocery_orders is not None:
                for inner_order in grocery_orders:
                    exp_order_ids[i].append(inner_order['id'])
        for order_id in exp_order_ids[i]:
            elem['orders'].append(
                _build_brand_and_donation(order_id, donations),
            )
        brands_response.append(elem)
    return brands_response


def _build_brand_and_donation(order_id, donations):
    order = {'order_id': order_id}
    if order_id in donations:
        order['donation'] = donations[order_id]
    return order


def add_grocery_info(
        grocery_orders, amounts=None, feedbacks=None, exp_total=None,
):
    if feedbacks is not None:
        feedbacks.append(GROCERY_FEEDBACK)
    for i, order in enumerate(grocery_orders):
        if amounts is not None:
            amounts[order['id']] = [str(i), 'finished']
        if exp_total is not None:
            exp_total.append(
                [order['cart']['total_rational'], order['cart']['total']],
            )


def order_updater_config3(**kwargs):
    return pytest.mark.experiments3(
        name='eats_orders_info_order_updater_settings',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-orders-info/order-updater-settings'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict({'enabled': True}, **kwargs),
    )


def generate_receipts(order_nr, data):
    receipts = []
    for receipt in data:
        receipts.append(
            {
                'order_id': order_nr,
                'document_id': '1',
                'is_refund': (receipt['type'] == 'refund'),
                'country_code': 'RU',
                'created_at': '2021-08-06T12:42:12+00:00',
                'payment_method': 'absent',
                'ofd_info': {'ofd_receipt_url': receipt['receipt_url']},
            },
        )
    return receipts


def standalone_products_config3(**kwargs):
    return pytest.mark.experiments3(
        name='eats_orders_info_standalone_product_settings',
        is_config=True,
        match={
            'consumers': [
                {'name': 'eats-orders-info/standalone-product-settings'},
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[
            {
                'title': 'standalone = using',
                'predicate': {
                    'init': {
                        'arg_name': 'brand_slug',
                        'arg_type': 'string',
                        'value': 'with_standalone',
                    },
                    'type': 'eq',
                },
                'value': {'using_last_product_id': True},
            },
        ],
        default_value=dict({'using_last_product_id': False}, **kwargs),
    )


def order_details_titles_config3():
    return pytest.mark.experiments3(
        name='eats_orders_info_order_details_titles',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-orders-info/description'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value={
            'titles': {
                'title_key': 'order_details.title',
                'tips_title_key': 'order_details.tips',
                'donation_title_key': 'order_details.donation',
                'rest_tips_title_key': 'order_details.rest_tips',
                'items_cost_title_key': 'order_details.items_cost',
                'service_fee_title_key': 'order_details.service_fee',
                'picking_cost_title_key': 'order_details.picking_cost',
                'refund_value_title_key': 'order_details.refund_value',
                'delivery_cost_title_key': 'order_details.delivery_cost',
            },
        },
    )


def format_response(response_body):
    response_body['original_items'].sort(key=lambda item: item['id'])
    response_body['diff']['add'].sort(key=lambda item: item['id'])
    response_body['diff']['remove'].sort(key=lambda item: item['id'])
    response_body['diff']['no_changes'].sort(key=lambda item: item['id'])
    response_body['diff']['replace'].sort(
        key=lambda replacement: replacement['from_item']['id'],
    )
    response_body['diff']['update'].sort(
        key=lambda update: update['from_item']['id'],
    )
    return response_body


async def db_check_orders_removed_dict(pg_realdict_cursor, order_nrs):
    pg_realdict_cursor.execute(
        'SELECT order_nr '
        'FROM eats_orders_info.removed_orders '
        'WHERE order_nr IN (\'{}\')'.format(STRING_DELIMETER.join(order_nrs)),
    )
    return pg_realdict_cursor.fetchone()


def can_be_removed_config3():
    return pytest.mark.experiments3(
        name='eats_orders_info_order_can_be_removed',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-orders-info/can-be-removed'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict({'can_be_removed': True}),
    )


def remove_enabled_config3():
    return pytest.mark.experiments3(
        name='eats_orders_info_remove_feat_enabled',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-orders-info/remove-feat-enabled'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict({'enabled': True}),
    )
