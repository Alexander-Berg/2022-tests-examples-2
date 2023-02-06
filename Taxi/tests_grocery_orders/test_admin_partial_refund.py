import json

import pytest

from . import headers
from . import models
from . import order_log
from . import processing_noncrit


def _get_cart_items():
    return [
        models.GroceryCartItem(item_id='item_id_1', price='100', quantity='3'),
        models.GroceryCartItem(item_id='item_id_2', price='200', quantity='2'),
        models.GroceryCartItem(item_id='item_id_3', price='300', quantity='1'),
    ]


REFUND_INFO = [
    (
        {'item_id_2': '1'},
        {'item_id_2': '1'},
        [
            {
                'item_id': 'item_id_1',
                'quantity': '3',
                'total_price': '300',
                'price': '100',
            },
            {
                'item_id': 'item_id_2',
                'quantity': '1',
                'total_price': '200',
                'price': '200',
            },
            {
                'item_id': 'item_id_3',
                'quantity': '1',
                'total_price': '300',
                'price': '300',
            },
        ],
    ),
    (
        {'item_id_2': '2'},
        {'item_id_2': '1'},
        [
            {
                'item_id': 'item_id_1',
                'quantity': '3',
                'total_price': '300',
                'price': '100',
            },
            {
                'item_id': 'item_id_2',
                'quantity': '0',
                'total_price': '0',
                'price': '200',
            },
            {
                'item_id': 'item_id_3',
                'quantity': '1',
                'total_price': '300',
                'price': '300',
            },
        ],
    ),
    (
        {'item_id_2': '2'},
        {'item_id_2': '0'},
        [
            {
                'item_id': 'item_id_1',
                'quantity': '3',
                'total_price': '300',
                'price': '100',
            },
            {
                'item_id': 'item_id_2',
                'quantity': '0',
                'total_price': '0',
                'price': '200',
            },
            {
                'item_id': 'item_id_3',
                'quantity': '1',
                'total_price': '300',
                'price': '300',
            },
        ],
    ),
    (
        {'item_id_3': '1'},
        {'item_id_2': '1'},
        [
            {
                'item_id': 'item_id_1',
                'quantity': '3',
                'total_price': '300',
                'price': '100',
            },
            {
                'item_id': 'item_id_2',
                'quantity': '1',
                'total_price': '200',
                'price': '200',
            },
            {
                'item_id': 'item_id_3',
                'quantity': '0',
                'total_price': '0',
                'price': '300',
            },
        ],
    ),
    (
        {'item_id_2': '1'},
        {'item_id_1': '1'},
        [
            {
                'item_id': 'item_id_1',
                'quantity': '2',
                'total_price': '200',
                'price': '100',
            },
            {
                'item_id': 'item_id_2',
                'quantity': '1',
                'total_price': '200',
                'price': '200',
            },
            {
                'item_id': 'item_id_3',
                'quantity': '1',
                'total_price': '300',
                'price': '300',
            },
        ],
    ),
    (
        {'item_id_3': '1'},
        {'item_id_2': '2', 'item_id_1': '3'},
        [
            {
                'item_id': 'item_id_1',
                'quantity': '0',
                'total_price': '0',
                'price': '100',
            },
            {
                'item_id': 'item_id_2',
                'quantity': '0',
                'total_price': '0',
                'price': '200',
            },
            {
                'item_id': 'item_id_3',
                'quantity': '0',
                'total_price': '0',
                'price': '300',
            },
        ],
    ),
]

COMPENSATION_ID = 'a2ace908-5d18-4764-8593-192a1b535514'


def _setup_order_and_cart(
        pgsql,
        grocery_cart,
        grocery_depots,
        transactions_eda,
        items,
        status='closed',
        hold_money_status='success',
        clear_money_status='success',
        grocery_flow='grocery_flow_v1',
        add_payment_method=True,
        country_iso3=models.Country.Russia.country_iso3,
        billing_settings_version=None,
):
    order = models.Order(
        pgsql=pgsql,
        status=status,
        state=models.OrderState(
            hold_money_status=hold_money_status,
            close_money_status=clear_money_status,
        ),
        grocery_flow_version=grocery_flow,
        billing_settings_version=billing_settings_version,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    if add_payment_method:
        grocery_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )
    grocery_cart.set_items(items=items)
    transactions_eda.set_items(items=items)

    grocery_cart.set_order_conditions(delivery_cost='500')

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, country_iso3=country_iso3,
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    return order


def _check_expected_history(order, history_status):
    order.check_order_history(
        'admin_action',
        {
            'to_action_type': 'partial_refund',
            'status': history_status,
            'admin_info': {},
        },
    )


GROCERY_FLOWS = pytest.mark.parametrize(
    'grocery_flow', ['grocery_flow_v1', 'grocery_flow_v3'],
)


@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.parametrize(
    'handler',
    [
        '/admin/orders/v1/money/partial-refund',
        '/processing/v1/compensation/partial-refund',
    ],
)
@pytest.mark.parametrize(
    'status',
    ['delivering', 'delivering', 'delivering', 'assembled', 'closed'],
)
@GROCERY_FLOWS
@pytest.mark.parametrize('add_payment_method_in_cart', [True, False])
@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_payments,
        transactions_eda,
        transactions_lavka_isr,
        grocery_depots,
        handler,
        status,
        grocery_flow,
        add_payment_method_in_cart,
        country,
        processing,
):
    items = _get_cart_items()
    order = _setup_order_and_cart(
        pgsql,
        grocery_cart,
        grocery_depots,
        transactions_eda,
        items=items,
        status=status,
        grocery_flow=grocery_flow,
        add_payment_method=add_payment_method_in_cart,
        country_iso3=country.country_iso3,
    )

    items_refund_request = [{'item_id': 'item_id_2', 'refund_quantity': '1'}]

    request_json = {'order_id': order.order_id, 'items': items_refund_request}
    if handler == '/processing/v1/compensation/partial-refund':
        request_json['compensation_id'] = COMPENSATION_ID

    response = await taxi_grocery_orders.post(
        handler, json=request_json, headers=headers.HEADER_APP_INFO_YANGO,
    )

    assert response.status_code == 200
    assert grocery_payments.times_remove_called() == 1
    assert grocery_cart.refund_times_called() == 1

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 2
    event = events[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['reason'] == 'order_edited'
    order_log.check_order_log_payload(
        event.payload, order, cart_items=items, depot=None,
    )

    event = events[1]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['reason'] == 'order_notification'
    assert event.payload['code'] == 'compensation'

    compensation_id = None
    if handler == '/processing/v1/compensation/partial-refund':
        compensation_id = COMPENSATION_ID
    order.update()
    order.check_payment_operation(
        (
            order.order_id,
            'refund-123',
            'remove',
            'requested',
            [
                {
                    'item_id': 'item_id_2_0',
                    'item_type': 'product',
                    'quantity': '1',
                },
            ],
            None,
            compensation_id,
        ),
    )


@pytest.mark.parametrize(
    'handler',
    [
        '/admin/orders/v1/money/partial-refund',
        '/processing/v1/compensation/partial-refund',
    ],
)
@pytest.mark.parametrize(
    'status, clear_money_status, expected_result, expected_code',
    [
        ('assembling', None, 'fail', 405),
        ('assembled', None, 'success', 200),
        ('closed', None, 'success', 200),
        ('closed', 'success', 'success', 200),
        ('canceled', None, 'fail', 405),
        ('canceled', 'success', 'fail', 405),
    ],
)
async def test_partial_refund_remove_items(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        transactions_eda,
        grocery_payments,
        handler,
        status,
        clear_money_status,
        expected_result,
        expected_code,
):
    items = _get_cart_items()
    order = _setup_order_and_cart(
        pgsql,
        grocery_cart,
        grocery_depots,
        transactions_eda,
        items=items,
        status=status,
        clear_money_status=clear_money_status,
    )

    request_json = {
        'order_id': order.order_id,
        'items': [{'item_id': items[0].item_id, 'refund_quantity': '1'}],
    }
    if handler == '/processing/v1/compensation/partial-refund':
        request_json['compensation_id'] = COMPENSATION_ID

    response = await taxi_grocery_orders.post(handler, json=request_json)
    assert response.status_code == expected_code
    order.update()

    _check_expected_history(order, expected_result)
    if expected_result == 'success' and clear_money_status == 'success':
        assert grocery_payments.times_remove_called() == 1


@pytest.mark.parametrize(
    'response_code, threshold, refund_sum, is_expensive_order',
    [
        (400, 5000, 4000, True),
        (400, 5000, 5000, False),
        (200, None, 4000, True),
        (200, None, 5000, False),
        (200, 5000, 4000, False),
        (200, 5000, 5000, True),
    ],
)
async def test_dynamic_permission(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        taxi_config,
        response_code,
        threshold,
        refund_sum,
        is_expensive_order,
):
    threshold_config_name = 'GROCERY_ORDERS_PERMISSION_SETTINGS'
    threshold_config = taxi_config.get(threshold_config_name)
    threshold_config['expensive_order_threshold_rus'] = threshold
    taxi_config.set_values({threshold_config_name: threshold_config})

    order = models.Order(pgsql=pgsql, status='closed')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    items = [
        models.GroceryCartItemV2(
            item_id='item-id-1',
            sub_items=[
                models.GroceryCartSubItem(
                    item_id='item-id-1_0',
                    full_price=str(refund_sum * 2),
                    price=str(refund_sum),
                    quantity='2',
                ),
            ],
        ),
    ]
    grocery_cart.set_items_v2(items=items)
    request_json = {
        'order_id': order.order_id,
        'items': [{'item_id': items[0].item_id, 'refund_quantity': '1'}],
        'is_expensive_order': is_expensive_order,
    }
    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/money/partial-refund',
        json=request_json,
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == response_code
