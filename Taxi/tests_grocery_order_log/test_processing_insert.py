import datetime
import decimal

import psycopg2.extras

from tests_grocery_order_log import helpers
from tests_grocery_order_log import models


async def test_basic(
        taxi_grocery_order_log, grocery_cold_storage, pgsql, load_json,
):
    order_log = models.OrderLog(pgsql)
    order_log_index = models.OrderLogIndex(pgsql, order_id=order_log.order_id)
    request = load_json('default_order_log.json')
    request['order_id'] = order_log.order_id
    request['order_log_info']['order_type'] = 'grocery'

    response = await taxi_grocery_order_log.post(
        '/processing/v1/insert', json=request,
    )

    assert response.status_code == 200

    order_log.update()
    assert order_log.order_id == request['order_id']
    request_order_log_info = request['order_log_info']
    assert (
        order_log.order_created_date.isoformat()
        == request_order_log_info['order_created_date']
    )
    assert (
        order_log.order_finished_date.isoformat()
        == request_order_log_info['order_finished_date']
    )
    assert order_log.order_state == request_order_log_info['order_state']
    assert order_log.order_source == request_order_log_info['order_source']
    assert order_log.cart_id == request_order_log_info['cart_id']
    assert (
        str(order_log.cart_total_price)
        == request_order_log_info['cart_total_price']
    )
    assert (
        str(order_log.cart_total_discount)
        == request_order_log_info['cart_total_discount']
    )
    assert (
        str(order_log.delivery_cost) == request_order_log_info['delivery_cost']
    )
    assert order_log.currency == request_order_log_info['currency']
    models.check_cart_items(
        order_log.cart_items, request_order_log_info['cart_items'],
    )
    assert order_log.depot_id == request_order_log_info['depot_id']
    models.check_legal_entities(
        order_log.legal_entities, request_order_log_info['legal_entities'],
    )
    assert order_log.yandex_uid == request_order_log_info['yandex_uid']
    assert order_log.eats_user_id == request_order_log_info['eats_user_id']
    assert order_log.destination == request_order_log_info['destination']
    assert order_log.courier == request_order_log_info['courier']['name']
    assert order_log.receipts == request_order_log_info['receipts']
    assert order_log.geo_id == request_order_log_info['geo_id']
    assert order_log.country_iso3 == request_order_log_info['country_iso3']
    assert models.cmp_decimal(
        order_log.cashback_gain, request_order_log_info.get('cashback_gain'),
    )
    assert models.cmp_decimal(
        order_log.cashback_charge,
        request_order_log_info.get('cashback_charge'),
    )

    order_log_index.update()
    assert (
        order_log_index.personal_phone_id
        == request_order_log_info['personal_phone_id']
    )
    assert (
        order_log_index.personal_email_id
        == request_order_log_info['personal_email_id']
    )
    assert (
        order_log_index.eats_user_id == request_order_log_info['eats_user_id']
    )
    assert order_log_index.cart_id == request_order_log_info['cart_id']
    assert (
        order_log_index.short_order_id
        == request_order_log_info['short_order_id']
    )
    assert (
        order_log_index.order_created_date.isoformat()
        == request_order_log_info['order_created_date']
    )
    assert order_log_index.yandex_uid == request_order_log_info['yandex_uid']
    assert order_log_index.order_state == order_log.order_state
    assert order_log_index.order_type == 'grocery'

    assert grocery_cold_storage.orders_times_called == 1
    assert grocery_cold_storage.prefetch_times_called == 0


async def test_restore(taxi_grocery_order_log, grocery_cold_storage, pgsql):
    order_id = 'cold-grocery'
    yandex_uid = 'test-uid'
    created_date = '2020-08-11T00:00:00+00:00'

    helpers.add_cold_storage_and_index(
        grocery_cold_storage, yandex_uid, created_date, order_id, pgsql,
    )

    request = {'order_id': order_id, 'order_log_info': {}}
    response = await taxi_grocery_order_log.post(
        '/processing/v1/insert', json=request,
    )

    assert response.status_code == 200

    cold_order_log = grocery_cold_storage.response_body['items'][0]

    cursor = pgsql['grocery_order_log'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute(
        'select * from order_log.order_log where order_id = %s', [order_id],
    )
    pg_order_log = dict(cursor.fetchone())

    pg_order_log.pop('updated')
    expected_order_log = {
        'order_id': cold_order_log['order_id'],
        'short_order_id': cold_order_log['short_order_id'],
        'order_created_date': datetime.datetime.fromisoformat(
            cold_order_log['order_created_date'],
        ).replace(tzinfo=models.UTC_TZ),
        'order_finished_date': datetime.datetime.fromisoformat(
            cold_order_log['order_finished_date'],
        ).replace(tzinfo=models.UTC_TZ),
        'order_state': cold_order_log['order_state'],
        'order_source': cold_order_log['order_source'],
        'cart_id': cold_order_log['cart_id'],
        'cart_total_price': decimal.Decimal(
            cold_order_log['cart_total_price'],
        ),
        'cashback_gain': decimal.Decimal(cold_order_log['cashback_gain']),
        'cashback_charge': decimal.Decimal(cold_order_log['cashback_charge']),
        'cart_total_discount': decimal.Decimal(
            cold_order_log['cart_total_discount'],
        ),
        'delivery_cost': decimal.Decimal(cold_order_log['delivery_cost']),
        'refund': decimal.Decimal(cold_order_log['refund']),
        'currency': cold_order_log['currency'],
        'cart_items': cold_order_log['cart_items'],
        'depot_id': cold_order_log['depot_id'],
        'legal_entities': cold_order_log['legal_entities'],
        'destination': cold_order_log['destination'],
        'courier': cold_order_log['courier'],
        'receipts': cold_order_log['receipts'],
        'yandex_uid': cold_order_log['yandex_uid'],
        'eats_user_id': cold_order_log['eats_user_id'],
        'appmetrica_device_id': cold_order_log['appmetrica_device_id'],
        'geo_id': cold_order_log['geo_id'],
        'country_iso3': cold_order_log['country_iso3'],
        'can_be_archived': None,
        'anonym_id': cold_order_log['anonym_id'],
    }

    assert set(pg_order_log.keys()) == set(expected_order_log.keys())
    assert pg_order_log == expected_order_log
