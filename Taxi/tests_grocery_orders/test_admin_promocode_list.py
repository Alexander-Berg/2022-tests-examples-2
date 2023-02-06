import json

import pytest

from . import headers
from . import models

EXPIRE_AT = '2020-03-13T07:19:13+00:00'


async def test_basic(taxi_grocery_orders, pgsql, grocery_coupons):
    order = models.Order(pgsql=pgsql)

    promocodes = [
        {
            'title': 'промокод 100 р',
            'subtitle': 'при заказе от 500 рублей',
            'valid': True,
            'promocode': 'LAVKA100',
            'expire_at': EXPIRE_AT,
            'type': 'fixed',
            'limit': '1000',
            'value': '100',
            'currency_code': 'RUB',
            'series_id': 'LAVKA',
        },
    ]

    grocery_coupons.check_coupons_list(skip_cart_check=True)
    grocery_coupons.set_coupons_list_response(response={'coupons': promocodes})

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/promocode/list', json={'order_id': order.order_id},
    )

    assert response.status == 200

    assert response.json()['promocodes'] == promocodes


@pytest.mark.parametrize(
    'order_flow', ['tristero_flow_v2', 'tristero_no_auth_flow_v1'],
)
async def test_no_auth_context(
        taxi_grocery_orders, pgsql, grocery_coupons, order_flow,
):
    order = models.Order(pgsql=pgsql, grocery_flow_version=order_flow)

    promocodes = [
        {
            'title': 'промокод 100 р',
            'subtitle': 'при заказе от 500 рублей',
            'valid': True,
            'promocode': 'LAVKA100',
            'expire_at': EXPIRE_AT,
            'type': 'fixed',
            'limit': '1000',
            'value': '100',
            'currency_code': 'RUB',
            'series_id': 'LAVKA',
        },
    ]

    grocery_coupons.check_coupons_list(skip_cart_check=True)
    grocery_coupons.set_coupons_list_response(response={'coupons': promocodes})

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/promocode/list', json={'order_id': order.order_id},
    )

    assert response.status == 200
    assert grocery_coupons.times_coupons_list_called() == 0
    assert response.json()['promocodes'] == []


async def test_client_recieves_extra_data(
        taxi_grocery_orders, pgsql, mockserver,
):
    order = models.Order(pgsql=pgsql)

    expected_request = {'depot_id': order.depot_id, 'skip_cart_check': True}

    @mockserver.json_handler('/grocery-coupons/internal/v1/coupons/list')
    def mock_check_request_contents(request):
        assert request.json == expected_request
        return {'coupons': []}

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/promocode/list', json={'order_id': order.order_id},
    )

    assert response.status == 200
    assert mock_check_request_contents.times_called == 1
    assert response.json()['promocodes'] == []


@pytest.mark.config(GROCERY_ORDERS_USE_COLD_STORAGE=True)
async def test_cold_storage(
        taxi_grocery_orders,
        pgsql,
        grocery_coupons,
        grocery_cold_storage,
        load_json,
):
    order_id = '9dc2300a4d004a9e9d854a9f5e45816a-grocery'
    depot_id = '60287'

    grocery_coupons.check_coupons_list(skip_cart_check=True, depot_id=depot_id)
    grocery_coupons.set_coupons_list_response(response={'coupons': []})

    request = load_json('cold_storage_request.json')
    grocery_cold_storage.set_orders_response(
        items=load_json('cold_storage_response.json')['items'],
    )
    grocery_cold_storage.check_orders_request(
        item_ids=request['item_ids'], fields=request['fields'],
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/promocode/list', json={'order_id': order_id},
    )

    assert response.status == 200
    assert grocery_coupons.times_coupons_list_called() == 1
    assert grocery_cold_storage.orders_times_called() == 1
