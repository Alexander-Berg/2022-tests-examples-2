import pytest

DISPATCH_TYPE = 'cargo_sync'
CLAIM_ID_1 = 'claim_1'
CLAIM_ID_2 = 'claim_2'

COURIER_ID_0 = 'courier_id_0'
DRIVER_ID_0 = 'driver_id_0'
PARK_ID_0 = 'park_id_0'

NOW = '2020-10-05T16:28:00.000Z'
DELIVERY_ETA_TS = '2020-10-05T16:38:00.000Z'


@pytest.mark.now(NOW)
async def test_basic_claim_status_200(
        taxi_grocery_dispatch,
        mocked_time,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
        pgsql,
):
    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    cargo_model = cargo_pg.create_claim(
        dispatch_id=dispatch_info.dispatch_id,
        claim_id=CLAIM_ID_1,
        claim_version=123,
    )

    cargo.set_data(
        items=cargo.convert_items(dispatch_info.order.items),
        delivered_eta_ts=DELIVERY_ETA_TS,
        courier_name='test_courier_name',
        version=123,
        status='performer_found',
    )
    cargo.add_performer(
        claim_id=CLAIM_ID_1,
        eats_profile_id=COURIER_ID_0,
        driver_id=DRIVER_ID_0,
        park_id=PARK_ID_0,
    )

    request = {'claim_id': CLAIM_ID_1}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/claim_status', request,
    )

    assert response.status_code == 200

    assert response.json()['status'] == 'matched'
    assert (
        response.json()['performer']['performer_id']
        == PARK_ID_0 + '_' + DRIVER_ID_0
    )
    assert (
        response.json()['performer']['performer_name'] == 'test_courier_name'
    )

    assert cargo_model.claim_version == 123
    assert cargo.times_external_info_called() == 1


@pytest.mark.now(NOW)
async def test_claim_status_404(
        taxi_grocery_dispatch,
        mocked_time,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
        pgsql,
):
    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch_info.dispatch_id,
        claim_id=CLAIM_ID_1,
        claim_version=123,
    )

    request = {'claim_id': CLAIM_ID_2}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/claim_status', request,
    )

    assert response.status_code == 204
    assert cargo.times_external_info_called() == 0
