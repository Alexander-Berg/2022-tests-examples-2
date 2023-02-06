import pytest

from testsuite.utils import ordered_object


@pytest.mark.parametrize(
    'handler_path',
    [
        '/internal/v1/parcels/orders/history',
        '/admin/parcels/v1/orders/history',
    ],
)
async def test_internal_orders_history_order_statuses(
        taxi_tristero_parcels, tristero_parcels_db, handler_path,
):
    """ Checks that /internal/v1/parcels/orders/history
    and /admin/parcels/v1/orders/history
    returns all order statuses in response """

    statuses = [
        'reserved',
        'expecting_delivery',
        'received_partialy',
        'received',
        'delivered_partially',
        'delivered',
        'cancelled',
    ]

    with tristero_parcels_db as db:
        order = db.add_order(1)
        for status in statuses:
            if status == 'reserved':
                continue
            order.set_status(status)

    response = await taxi_tristero_parcels.post(
        handler_path, json={'order_ids': [order.order_id]},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data['orders']) == 1
    order_history = response_data['orders'][0]
    assert order.order_id == order_history['order_id']
    assert order.depot_id == order_history['depot_id']
    assert not order_history['items']
    ordered_object.assert_eq(
        statuses, [event['state'] for event in order_history['events']], [''],
    )


@pytest.mark.parametrize(
    'handler_path',
    [
        '/internal/v1/parcels/orders/history',
        '/admin/parcels/v1/orders/history',
    ],
)
async def test_internal_orders_history_order_with_parcels_statuses(
        taxi_tristero_parcels, tristero_parcels_db, handler_path,
):
    """ Checks that /internal/v1/parcels/orders/history
    and /admin/parcels/v1/orders/history
    returns all parcel statuses in response """

    statuses = [
        'reserved',
        'created',
        'in_depot',
        'ordered',
        'order_cancelled',
        'ready_for_delivery',
        'courier_assigned',
        'delivering',
        'delivered',
        'returned_to_vendor',
        'auto_ordered',
    ]

    with tristero_parcels_db as db:
        order = db.add_order(1)
        parcel = order.add_parcel(1)
        for status in statuses:
            if status == 'reserved':
                continue
            parcel.set_status(status)
        order.set_status('expecting_delivery')
        order.set_status('received_partialy')
        order.set_status('cancelled')

    response = await taxi_tristero_parcels.post(
        handler_path, json={'order_ids': [order.order_id]},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data['orders']) == 1
    order_history = response_data['orders'][0]
    assert order.order_id == order_history['order_id']
    assert order.depot_id == order_history['depot_id']
    assert len(order_history['items']) == 1
    parcel_history = order_history['items'][0]
    assert parcel.item_id == parcel_history['item_id']
    assert parcel.barcode == parcel_history['barcode']
    ordered_object.assert_eq(
        statuses, [event['state'] for event in parcel_history['events']], [''],
    )
