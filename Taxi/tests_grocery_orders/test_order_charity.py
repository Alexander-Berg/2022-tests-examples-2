import copy
import json

import pytest

from . import headers
from . import helpers
from . import models


X_YATAXI_USER_ID = 'taxi_user_id'
X_LOGIN_ID = 'login_id'

DEPOT_ID = '2809'

BILLING_SETTINGS_VERSION = 'settings-version'

HELPING_HAND = pytest.mark.experiments3(
    name='grocery_help_is_near',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'start_enabled': True, 'finish_enabled': True},
        },
    ],
    is_config=True,
)


@HELPING_HAND
async def test_success_hold_money_starts_charity(
        taxi_grocery_orders, pgsql, grocery_cart, processing, grocery_depots,
):
    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        state=models.OrderState(wms_reserve_status='success'),
    )
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_cart.set_payment_method({'type': 'googlepay', 'id': 'id'})
    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID)

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {'success': True},
        },
    )
    assert response.status_code == 200

    assert _get_last_processing_events(processing, order) == [
        {'order_id': order.order_id, 'reason': 'start_charity'},
    ]


async def test_processing_starts_charity(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, stq,
):
    order = models.Order(
        pgsql=pgsql, billing_settings_version=BILLING_SETTINGS_VERSION,
    )
    _setup_headers(pgsql, order.order_id)

    cart_price = '55'

    item_id = cart_price + '-cost-cart'  # 55-cost-cart
    grocery_cart.set_items_v2(
        [models.make_cart_item_v2(item_id, cart_price, '1')],
    )

    payment_method_type = 'googlepay'
    payment_method_id = 'pm_id'
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_cart.set_payment_method(
        {'type': payment_method_type, 'id': payment_method_id},
    )
    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )

    region_id = 2809
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID, region_id=region_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/charity/start',
        json={'order_id': order.order_id, 'payload': {}},
    )
    assert response.status_code == 200

    assert stq.persey_payments_grocery_order_confirmed.times_called == 1
    args = stq.persey_payments_grocery_order_confirmed.next_call()

    assert args['id'] == order.order_id
    args['kwargs'].pop('log_extra')
    assert args['kwargs'] == {
        'amount': cart_price,
        'currency_code': 'RUB',
        'grocery_country_iso3': 'RUS',
        'region_id': region_id,
        'order_id': order.order_id,
        'payment_tech_type': payment_method_type,
        'payment_method_id': payment_method_id,
        'x_remote_ip': headers.USER_IP,
        'x_request_language': 'ru',
        'yandex_uid': order.yandex_uid,
        'x_yataxi_user': headers.USER_INFO,
        'x_yataxi_user_id': X_YATAXI_USER_ID,
        'x_login_id': X_LOGIN_ID,
        'personal_phone_id': headers.PERSONAL_PHONE_ID,
        'x_request_application': headers.APP_INFO,
        'x_yataxi_session': headers.DEFAULT_SESSION,
        'billing_settings_version': BILLING_SETTINGS_VERSION,
    }


@HELPING_HAND
async def test_finish_closed_order_confirms_charity(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, stq,
):
    order = models.Order(
        pgsql=pgsql,
        status='closed',
        state=models.OrderState(close_money_status='success'),
    )
    _setup_headers(pgsql, order.order_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={'order_id': order.order_id, 'payload': {}},
    )
    assert response.status_code == 200

    assert stq.persey_payments_grocery_order_delivered.times_called == 1
    args = stq.persey_payments_grocery_order_delivered.next_call()

    assert args['id'] == order.order_id
    args['kwargs'].pop('log_extra')
    assert args['kwargs'] == {
        'grocery_country_iso3': 'RUS',
        'order_id': order.order_id,
        'x_remote_ip': headers.USER_IP,
        'yandex_uid': order.yandex_uid,
        'x_login_id': X_LOGIN_ID,
        'personal_phone_id': headers.PERSONAL_PHONE_ID,
        'x_yataxi_session': headers.DEFAULT_SESSION,
        'x_yataxi_user_id': X_YATAXI_USER_ID,
    }


@HELPING_HAND
async def test_finish_cancelled_order_cancels_charity(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, stq,
):
    order = models.Order(
        pgsql=pgsql,
        status='canceled',
        state=models.OrderState(close_money_status='success'),
        billing_settings_version=BILLING_SETTINGS_VERSION,
    )
    _setup_headers(pgsql, order.order_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={'order_id': order.order_id, 'payload': {}},
    )
    assert response.status_code == 200

    assert stq.persey_payments_grocery_order_cancelled.times_called == 1
    args = stq.persey_payments_grocery_order_cancelled.next_call()

    assert args['id'] == order.order_id
    args['kwargs'].pop('log_extra')
    assert args['kwargs'] == {
        'grocery_country_iso3': 'RUS',
        'order_id': order.order_id,
        'x_remote_ip': headers.USER_IP,
        'yandex_uid': order.yandex_uid,
        'x_login_id': X_LOGIN_ID,
        'personal_phone_id': headers.PERSONAL_PHONE_ID,
        'x_yataxi_session': headers.DEFAULT_SESSION,
        'x_yataxi_user_id': X_YATAXI_USER_ID,
        'billing_settings_version': BILLING_SETTINGS_VERSION,
    }


def _setup_headers(pgsql, order_id):
    auth_headers = copy.deepcopy(headers.DEFAULT_HEADERS)
    auth_headers['X-Remote-IP'] = headers.USER_IP
    auth_headers['X-YaTaxi-UserId'] = X_YATAXI_USER_ID
    auth_headers['X-Login-Id'] = X_LOGIN_ID
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order_id,
        raw_auth_context=json.dumps({'headers': auth_headers}),
    )


def _get_last_processing_events(
        processing, order, count=1, queue='processing_non_critical',
):
    return helpers.get_last_processing_payloads(
        processing, order.order_id, count=count, queue=queue,
    )
