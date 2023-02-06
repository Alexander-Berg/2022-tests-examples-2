import json

from tests_grocery_uber_gw import models

SOME_UUID = '01234567-89ab-cdef-0123-456789abcdef'


async def test_orders_created_metrics(
        taxi_grocery_uber_gw,
        mock_uber_api,
        grocery_depots,
        mockserver,
        taxi_grocery_uber_gw_monitor,
):
    """ Checking correctness of collection of OrdersCreated metrics """

    uber_order_id = SOME_UUID
    uber_store_id = 'uber_store_id'
    depot_id = 'deli_id'
    eater_phone = '+01 2345 678901'
    eater_phone_code = '012 34 567'
    personal_phone_id = 'some_personal_phone_id'
    cart_id = SOME_UUID
    items = [
        {
            'id': 'item_id',
            'quantity': 1,
            'price': {'unit_price': {'amount': 1, 'currency_code': 'GBP'}},
        },
    ]

    store = models.Store(store_id=uber_store_id, merchant_store_id=depot_id)
    order = models.Order(
        order_id=uber_order_id,
        store_id=uber_store_id,
        items=items,
        eater_phone=eater_phone,
        eater_phone_code=eater_phone_code,
        store_external_reference_id=depot_id,
    )
    mock_uber_api_payload = {
        'stores': {store.store_id: store},
        'orders': {order.order_id: order},
    }
    mock_uber_api.set_payload(mock_uber_api_payload)

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    @mockserver.json_handler('personal/v1/phones/store')
    def _phones_store(request):
        return {'value': request.json['value'], 'id': personal_phone_id}

    @mockserver.json_handler('grocery-cart/internal/v1/cart/create')
    def _cart_create():
        return {'cart_id': cart_id, 'cart_version': 1}

    @mockserver.json_handler(
        'grocery-orders/orders/v1/integration-api/v1/submit',
    )
    def _orders_submit():
        return {'order_id': uber_order_id}

    request = {
        'event_type': 'orders.notification',
        'event_id': SOME_UUID,
        'event_time': 1234567890,
        'meta': {
            'resource_id': uber_order_id,
            'status': 'pos',
            'user_id': SOME_UUID,
        },
        'resource_href': f'https://api.uber.com/v2/eats/order/{uber_order_id}',
    }
    response = await taxi_grocery_uber_gw.post(
        'processing/v1/uber-gw/v1/order/create',
        data=json.dumps(request),
        headers={'content-type': 'application/json'},
    )
    assert response.status_code == 200

    metrics = await taxi_grocery_uber_gw_monitor.get_metrics(
        'grocery_uber_gw_orders_created',
    )
    assert metrics['grocery_uber_gw_orders_created_city']['Moscow'] == 1
    assert metrics['grocery_uber_gw_orders_created_country']['Russia'] == 1


async def test_orders_canceled_metrics(
        taxi_grocery_uber_gw,
        mock_uber_api,
        grocery_depots,
        grocery_uber_gw_db,
        mockserver,
        taxi_grocery_uber_gw_monitor,
):
    """ Checking correctness of collection of OrdersCanceled metrics """

    uber_order_id = SOME_UUID
    uber_store_id = 'uber_store_id'
    depot_id = 'deli_id'

    store = models.Store(store_id=uber_store_id, merchant_store_id=depot_id)
    order = models.Order(
        order_id=uber_order_id,
        store_id=uber_store_id,
        store_external_reference_id=depot_id,
    )
    mock_uber_api_payload = {
        'stores': {store.store_id: store},
        'orders': {order.order_id: order},
    }
    mock_uber_api.set_payload(mock_uber_api_payload)

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    @mockserver.json_handler(
        'grocery-orders/orders/v1/integration-api/v1/actions/cancel',
    )
    def _orders_cancel():
        return mockserver.make_response(status=202)

    request = {
        'event_type': 'orders.cancel',
        'event_id': SOME_UUID,
        'event_time': 1234567890,
        'meta': {
            'resource_id': uber_order_id,
            'status': 'pos',
            'user_id': SOME_UUID,
        },
        'resource_href': f'https://api.uber.com/v2/eats/order/{uber_order_id}',
    }
    response = await taxi_grocery_uber_gw.post(
        'processing/v1/uber-gw/v1/order/cancel',
        data=json.dumps(request),
        headers={'content-type': 'application/json'},
    )
    assert response.status_code == 200

    metrics = await taxi_grocery_uber_gw_monitor.get_metrics(
        'grocery_uber_gw_orders_canceled',
    )
    assert metrics['grocery_uber_gw_orders_canceled_city']['Moscow'] == 1
    assert metrics['grocery_uber_gw_orders_canceled_country']['Russia'] == 1
