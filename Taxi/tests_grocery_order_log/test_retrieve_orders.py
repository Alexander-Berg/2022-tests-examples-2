# pylint: disable=C5521

import datetime

from tests_grocery_order_log import models
from tests_grocery_order_log.helpers_retrieve import (
    CONFIG_CURRENCY_FORMATTING_RULES,
)
from tests_grocery_order_log.helpers_retrieve import create_cart_items
from tests_grocery_order_log.helpers_retrieve import CURSOR_DATA
from tests_grocery_order_log.helpers_retrieve import fetch_delivery_cost
from tests_grocery_order_log.helpers_retrieve import from_template


@CURSOR_DATA
@CONFIG_CURRENCY_FORMATTING_RULES
async def test_retrieve_orders_basic(
        taxi_grocery_order_log,
        grocery_cold_storage,
        load_json,
        pgsql,
        cursor_data,
):
    orders_info = load_json('grocery_orders_response.json')

    yandex_uid = 'test-uid'
    bound_uid = 'test-uid-1'
    for order_info in orders_info['orders']:
        created_date = datetime.datetime.fromisoformat(
            order_info['created_at'],
        )

        finished_date = datetime.datetime.fromisoformat(
            order_info['closed_at'],
        )
        calculation = order_info['calculation']
        order_log = models.OrderLog(
            pgsql=pgsql,
            order_id=order_info['order_id'],
            short_order_id=order_info['short_order_id'],
            order_created_date=created_date,
            order_finished_date=finished_date,
            cart_id='cart_id',
            courier=order_info['contact']['courier']['name'],
            destination=order_info['destination'],
            legal_entities=order_info['legal_entities'],
            receipts=order_info['receipts'],
            order_state='closed',
            cart_items=create_cart_items(calculation['addends']),
            currency=calculation['currency_code'],
            cart_total_price=from_template(calculation['final_cost']),
            cashback_gain=calculation.get('cashback_gain'),
            cashback_charge=calculation.get('cashback_charge'),
            cart_total_discount=from_template(calculation['discount']),
            delivery_cost=fetch_delivery_cost(calculation['addends']),
            refund=from_template(calculation['refund']),
            yandex_uid=yandex_uid,
            geo_id='test_geo_id',
            country_iso3='RUS',
        )
        order_log.update_db()

        order_log_index = models.OrderLogIndex(
            pgsql=pgsql,
            order_id=order_info['order_id'],
            cart_id='cart_id',
            order_created_date=created_date,
            yandex_uid=yandex_uid,
        )
        order_log_index.update_db()

        order_log.update()
        assert order_log.yandex_uid == yandex_uid

    request_json = {
        'range': cursor_data,
        'user_identity': {
            'yandex_uid': yandex_uid,
            'bound_yandex_uids': [bound_uid],
        },
    }
    response = await taxi_grocery_order_log.post(
        '/lavka/order-log/v1/retrieve',
        headers={'Accept-Language': 'ru-RU'},
        json=request_json,
    )
    assert response.status_code == 200

    assert response.json() == load_json('expected_response.json')
