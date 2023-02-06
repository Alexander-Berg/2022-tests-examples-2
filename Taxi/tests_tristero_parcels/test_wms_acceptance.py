import copy

import pytest

REQUEST_EXAMPLE = {
    'acceptance_id': 'some_acceptance_id',
    'courier_id': 'some_courier_id',
    'depot_id': 'some_depot_id',
    'delivery_date': '2022-06-21',
    'courier_name': 'Иванов Иван Иванович',
    'order_data': [{'ref_order': 'some_ref_order', 'vendor': 'beru'}],
}


async def test_wms_acceptance_basic(
        taxi_tristero_parcels, tristero_parcels_db, mockserver,
):
    payload = copy.deepcopy(REQUEST_EXAMPLE)
    depot_id = tristero_parcels_db.make_depot_id(1)
    payload['depot_id'] = depot_id
    ref_orders = []
    with tristero_parcels_db as db:
        order = db.add_order(1, depot_id=depot_id, vendor='beru')
        order.add_parcel(1)
        order.add_parcel(2)
        ref_orders.append(order.ref_order)

        order_2 = db.add_order(2, depot_id=depot_id, vendor='beru')
        order_2.add_parcel(1)
        order_2.add_parcel(2)
        ref_orders.append(order_2.ref_order)

    payload['order_data'].clear()
    for _, ref_order in enumerate(ref_orders):
        payload['order_data'].append(
            {'ref_order': ref_order, 'vendor': 'beru'},
        )

    @mockserver.json_handler(
        '/grocery-wms/api/external/orders/v1/acceptance_items/create',
    )
    def _wms_acceptances_create(request):
        assert request.json['external_id'] == 'some_acceptance_id'
        assert request.json['market_courier'] == {
            'external_id': REQUEST_EXAMPLE['courier_id'],
            'name': REQUEST_EXAMPLE['courier_name'],
        }
        assert request.json['store_id'] == depot_id
        assert (
            request.json['delivery_date'] == REQUEST_EXAMPLE['delivery_date']
        )

        assert len(request.json['market_orders']) == 2
        for order in request.json['market_orders']:
            assert len(order['item_ids']) == 2
        return {'code': 'OK', 'order': {}}

    response = await taxi_tristero_parcels.post(
        'internal/v1/parcels/v1/acceptance', headers={}, json=payload,
    )

    assert response.status_code == 200


async def test_wms_acceptance_filter_orders(
        taxi_tristero_parcels, tristero_parcels_db, mockserver,
):
    payload = copy.deepcopy(REQUEST_EXAMPLE)
    depot_id = tristero_parcels_db.make_depot_id(1)
    payload['depot_id'] = depot_id
    ref_orders = []
    with tristero_parcels_db as db:
        # order in the wrong status, won't be sent to wms
        order = db.add_order(
            1, depot_id=depot_id, vendor='beru', status='received',
        )
        order.add_parcel(1)
        order.add_parcel(2)
        ref_orders.append(order.ref_order)

        # order in another depot, won't be sent to wms
        wrong_depot_id = 'some-depot-id'
        order_2 = db.add_order(2, depot_id=wrong_depot_id, vendor='beru')
        order_2.add_parcel(1)
        order_2.add_parcel(2)
        ref_orders.append(order_2.ref_order)

        order_3 = db.add_order(
            3, depot_id=depot_id, vendor='beru', status='expecting_delivery',
        )
        order_3.add_parcel(1)
        order_3.add_parcel(2)
        ref_orders.append(order_3.ref_order)

    payload['order_data'].clear()
    for _, ref_order in enumerate(ref_orders):
        payload['order_data'].append(
            {'ref_order': ref_order, 'vendor': 'beru'},
        )

    @mockserver.json_handler(
        '/grocery-wms/api/external/orders/v1/acceptance_items/create',
    )
    def _wms_acceptances_create(request):
        assert len(request.json['market_orders']) == 1
        return {'code': 'OK', 'order': {}}

    response = await taxi_tristero_parcels.post(
        'internal/v1/parcels/v1/acceptance', headers={}, json=payload,
    )

    assert response.status_code == 200


@pytest.mark.parametrize('error_status', [400, 403, 404, 409, 410])
async def test_wms_acceptance_errors(
        taxi_tristero_parcels, mockserver, error_status,
):
    @mockserver.json_handler(
        '/grocery-wms/api/external/orders/v1/acceptance_items/create',
    )
    def _wms_acceptances_create(request):
        return mockserver.make_response(
            json={'code': str(error_status), 'message': 'error_message'},
            status=error_status,
        )

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/acceptance', json=REQUEST_EXAMPLE,
    )
    assert response.status_code == error_status
    assert response.json() == {
        'code': str(error_status),
        'message': 'error_message',
    }


async def test_wms_acceptance_500(taxi_tristero_parcels, mockserver):
    @mockserver.json_handler(
        '/grocery-wms/api/external/orders/v1/acceptance_items/create',
    )
    def _mock_parcels(request):
        return mockserver.make_response(status=500)

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/acceptance', json=REQUEST_EXAMPLE,
    )
    assert response.status_code == 500
