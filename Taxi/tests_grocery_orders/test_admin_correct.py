import pytest

from . import configs
from . import models

CORRECTING_ENABLED_BY_CARD = pytest.mark.experiments3(
    name='grocery_admin_correct_order',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {
                'init': {
                    'value': 'card',
                    'arg_name': 'payment_method_type',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {'enabled': True, 'addition_enabled': True},
        },
    ],
    is_config=True,
)


@configs.CORRECTING_ENABLED
@pytest.mark.parametrize('correcting_type', [None, 'remove', 'add'])
@pytest.mark.parametrize('do_set_wms_pause', [False, True])
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        grocery_wms_gateway,
        correcting_type,
        do_set_wms_pause,
):
    state = models.OrderState(hold_money_status='success')
    order = models.Order(pgsql=pgsql, status='assembling', state=state)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_items(
        [
            models.GroceryCartItem(item_id='item_id_1', quantity='2'),
            models.GroceryCartItem(item_id='item_id_2', quantity='3'),
        ],
    )

    correcting_items = [
        {'item_id': 'item_id_1', 'new_quantity': '0', 'old_quantity': '2'},
        {'item_id': 'item_id_2', 'new_quantity': '2', 'old_quantity': '3'},
    ]

    if correcting_type == 'add':
        correcting_items = [
            {'item_id': 'item_id_1', 'new_quantity': '4', 'old_quantity': '2'},
            {'item_id': 'item_id_2', 'new_quantity': '4', 'old_quantity': '3'},
            {'item_id': 'item_id_3', 'new_quantity': '4', 'old_quantity': '0'},
        ]

    request = {
        'order_id': order.order_id,
        'correcting_items': correcting_items,
        'set_wms_pause': do_set_wms_pause,
    }

    if correcting_type is not None:
        request['correcting_type'] = correcting_type

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/correct', json=request,
    )

    order.update()

    assert response.status == 202

    assert order.edit_status == 'in_progress'

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    event = events[0]

    expected_payload = {
        'order_id': order.order_id,
        'reason': 'correct',
        'correcting_items': correcting_items,
        'correcting_order_revision': order.order_revision,
        'flow_version': order.grocery_flow_version,
        'correcting_cart_version': order.cart_version,
        'correcting_type': 'remove',
        'correcting_source': 'admin',
    }

    if correcting_type == 'add':
        expected_payload['correcting_type'] = 'add'

    assert event.payload == expected_payload

    order.check_order_history(
        'admin_action',
        {'to_action_type': 'correct', 'status': 'success', 'admin_info': {}},
    )

    logged_correcting_items = [
        {'item_id': 'item_id_1', 'quantity': '2'},
        {'item_id': 'item_id_2', 'quantity': '1'},
    ]

    if correcting_type == 'add':
        logged_correcting_items.append(
            {'item_id': 'item_id_3', 'quantity': '4'},
        )

    if correcting_type is not None:
        order.check_order_history(
            'order_correcting_status',
            {
                'to_order_correcting': 'correcting_started',
                'correcting_result': 'success',
                'correcting_items': logged_correcting_items,
                'correcting_type': correcting_type,
            },
        )
    else:
        order.check_order_history(
            'order_correcting_status',
            {
                'to_order_correcting': 'correcting_started',
                'correcting_result': 'success',
                'correcting_items': logged_correcting_items,
                'correcting_type': 'remove',
            },
        )

    order.check_order_history(
        'state_change', {'to': {'edit_status': 'in_progress'}},
    )

    if do_set_wms_pause:
        order.check_order_history(
            'wms_pause', {'type': 'pause', 'delay': '30'},
        )
        assert grocery_wms_gateway.times_set_pause_called() == 1


@CORRECTING_ENABLED_BY_CARD
async def test_addition_card_only(
        taxi_grocery_orders, pgsql, grocery_cart, processing, grocery_depots,
):
    state = models.OrderState(hold_money_status='success')
    order = models.Order(pgsql=pgsql, status='assembling', state=state)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_items(
        [
            models.GroceryCartItem(item_id='item_id_1', quantity='2'),
            models.GroceryCartItem(item_id='item_id_2', quantity='3'),
        ],
    )

    correcting_items = [
        {'item_id': 'item_id_1', 'new_quantity': '4'},
        {'item_id': 'item_id_2', 'new_quantity': '4'},
        {'item_id': 'item_id_3', 'new_quantity': '4'},
    ]

    request = {
        'order_id': order.order_id,
        'correcting_items': correcting_items,
        'correcting_type': 'add',
    }

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/correct', json=request,
    )

    order.update()

    assert response.status == 202


@configs.CORRECTING_ENABLED
@pytest.mark.parametrize('correcting_type', [None, 'remove', 'add'])
async def test_bad_revision(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        correcting_type,
):
    state = models.OrderState(hold_money_status='success')
    order = models.Order(
        pgsql=pgsql, status='assembling', order_revision=1, state=state,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(
        [
            models.GroceryCartItem(item_id='item_id_1', quantity='2'),
            models.GroceryCartItem(item_id='item_id_2', quantity='3'),
        ],
    )

    correcting_items = [
        {'item_id': 'item_id_1', 'new_quantity': '0'},
        {'item_id': 'item_id_2', 'new_quantity': '2'},
    ]

    request = {
        'order_id': order.order_id,
        'correcting_items': correcting_items,
        'order_revision': 0,
    }

    if correcting_type is not None:
        request['correcting_type'] = correcting_type

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/correct', json=request,
    )

    assert response.status == 409


@configs.CORRECTING_ENABLED
async def test_money_status_failed(
        taxi_grocery_orders, pgsql, grocery_cart, processing, grocery_depots,
):
    state = models.OrderState(hold_money_status='failed')
    order = models.Order(
        pgsql=pgsql, status='assembling', order_revision=0, state=state,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(
        [
            models.GroceryCartItem(item_id='item_id_1', quantity='2'),
            models.GroceryCartItem(item_id='item_id_2', quantity='3'),
        ],
    )

    correcting_items = [
        {'item_id': 'item_id_1', 'new_quantity': '0'},
        {'item_id': 'item_id_2', 'new_quantity': '2'},
    ]

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/correct',
        json={
            'order_id': order.order_id,
            'correcting_items': correcting_items,
            'order_revision': 0,
        },
    )

    assert response.status == 409


@configs.CORRECTING_ENABLED
@pytest.mark.parametrize('edit_status', ['in_progress', 'success', 'failed'])
async def test_other_edit_in_progress(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        edit_status,
):
    order = models.Order(
        pgsql=pgsql,
        status='assembling',
        order_revision=0,
        edit_status=edit_status,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(
        [
            models.GroceryCartItem(item_id='item_id_1', quantity='2'),
            models.GroceryCartItem(item_id='item_id_2', quantity='3'),
        ],
    )

    correcting_items = [
        {'item_id': 'item_id_1', 'new_quantity': '0'},
        {'item_id': 'item_id_2', 'new_quantity': '2'},
    ]

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/correct',
        json={
            'order_id': order.order_id,
            'correcting_items': correcting_items,
            'order_revision': 0,
        },
    )

    assert response.status == 409


@configs.CORRECTING_ENABLED
@pytest.mark.parametrize(
    'item_id_1_quantity,item_id_2_quantity,item_id_3_quantity',
    [
        ('0', '0', None),
        ('3', '0', None),
        ('4', '0', None),
        ('2', '3', None),
        ('1', '2', '2'),
    ],
)
async def test_bad_quantity(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        item_id_1_quantity,
        item_id_2_quantity,
        item_id_3_quantity,
):
    state = models.OrderState(hold_money_status='success')
    order = models.Order(pgsql=pgsql, status='assembling', state=state)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(
        [
            models.GroceryCartItem(item_id='item_id_1', quantity='2'),
            models.GroceryCartItem(item_id='item_id_2', quantity='3'),
        ],
    )

    correcting_items = [
        {'item_id': 'item_id_1', 'new_quantity': item_id_1_quantity},
        {'item_id': 'item_id_2', 'new_quantity': item_id_2_quantity},
    ]

    if item_id_3_quantity is not None:
        correcting_items.append(
            {'item_id': 'item_id_3', 'new_quantity': item_id_3_quantity},
        )

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/correct',
        json={
            'order_id': order.order_id,
            'correcting_items': correcting_items,
        },
    )

    assert response.status == 400

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events
    order.check_order_history(
        'admin_action',
        {'to_action_type': 'correct', 'status': 'fail', 'admin_info': {}},
    )
    order.check_order_history(
        'order_correcting_status',
        {
            'to_order_correcting': 'correcting_started',
            'correcting_result': 'fail',
            'correcting_type': 'remove',
        },
    )
    order.check_order_history(
        'state_change', {'to': {'edit_status': 'failed'}},
    )


@configs.CORRECTING_ENABLED
@pytest.mark.parametrize(
    'order_status,code,correcting_type',
    [
        ('checked_out', 202, 'remove'),
        ('reserved', 202, 'remove'),
        ('assembling', 202, 'remove'),
        ('assembled', 409, 'remove'),
        ('delivering', 202, 'remove'),
        ('pending_cancel', 202, 'remove'),
        ('closed', 202, 'remove'),
        ('checked_out', 202, 'add'),
        ('reserved', 202, 'add'),
        ('assembling', 202, 'add'),
        ('assembled', 409, 'add'),
        ('delivering', 409, 'add'),
        ('pending_cancel', 409, 'add'),
        ('closed', 409, 'add'),
    ],
)
async def test_order_status(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        order_status,
        correcting_type,
        code,
):
    state = models.OrderState(hold_money_status='success')
    order = models.Order(pgsql=pgsql, status=order_status, state=state)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(
        [
            models.GroceryCartItem(item_id='item_id_1', quantity='2'),
            models.GroceryCartItem(item_id='item_id_2', quantity='3'),
        ],
    )

    if correcting_type == 'remove':
        correcting_items = [
            {'item_id': 'item_id_1', 'new_quantity': '0', 'old_quantity': '2'},
            {'item_id': 'item_id_2', 'new_quantity': '2', 'old_quantity': '3'},
        ]
    elif correcting_type == 'add':
        correcting_items = [
            {'item_id': 'item_id_1', 'new_quantity': '3', 'old_quantity': '2'},
            {'item_id': 'item_id_2', 'new_quantity': '4', 'old_quantity': '3'},
        ]

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/correct',
        json={
            'order_id': order.order_id,
            'correcting_items': correcting_items,
            'correcting_type': correcting_type,
        },
    )

    assert response.status == code

    if code == 202:
        events = list(processing.events(scope='grocery', queue='processing'))
        assert len(events) == 1

        event = events[0]

        assert event.payload['order_id'] == order.order_id
        if order_status == 'closed':
            assert event.payload['reason'] == 'correct_refund'
        else:
            assert event.payload['reason'] == 'correct'
        assert event.payload['correcting_items'] == correcting_items
        assert (
            event.payload['correcting_order_revision'] == order.order_revision
        )
        order.check_order_history(
            'admin_action',
            {
                'to_action_type': 'correct',
                'status': 'success',
                'admin_info': {},
            },
        )
        if correcting_type == 'remove':
            order.check_order_history(
                'order_correcting_status',
                {
                    'to_order_correcting': 'correcting_started',
                    'correcting_result': 'success',
                    'correcting_items': [
                        {'item_id': 'item_id_1', 'quantity': '2'},
                        {'item_id': 'item_id_2', 'quantity': '1'},
                    ],
                    'correcting_type': 'remove',
                },
            )
        elif correcting_type == 'add':
            order.check_order_history(
                'order_correcting_status',
                {
                    'to_order_correcting': 'correcting_started',
                    'correcting_result': 'success',
                    'correcting_items': [
                        {'item_id': 'item_id_1', 'quantity': '1'},
                        {'item_id': 'item_id_2', 'quantity': '1'},
                    ],
                    'correcting_type': 'add',
                },
            )

        order.check_order_history(
            'state_change', {'to': {'edit_status': 'in_progress'}},
        )
    else:
        events = list(processing.events(scope='grocery', queue='processing'))
        assert not events
        order.check_order_history(
            'admin_action',
            {'to_action_type': 'correct', 'status': 'fail', 'admin_info': {}},
        )
        if correcting_type == 'remove':
            order.check_order_history(
                'order_correcting_status',
                {
                    'to_order_correcting': 'correcting_started',
                    'correcting_result': 'fail',
                    'correcting_items': [
                        {'item_id': 'item_id_1', 'quantity': '2'},
                        {'item_id': 'item_id_2', 'quantity': '1'},
                    ],
                    'correcting_type': 'remove',
                },
            )
        elif correcting_type == 'add':
            order.check_order_history(
                'order_correcting_status',
                {
                    'to_order_correcting': 'correcting_started',
                    'correcting_result': 'fail',
                    'correcting_items': [
                        {'item_id': 'item_id_1', 'quantity': '1'},
                        {'item_id': 'item_id_2', 'quantity': '1'},
                    ],
                    'correcting_type': 'add',
                },
            )

        order.check_order_history(
            'state_change', {'to': {'edit_status': 'failed'}},
        )


@configs.CORRECTING_ENABLED
async def test_wms_pause_409(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_wms_gateway,
):
    order = models.Order(pgsql=pgsql, status='assembling', order_revision=0)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(
        [
            models.GroceryCartItem(item_id='item_id_1', quantity='2'),
            models.GroceryCartItem(item_id='item_id_2', quantity='3'),
        ],
    )
    grocery_wms_gateway.set_http_resp(
        '{"code": "WMS_409", "message": "Not allowed"}', 409,
    )

    correcting_items = [
        {'item_id': 'item_id_1', 'new_quantity': '0'},
        {'item_id': 'item_id_2', 'new_quantity': '2'},
    ]

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/correct',
        json={
            'order_id': order.order_id,
            'correcting_items': correcting_items,
            'order_revision': 0,
            'set_wms_pause': True,
        },
    )
    assert response.status == 202
