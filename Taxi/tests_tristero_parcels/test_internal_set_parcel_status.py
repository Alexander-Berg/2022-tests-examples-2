import pytest

from tests_tristero_parcels import headers


@pytest.mark.parametrize(
    'status',
    [
        'reserved',
        'created',
        'in_depot',
        'ready_for_delivery',
        'courier_assigned',
        'delivering',
    ],
)
@pytest.mark.parametrize('header', [{}, headers.DEFAULT_HEADERS])
async def test_internal_parcels_set_delivered(
        taxi_tristero_parcels,
        taxi_config,
        tristero_parcels_db,
        status,
        header,
):
    """ test PUT /internal/v1/parcels/v1/set-status set
    requested status and meta for parcels by wms ids """

    status_meta = {'some_id': '1122334455'}
    parcels = []
    parcel_product_keys = []

    with tristero_parcels_db as db:
        order = db.add_order(1, user_id=headers.YANDEX_UID)
        # lets add some parcels
        for i in range(3):
            parcel = order.add_parcel(i + 1, status='created')
            parcels.append(parcel)
            parcel_product_keys.append(parcel.product_key)
        other_order = db.add_order(2, user_id='some_other_user')
        other_parcel = other_order.add_parcel(100, status='created')
        parcels.append(other_parcel)
        parcel_product_keys.append(other_parcel.product_key)
    await taxi_tristero_parcels.invalidate_caches()

    response = await taxi_tristero_parcels.put(
        '/internal/v1/parcels/v1/set-state',
        headers=header,
        json={
            'parcel_wms_ids': parcel_product_keys,
            'state': status,
            'state_meta': status_meta,
        },
    )

    assert response.status_code == 200
    assert set(response.json()['parcel_wms_ids']) == {
        p.product_key for p in parcels
    }

    for parcel in parcels:
        parcel.update_from_db()
        assert parcel.status == status
        assert parcel.status_meta == status_meta


async def test_internal_parcels_set_update_order(
        taxi_tristero_parcels, taxi_config, tristero_parcels_db,
):
    """ test PUT /internal/v1/parcels/v1/set-status also
    update order via trigger """

    new_status = 'ordered'

    with tristero_parcels_db as db:
        order = db.add_order(1, user_id=headers.YANDEX_UID, status='received')
        parcel = order.add_parcel(1, status='in_depot')
    order.update_from_db()
    updated_before_request = order.updated

    response = await taxi_tristero_parcels.put(
        '/internal/v1/parcels/v1/set-state',
        headers=headers.DEFAULT_HEADERS,
        json={
            'parcel_wms_ids': [parcel.product_key],
            'state': new_status,
            'state_meta': {},
        },
    )
    assert response.status_code == 200

    order.update_from_db()
    assert order.status == 'received'
    assert order.updated != updated_before_request
    parcel.update_from_db()
    assert parcel.status == new_status
    assert parcel.updated == order.updated


@pytest.mark.parametrize('auto_ordered', [True, False])
async def test_internal_parcels_set_in_depot_auto_ordered(
        taxi_tristero_parcels, taxi_config, tristero_parcels_db, auto_ordered,
):
    """ Test a corner case when parcel's status was auto_ordered before
    and now has became in_depot, it's request_kind should become on_demand."""

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id=headers.YANDEX_UID,
            status='received',
            request_kind='wide_slot',
        )
        parcel = order.add_parcel(1, status='in_depot')

        dispatch_start = '2021-07-15T15:00:00+03:00'
        dispatch_end = '2021-07-15T16:00:00+03:00'
        order.insert_dispatch_schedule(
            dispatch_start, dispatch_end, dispatched=auto_ordered,
        )

    if auto_ordered:
        parcel.set_status('auto_ordered')
    parcel.set_status('ordered')

    order.update_from_db()
    assert order.request_kind == 'wide_slot'

    response = await taxi_tristero_parcels.put(
        '/internal/v1/parcels/v1/set-state',
        headers=headers.DEFAULT_HEADERS,
        json={
            'parcel_wms_ids': [parcel.product_key],
            'state': 'in_depot',
            'state_meta': {},
        },
    )
    order.update_from_db()
    assert response.status_code == 200
    assert order.request_kind == ('on_demand' if auto_ordered else 'wide_slot')
