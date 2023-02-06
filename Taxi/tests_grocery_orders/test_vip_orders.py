import copy

import pytest

from . import admin_orders_suggest_consts
from . import consts
from . import experiments
from . import headers
from . import models
from . import order_v2_submit_consts as submit_consts
from . import processing_noncrit


async def _get_order(taxi_grocery_orders, order_id, header=None):
    header['X-Remote-IP'] = '172.99.23.44'
    request_json = {'order_id': order_id}
    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/suggest', json=request_json, headers=header,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == 1
    return orders[0]


@pytest.mark.experiments3(
    name='grocery_orders_vip_options',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'By user tag and newbie or newbie_fraud',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'user_tags',
                                'set_elem_type': 'string',
                                'value': 'ultima',
                            },
                            'type': 'contains',
                        },
                        {
                            'type': 'any_of',
                            'init': {
                                'predicates': [
                                    {
                                        'init': {
                                            'arg_name': 'newbie_check_result',
                                            'arg_type': 'string',
                                            'value': 'newbie',
                                        },
                                        'type': 'eq',
                                    },
                                    {
                                        'init': {
                                            'arg_name': 'newbie_check_result',
                                            'arg_type': 'string',
                                            'value': 'newbie_fraud',
                                        },
                                        'type': 'eq',
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
            'value': {'vip_type': consts.OTHER_VIP_TYPE},
        },
        {
            'title': 'By personal_phone_id',
            'predicate': {
                'init': {
                    'arg_name': 'personal_phone_id',
                    'arg_type': 'string',
                    'value': headers.PERSONAL_PHONE_ID,
                },
                'type': 'eq',
            },
            'value': {'vip_type': consts.VIP_TYPE},
        },
    ],
    is_config=True,
)
@experiments.antifraud_check_experiment(True)
@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.parametrize(
    'personal_phone_id, user_tag, newbie_check_result',
    [
        (headers.PERSONAL_PHONE_ID, None, 'newbie'),
        (headers.OTHER_PERSONAL_PHONE_ID, 'usual_user', 'regular_user'),
        (headers.OTHER_PERSONAL_PHONE_ID, 'ultima', 'newbie'),
        (headers.OTHER_PERSONAL_PHONE_ID, 'ultima', 'newbie_fraud'),
    ],
)
async def test_v2_submit(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        grocery_tags,
        passport,
        antifraud,
        grocery_marketing,
        grocery_user_profiles,
        personal_phone_id,
        user_tag,
        newbie_check_result,
):
    grocery_tags.add_tag(personal_phone_id=personal_phone_id, tag=user_tag)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_depot_id(depot_id=submit_consts.DEPOT_ID)
    grocery_depots.add_depot(legacy_depot_id=submit_consts.DEPOT_ID)
    await taxi_grocery_orders.invalidate_caches()

    delivery_type = 'courier'
    grocery_cart.set_delivery_type(delivery_type)

    antifraud.set_is_fraud(newbie_check_result == 'newbie_fraud')
    total_orders_count = 0 if newbie_check_result != 'regular_user' else 5
    grocery_marketing.add_user_tag(
        'total_orders_count', total_orders_count, user_id=headers.YANDEX_UID,
    )
    grocery_user_profiles.set_is_fraud(False)

    if personal_phone_id == headers.PERSONAL_PHONE_ID:
        request_headers = headers.DEFAULT_HEADERS
    else:
        request_headers = copy.deepcopy(headers.DEFAULT_HEADERS)
        request_headers['X-YaTaxi-User'] = headers.OTHER_USER_INFO
    # Create order ------------------------------------------------------------
    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/submit',
        json=submit_consts.SUBMIT_BODY,
        headers=request_headers,
    )

    assert response.status_code == 200
    order_id = response.json()['order_id']

    order = models.Order(pgsql=pgsql, order_id=order_id, insert_in_pg=False)
    order.update()

    assert order.order_version == 0
    assert order.status == 'checked_out'
    assert order.cart_id == submit_consts.CART_ID

    assert grocery_cart.checkout_times_called() == 1
    grocery_cart.flush_all()

    if personal_phone_id == headers.PERSONAL_PHONE_ID:
        assert order.vip_type == consts.VIP_TYPE
    elif user_tag == 'ultima':
        assert order.vip_type == consts.OTHER_VIP_TYPE
    else:
        assert order.vip_type is None

    # Check g-support ---------------------------------------------------------
    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )
    response = await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers=request_headers,
    )

    assert grocery_cart.set_order_id_times_called() == 0
    order.update()

    assert response.status_code == 200

    state_change_event = processing_noncrit.check_noncrit_event(
        processing, order.order_id, 'status_change',
    )
    assert state_change_event is not None
    if personal_phone_id == headers.PERSONAL_PHONE_ID:
        assert (
            state_change_event['order_log_info']['vip_type'] == consts.VIP_TYPE
        )
    elif user_tag == 'ultima':
        assert (
            state_change_event['order_log_info']['vip_type']
            == consts.OTHER_VIP_TYPE
        )
    else:
        assert 'vip_type' not in state_change_event['order_log_info']

    # Check suggest -----------------------------------------------------------
    specific_order = await _get_order(
        taxi_grocery_orders,
        order.order_id,
        header=admin_orders_suggest_consts.HEADER,
    )
    assert state_change_event is not None
    if personal_phone_id == headers.PERSONAL_PHONE_ID:
        assert specific_order['vip_type'] == consts.VIP_TYPE
    elif user_tag == 'ultima':
        assert specific_order['vip_type'] == consts.OTHER_VIP_TYPE
    else:
        assert 'vip_type' not in specific_order
