import pytest


def _check_parcel(db_parcel, response_parcel):
    assert response_parcel['id'] == db_parcel.item_id
    assert response_parcel['state'] == db_parcel.status
    assert response_parcel['state_meta'] == db_parcel.status_meta
    if 'barcode' in response_parcel:
        assert response_parcel['barcode'] == db_parcel.barcode
    if 'partner_id' in response_parcel:
        assert response_parcel['partner_id'] == db_parcel.partner_id
    if 'wms_id' in response_parcel:
        assert response_parcel['wms_id'] == db_parcel.wms_id


def _check_order(db_order, response_order, parcels_id_to_test_ids):
    assert response_order['order_id'] == db_order.order_id
    assert response_order['depot_id'] == db_order.depot_id
    assert response_order['ref_order'] == db_order.ref_order
    assert response_order['uid'] == db_order.uid
    assert response_order['state'] == db_order.status
    assert len(response_order['items']) == len(db_order.items)
    for response_parcel in response_order['items']:
        test_parcel_id = parcels_id_to_test_ids[response_parcel['id']]
        _check_parcel(db_order.items[test_parcel_id], response_parcel)


@pytest.mark.parametrize('id_type', ['id', 'ref_order'])
async def test_admin_order_get_200(
        taxi_tristero_parcels, tristero_parcels_db, id_type,
):
    """ test /admin/parcels/v1/order GET returns order with
    parcels by order_id and by ref_order """

    order = None
    parcels_id_to_test_ids = {}
    with tristero_parcels_db as db:
        order = db.add_order(1)
        first_parcel = order.add_parcel(1, status='in_depot')
        parcels_id_to_test_ids[first_parcel.item_id] = 1.0
        second_parcel = order.add_parcel(2, status='delivering')
        parcels_id_to_test_ids[second_parcel.item_id] = 2
        third_parcel = order.add_parcel(3, status='courier_assigned')
        parcels_id_to_test_ids[third_parcel.item_id] = 3
        fourth_parcel = order.add_parcel(4, status='courier_assigned')
        parcels_id_to_test_ids[fourth_parcel.item_id] = 4
    await taxi_tristero_parcels.invalidate_caches()

    params = {}
    params['vendor'] = order.vendor
    if id_type == 'id':
        params['id'] = order.order_id
    elif id_type == 'ref_order':
        params['ref_order'] = order.ref_order
    else:
        assert False

    response = await taxi_tristero_parcels.get(
        '/admin/parcels/v1/order', params=params,
    )
    assert response.status_code == 200
    _check_order(order, response.json(), parcels_id_to_test_ids)


async def test_admin_same_ref_order(
        taxi_tristero_parcels, tristero_parcels_db,
):
    ref_order = 'same-ref-order'
    orders = {}
    vendors = ['beru', 'vendor-test', 'another-vendor']
    with tristero_parcels_db as db:
        for i, vendor in enumerate(vendors):
            orders[vendor] = db.add_order(
                i + 1, ref_order=ref_order, vendor=vendor,
            )
    await taxi_tristero_parcels.invalidate_caches()

    assert all([order.ref_order == ref_order for order in orders.values()])

    for vendor in vendors:
        response = await taxi_tristero_parcels.get(
            'admin/parcels/v1/order',
            params={'ref_order': orders[vendor].ref_order, 'vendor': vendor},
        )
        assert response.status_code == 200
        assert response.json()['vendor'] == vendor
        assert response.json()['ref_order'] == ref_order

    response = await taxi_tristero_parcels.get(
        'admin/parcels/v1/order', params={'ref_order': ref_order},
    )
    assert response.status_code == 200
    assert response.json()['vendor'] == 'beru'


async def test_admin_cancelled_order(
        taxi_tristero_parcels, tristero_parcels_db,
):
    with tristero_parcels_db as db:
        cancelled_order = db.add_order(1, status='cancelled')
    await taxi_tristero_parcels.invalidate_caches()

    response = await taxi_tristero_parcels.get(
        '/admin/parcels/v1/order',
        params={
            'id': cancelled_order.order_id,
            'vendor': cancelled_order.vendor,
        },
    )
    assert response.json()['state'] == 'cancelled'


@pytest.mark.parametrize('id_type', ['id', 'ref_order'])
async def test_admin_order_get_404(taxi_tristero_parcels, id_type):
    """ test /admin/parcels/v1/order GET
    return 404 error on order not found in cache """

    params = {}
    params['vendor'] = 'beru'
    if id_type == 'id':
        params['id'] = '00000000-0000-0000-0000-000000000001'
    elif id_type == 'ref_order':
        params['ref_order'] = '1234567890'
    else:
        assert False

    response = await taxi_tristero_parcels.get(
        '/admin/parcels/v1/order', params=params,
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'ORDER_NOT_FOUND'


@pytest.mark.parametrize('ids', [['id', 'ref_order'], []])
async def test_admin_order_get_400(taxi_tristero_parcels, ids):
    """ test /admin/parcels/v1/order GET returns 400 when
    recieved more or less than one id """

    params = {}
    params['vendor'] = 'beru'
    if 'id' in ids:
        params['id'] = '00000000-0000-0000-0000-000000000001'
    if 'ref_order' in ids:
        params['ref_order'] = '1234567890'

    response = await taxi_tristero_parcels.get(
        '/admin/parcels/v1/order', params=params,
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'ONLY_ONE_ID_REQUIRED'
