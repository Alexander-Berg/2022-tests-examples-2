import pytest

from tests_tristero_parcels import headers
from tests_tristero_parcels import sql_queries

GROCERY_ORDER_RESPONSE = {
    'order_id': '4fe795ed-afd8-41d2-9f73-bb4333437bb5',
    'short_order_id': '280920-a-2254655',
    'status': 'assembled',
    'order_source': 'yango',
    'delivery_eta_min': 3,
    'cart_id': 'e30597e0-595e-4af9-96a5-010a5f4787c7',
    'client_price_template': '1000$SIGN$$CURRENCY$',
    'location': [10.0, 20.0],
    'address': {
        'country': 'order_country',
        'city': 'order_city',
        'street': 'order_street',
        'house': 'order_building',
        'floor': 'order_floor',
        'flat': 'order_flat',
        'doorcode': 'order_doorcode',
        'place_id': 'place-id',
    },
    'depot_location': [13.0, 37.0],
    'promise_max': '2020-05-25T15:38:45+00:00',
    'localized_promise': 'Заказ приедет к ~ 18:38',
    'courier_info': {'name': 'Ivan', 'transport_type': 'car'},
    'tracking_info': {'title': 'Ещё примерно 56 минут'},
    'status_updated': '2020-03-10T00:00:00+00:00',
    'actions': [{'type': 'call_courier'}],
}


@pytest.mark.parametrize('id_source', ['in_request, from db'])
async def test_internal_order_track_order_200(
        taxi_tristero_parcels,
        tristero_parcels_db,
        mockserver,
        pgsql,
        id_source,
):
    depot_id = tristero_parcels_db.make_depot_id(1)
    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id=headers.YANDEX_UID,
            depot_id=depot_id,
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
        )
    parcel = order.add_parcel(
        1, status='in_depot', partner_id='some_partner_id',
    )
    cursor = pgsql['tristero_parcels'].cursor()

    cursor.execute(
        sql_queries.insert_items_history(
            item_id=parcel.item_id,
            status=parcel.status,
            order_id=GROCERY_ORDER_RESPONSE['order_id'],
        ),
    )

    @mockserver.json_handler('/grocery-orders/internal/v1/orders-state')
    def _orders_state(request):
        assert (
            request.json['order_ids'][0] == GROCERY_ORDER_RESPONSE['order_id']
        )
        return {'grocery_orders': [GROCERY_ORDER_RESPONSE]}

    json = {
        'ref_order': order.ref_order,
        'vendor': order.vendor,
        'token': order.token,
        'device_pixel_ratio': 4,
    }
    if id_source == 'in_request':
        json['order_id'] = GROCERY_ORDER_RESPONSE['order_id']

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/order/track', json=json,
    )
    response_json = response.json()['order_data']
    assert response.status_code == 200
    for key, value in GROCERY_ORDER_RESPONSE.items():
        if key not in [
                'order_source',
                'cart_id',
                'status_updated',
                'order_id',
        ]:
            assert response_json[key] == value
    assert (
        response_json['grocery_order_id'] == GROCERY_ORDER_RESPONSE['order_id']
    )

    order_in_response = response_json['order']
    assert order.ref_order == order_in_response['ref_order']
    assert order.order_id == order_in_response['order_id']
    assert order.vendor == order_in_response['vendor']
    assert order.depot_id == order_in_response['depot_id']
    assert order.status == order_in_response['state']
    parcels = order_in_response['items']
    assert parcels[0]['order_id'] == order.order_id
    assert parcels[0]['state'] == 'in_depot'
    assert parcels[0]['partner_id'] == 'some_partner_id'
    assert 'quantity_limit' in parcels[0]


@pytest.mark.parametrize('reason', ['unknown_order', 'no_tracking_info'])
async def test_internal_order_track_order_404(
        taxi_tristero_parcels, tristero_parcels_db, mockserver, pgsql, reason,
):
    with tristero_parcels_db as db:
        order = db.add_order(1)

    parcel = order.add_parcel(
        1, status='in_depot', partner_id='some_partner_id',
    )
    cursor = pgsql['tristero_parcels'].cursor()

    cursor.execute('select id from parcels.items')
    for i in cursor:
        print(i)

    cursor.execute(
        sql_queries.insert_items_history(
            item_id=parcel.item_id,
            status=parcel.status,
            order_id=GROCERY_ORDER_RESPONSE['order_id'],
        ),
    )

    @mockserver.json_handler('/grocery-orders/internal/v1/orders-state')
    def _orders_state(request):
        return {'grocery_orders': []}

    if reason == 'unknown_order':
        json = {
            'ref_order': 'wrong_ref_order',
            'vendor': 'wrong_vendor',
            'token': 'wrong_token',
            'device_pixel_ratio': 4,
        }
    else:
        json = {
            'ref_order': order.ref_order,
            'vendor': order.vendor,
            'token': order.token,
            'device_pixel_ratio': 4,
        }

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/order/track', json=json,
    )

    assert response.status_code == 200
    assert response.json() == {}
    if reason == 'unknown_order':
        assert _orders_state.times_called == 0
    else:
        assert _orders_state.times_called == 1


async def test_internal_order_priority(
        taxi_tristero_parcels, tristero_parcels_db, mockserver, pgsql,
):
    depot_id = tristero_parcels_db.make_depot_id(1)
    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id=headers.YANDEX_UID,
            depot_id=depot_id,
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
        )
    parcel_1 = order.add_parcel(
        1, status='in_depot', partner_id='some_partner_id',
    )
    parcel_2 = order.add_parcel(2, status='in_depot')
    parcel_3 = order.add_parcel(3, status='delivering')
    cursor = pgsql['tristero_parcels'].cursor()

    grocery_order_ids = [
        '4fe795ed-afd8-41d2-9f73-bb4333437bb0',
        '4fe795ed-afd8-41d2-9f73-bb4333437bb1',
        '4fe795ed-afd8-41d2-9f73-bb4333437bb2',
    ]
    cursor.execute(
        sql_queries.insert_items_history(
            item_id=parcel_1.item_id,
            status=parcel_1.status,
            order_id=grocery_order_ids[0],
        ),
    )
    cursor.execute(
        sql_queries.insert_items_history(
            item_id=parcel_2.item_id,
            status=parcel_2.status,
            order_id=grocery_order_ids[1],
        ),
    )
    cursor.execute(
        sql_queries.insert_items_history(
            item_id=parcel_3.item_id,
            status=parcel_3.status,
            order_id=grocery_order_ids[2],
        ),
    )

    @mockserver.json_handler('/grocery-orders/internal/v1/orders-state')
    def _orders_state(request):
        request_order_ids = request.json['order_ids']
        assert len(request_order_ids) == 3
        orders_responses = [
            GROCERY_ORDER_RESPONSE.copy(),
            GROCERY_ORDER_RESPONSE.copy(),
            GROCERY_ORDER_RESPONSE.copy(),
        ]
        for i, response in enumerate(orders_responses):
            response['order_id'] = request_order_ids[i]
        orders_responses[2]['status'] = 'closed'  # inactive status
        orders_responses[2][
            'status_updated'
        ] = '2020-03-10T00:00:02+00:00'  # least recently updated
        orders_responses[1][
            'status_updated'
        ] = '2020-03-10T00:00:01+00:00'  # most recently updated
        orders_responses[0][
            'status_updated'
        ] = '2020-03-10T00:00:00+00:00'  # least recently updated among active
        return {'grocery_orders': orders_responses}

    json = {
        'ref_order': order.ref_order,
        'vendor': order.vendor,
        'token': order.token,
        'device_pixel_ratio': 4,
    }
    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/order/track', json=json,
    )

    response_json = response.json()
    print(response_json)
    assert response.status_code == 200
    assert (
        response_json['order_data']['grocery_order_id'] == grocery_order_ids[1]
    )  # least recently updated amongst active orders
