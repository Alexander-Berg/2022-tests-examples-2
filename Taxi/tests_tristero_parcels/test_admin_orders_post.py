import pytest


def _create_parcels(tristero_parcels_db, order_num):
    order = None
    product_keys = []
    with tristero_parcels_db as db:
        order = db.add_order(order_num + 1)
        for i, status in enumerate(
                [
                    'in_depot',
                    'delivering',
                    'courier_assigned',
                    'ready_for_delivery',
                ],
        ):
            product_keys.append(
                order.add_parcel(i + 1, status=status).product_key,
            )
    return order, product_keys


@pytest.mark.parametrize('request_type', ['normal', 'not_existing_parcel'])
async def test_basic(taxi_tristero_parcels, tristero_parcels_db, request_type):
    parcel_ids = []
    orders = []
    for order_num in range(2):
        order, product_keys = _create_parcels(tristero_parcels_db, order_num)
        parcel_ids.extend(product_keys)
        orders.append(order)

    await taxi_tristero_parcels.invalidate_caches()

    if request_type == 'not_existing_parcel':
        parcel_ids.extend(['bad_parcel_id_1', 'bad_parcel_id_2'])
    params = {'parcel_ids': parcel_ids}

    response = await taxi_tristero_parcels.post(
        '/admin/parcels/v1/orders',
        json=params,
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    assert len(response.json()['orders_info']) == 2

    for idx, order_info in enumerate(response.json()['orders_info']):
        for parcel in order_info['items']:
            if parcel_ids[idx] in parcel['parcel_id']:
                index_found = True
                break
        assert index_found

        assert order_info['order_id'] == orders[idx].order_id
        assert order_info['ref_order'] == orders[idx].ref_order

    if request_type == 'not_existing_parcel':
        assert len(response.json()['errors']) == 2
        for error in response.json()['errors']:
            assert error['error'] == 'parcel_not_found'


async def test_canceled_order_return(
        taxi_tristero_parcels, tristero_parcels_db,
):

    orders = []
    parcel_ids = []
    canceled_order = tristero_parcels_db.add_order(
        len(orders) + 1, status='cancelled',
    )
    c_parcel = canceled_order.add_parcel(1, status='delivering')
    orders.append(canceled_order)
    parcel_ids.extend({c_parcel.product_key})

    params = {'parcel_ids': parcel_ids}
    await taxi_tristero_parcels.invalidate_caches()

    response = await taxi_tristero_parcels.post(
        '/admin/parcels/v1/orders',
        json=params,
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    assert len(response.json()['orders_info']) == 1
