import pytest

LOGISTIC_DISPATCH = 'logistic-dispatch'


# pylint: disable=invalid-name
pytestmark = [pytest.mark.usefixtures('set_up_alive_batch_exp')]


def build_request(waybill_id, manual_dispatch=True):
    return {
        'waybill_ref': waybill_id,
        'order_id': 'b66b2650-31b5-46d2-95dc-5ff80f865c6f',
        'taxi_order_id': 'taxi-order',
        'performer': {'driver_id': 'driver_id1', 'park_id': 'park_id1'},
        'manual_dispatch': manual_dispatch,
        'lookup_version': 0,
    }


@pytest.fixture(name='state_order_created_by_ld')
async def _state_order_created_by_ld(
        happy_path_state_first_import,
        set_up_segment_routers_exp,
        propose_from_segments,
        run_choose_routers,
        run_choose_waybills,
        run_create_orders,
        mock_claim_bulk_update_state,
        run_notify_claims,
):
    await set_up_segment_routers_exp(smart_router=LOGISTIC_DISPATCH)
    await run_choose_routers()
    await propose_from_segments(LOGISTIC_DISPATCH, 'waybill_ld_1', 'seg1')

    await run_choose_waybills()
    await run_create_orders(should_set_stq=True)
    await run_notify_claims()

    assert mock_claim_bulk_update_state.handler.times_called == 1
    mock_claim_bulk_update_state.handler.flush()


async def test_ok(
        state_order_created_by_ld,
        taxi_cargo_dispatch,
        mock_assign_external_driver,
        waybill_id='waybill_ld_1',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/performer-assigning', json=build_request(waybill_id),
    )
    assert response.status_code == 200

    assert mock_assign_external_driver.last_request == {
        'waybill_ref': waybill_id,
        'order_id': 'b66b2650-31b5-46d2-95dc-5ff80f865c6f',
        'taxi_order_id': 'taxi-order',
        'performer': {'driver_id': 'driver_id1', 'park_id': 'park_id1'},
        'kind': 'manual_dispatch',
        'lookup_version': 0,
    }


@pytest.mark.parametrize(
    'ld_status_code, expected_code',
    [(404, 'performer_not_found'), (409, 'performer_is_booked')],
)
async def test_error_codes(
        state_order_created_by_ld,
        taxi_cargo_dispatch,
        mock_assign_external_driver,
        ld_status_code: int,
        expected_code: str,
        waybill_id='waybill_ld_1',
):
    mock_assign_external_driver.status_code = ld_status_code
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/performer-assigning', json=build_request(waybill_id),
    )
    assert response.status_code == ld_status_code
    assert response.json()['code'] == expected_code


async def test_initial_waybill(
        state_order_created_by_ld,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_assign_external_driver,
        taxi_cargo_dispatch,
        initial_waybill_ref='waybill_ld_1',
        replace_waybill_ref='waybill_ld_2',
):
    waybill = await waybill_from_segments(
        LOGISTIC_DISPATCH, replace_waybill_ref, 'seg1', 'seg2',
    )
    response = await request_waybill_update_proposition(
        waybill, initial_waybill_ref,
    )
    assert response.status_code == 200

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/performer-assigning',
        json=build_request(initial_waybill_ref),
    )
    assert response.status_code == 200

    assert (
        mock_assign_external_driver.last_request['waybill_ref']
        == initial_waybill_ref
    )
