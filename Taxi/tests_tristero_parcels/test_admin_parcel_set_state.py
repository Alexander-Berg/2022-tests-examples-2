import pytest


@pytest.mark.parametrize(
    'old_status',
    [
        'reserved',
        'created',
        'in_depot',
        'ready_for_delivery',
        'courier_assigned',
        'delivering',
        'delivered',
    ],
)
@pytest.mark.parametrize(
    'new_status, new_order_status',
    [
        ('reserved', 'reserved'),
        ('created', 'expecting_delivery'),
        ('in_depot', 'received'),
        ('courier_assigned', 'received'),
        ('ready_for_delivery', 'received'),
        ('delivering', 'received'),
        ('delivered', 'delivered'),
    ],
)
async def test_internal_parcel_set_state_one_parcel(
        taxi_tristero_parcels,
        tristero_parcels_db,
        old_status,
        new_status,
        new_order_status,
):
    """ test PUT /admin/parcels/v1/parcel/set-state
    changes parcel status and its order status
    this case for orders with only one parcel """

    parcel = None
    with tristero_parcels_db as db:
        order = db.add_order(1)
        parcel = order.add_parcel(1, status=old_status)

    response = await taxi_tristero_parcels.put(
        '/admin/parcels/v1/parcel/set-state',
        params={'id': parcel.item_id},
        json={'state': new_status},
    )
    assert response.status_code == 200

    parcel.update_from_db()
    assert parcel.status == new_status
    if old_status == new_status:
        # trigger should work only on UPDATE
        prev_status = order.status
        order.update_from_db()
        assert order.status == prev_status
    else:
        order.update_from_db()
        assert order.status == new_order_status


@pytest.mark.parametrize(
    'old_status, new_status, new_order_status',
    [
        ('reserved', 'created', 'reserved'),
        ('reserved', 'in_depot', 'received_partialy'),
        ('reserved', 'ready_for_delivery', 'received_partialy'),
        ('reserved', 'courier_assigned', 'received_partialy'),
        ('reserved', 'delivering', 'received_partialy'),
        ('reserved', 'delivered', 'delivered_partially'),
        ('created', 'reserved', 'reserved'),
        ('created', 'in_depot', 'received_partialy'),
        ('created', 'courier_assigned', 'received_partialy'),
        ('created', 'ready_for_delivery', 'received_partialy'),
        ('created', 'delivering', 'received_partialy'),
        ('created', 'delivered', 'delivered_partially'),
        ('in_depot', 'reserved', 'received_partialy'),
        ('in_depot', 'created', 'received_partialy'),
        ('in_depot', 'courier_assigned', 'received'),
        ('in_depot', 'ready_for_delivery', 'received'),
        ('in_depot', 'delivering', 'received'),
        ('in_depot', 'delivered', 'delivered_partially'),
        ('ready_for_delivery', 'reserved', 'received_partialy'),
        ('ready_for_delivery', 'created', 'received_partialy'),
        ('ready_for_delivery', 'in_depot', 'received'),
        ('ready_for_delivery', 'courier_assigned', 'received'),
        ('ready_for_delivery', 'delivering', 'received'),
        ('ready_for_delivery', 'delivered', 'delivered_partially'),
        ('courier_assigned', 'reserved', 'received_partialy'),
        ('courier_assigned', 'created', 'received_partialy'),
        ('courier_assigned', 'in_depot', 'received'),
        ('courier_assigned', 'ready_for_delivery', 'received'),
        ('courier_assigned', 'delivering', 'received'),
        ('courier_assigned', 'delivered', 'delivered_partially'),
        ('delivering', 'reserved', 'received_partialy'),
        ('delivering', 'created', 'received_partialy'),
        ('delivering', 'in_depot', 'received'),
        ('delivering', 'courier_assigned', 'received'),
        ('delivering', 'ready_for_delivery', 'received'),
        ('delivering', 'delivered', 'delivered_partially'),
        ('delivered', 'reserved', 'delivered_partially'),
        ('delivered', 'created', 'delivered_partially'),
        ('delivered', 'in_depot', 'delivered_partially'),
        ('delivered', 'delivering', 'delivered_partially'),
    ],
)
async def test_internal_parcel_set_state_two_parcels(
        taxi_tristero_parcels,
        tristero_parcels_db,
        old_status,
        new_status,
        new_order_status,
):
    """ test PUT /admin/parcels/v1/parcel/set-state
    changes parcel status and its order status
    this case for orders with two or more parcels
    we will change status for only one parcel and
    will check order status changes """

    with tristero_parcels_db as db:
        order = db.add_order(1)
        parcel = order.add_parcel(1, status=old_status)
        order.add_parcel(2, status=old_status)

    response = await taxi_tristero_parcels.put(
        '/admin/parcels/v1/parcel/set-state',
        params={'id': parcel.item_id},
        json={'state': new_status},
    )
    assert response.status_code == 200
    parcel.update_from_db()
    assert parcel.status == new_status
    order.update_from_db()
    assert order.status == new_order_status


@pytest.mark.parametrize(
    'new_status, is_update_cancelled',
    [('in_depot', True), ('in_depot', False)],
)
async def test_internal_parcel_set_state_canceled_order_never_changes(
        taxi_tristero_parcels,
        tristero_parcels_db,
        new_status,
        taxi_config,
        is_update_cancelled,
):
    """ test PUT /admin/parcels/v1/parcel/set-state
    changes parcel status and does not change canceled
    order status"""

    with tristero_parcels_db as db:
        order = db.add_order(1, status='cancelled')
        parcel = order.add_parcel(1)

    old_status = parcel.status
    taxi_config.set(
        TRISTERO_PARCELS_SHOULD_UPDATE_CANCELED_ORDERS=is_update_cancelled,
    )
    response = await taxi_tristero_parcels.put(
        '/admin/parcels/v1/parcel/set-state',
        params={'id': parcel.item_id},
        json={'state': new_status},
    )

    parcel.update_from_db()
    if is_update_cancelled:
        assert response.status_code == 200
        assert parcel.status == new_status
    else:
        assert response.status_code == 404
        assert parcel.status == old_status

    order.update_from_db()
    assert order.status == 'cancelled'


async def test_internal_parcel_set_state_404(taxi_tristero_parcels):
    """ test PUT /admin/parcels/v1/parcel/set-state
    return 404 error on parcel not found in cache """

    response = await taxi_tristero_parcels.put(
        '/admin/parcels/v1/parcel/set-state',
        params={'id': '00000000-0000-0000-0000-000000000001'},
        json={'state': 'delivered'},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'PARCEL_NOT_FOUND'
