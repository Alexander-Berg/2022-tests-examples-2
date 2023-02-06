import copy
import json

import pytest

from tests_grocery_uber_gw import models
from tests_grocery_uber_gw import sql_queries

REQUEST_DATA = {
    'event_type': 'orders.cancel',
    'event_id': 'c4d2261e-2779-4eb6-beb0-cb41235c751e',
    'event_time': 1427343990,
    'meta': {
        'resource_id': '153dd7f1-339d-4619-940c-418943c14636',
        'status': 'pos',
        'user_id': '89dd9741-66b5-4bb4-b216-a813f3b21b4f',
    },
    'resource_href': (
        'https://api.uber.com/v2/eats/order/'
        '153dd7f1-339d-4619-940c-418943c14636'
    ),
}


@pytest.mark.parametrize('use_cache', [True, False])
async def test_order_canceled_by_uber_200(
        taxi_grocery_uber_gw,
        mock_uber_api,
        mockserver,
        grocery_uber_gw_db,
        use_cache,
):
    """ Checks happy path: Recieve a request to remove the order, get grocery_id
    of the order from Uber or cache, then call g-orders to cancel
    and return 200 on success """

    uber_order_id = '73ef6892-11c0-4bb4-b216-f827a3c21f8b'
    grocery_order_id = '95f8a691-8b1b-4279-b7f6-4a4dc6d0016f'
    order = models.Order(
        order_id=uber_order_id, external_reference_id=grocery_order_id,
    )
    request = copy.deepcopy(REQUEST_DATA)
    request['meta']['resource_id'] = order.order_id

    mock_uber_api_payload = {'orders': {order.order_id: order}}
    mock_uber_api.set_payload(mock_uber_api_payload)

    if use_cache:
        grocery_uber_gw_db.apply_sql_query(
            sql_queries.insert_order(
                uber_order_id, grocery_order_id, None, 'depot_id',
            ),
        )
        await taxi_grocery_uber_gw.invalidate_caches()

    @mockserver.json_handler(
        'grocery-orders/orders/v1/integration-api/v1/actions/cancel',
    )
    def _orders_cancel(request):
        assert request.json['order_id'] == grocery_order_id
        return mockserver.make_response(status=202)

    response = await taxi_grocery_uber_gw.post(
        'processing/v1/uber-gw/v1/order/cancel',
        data=json.dumps(request),
        headers={'content-type': 'application/json'},
    )
    assert mock_uber_api.get_order_details_times_called == (
        0 if use_cache else 1
    )
    assert response.status_code == 200


@pytest.mark.parametrize('reason', ['uber_error', 'g_orders_error'])
async def test_order_canceled_by_uber_500(
        taxi_grocery_uber_gw, mock_uber_api, mockserver, reason,
):
    """ Return 500 regardless of whether Uber or grocery-orders fail """

    order_id = '73ef6892-11c0-4bb4-b216-f827a3c21f8b'
    order = models.Order(order_id=order_id)
    request = copy.deepcopy(REQUEST_DATA)
    if reason != 'uber_error':
        request['meta']['resource_id'] = order.order_id

    mock_uber_api_payload = {'orders': {order.order_id: order}}
    mock_uber_api.set_payload(mock_uber_api_payload)

    @mockserver.json_handler(
        'grocery-orders/orders/v1/integration-api/v1/actions/cancel',
    )
    def _orders_cancel():
        if reason != 'g_orders_error':
            assert False
        return mockserver.make_response(status=g_orders_error_code)

    g_orders_error_code = 400
    response = await taxi_grocery_uber_gw.post(
        'processing/v1/uber-gw/v1/order/cancel',
        data=json.dumps(request),
        headers={'content-type': 'application/json'},
    )
    assert response.status_code == (500 if reason == 'uber_error' else 200)

    if reason == 'g_orders_error':
        g_orders_error_code = 404
        response = await taxi_grocery_uber_gw.post(
            'processing/v1/uber-gw/v1/order/cancel',
            data=json.dumps(request),
            headers={'content-type': 'application/json'},
        )
        assert response.status_code == 500

        g_orders_error_code = 500
        response = await taxi_grocery_uber_gw.post(
            'processing/v1/uber-gw/v1/order/cancel',
            data=json.dumps(request),
            headers={'content-type': 'application/json'},
        )
        assert response.status_code == 500
