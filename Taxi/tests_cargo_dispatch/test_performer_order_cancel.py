import pytest


@pytest.mark.parametrize('reason', ['performer_not_found', 'performer_cancel'])
@pytest.mark.parametrize('perf_cancel_need_reorder', [True, False])
@pytest.mark.parametrize('need_reorder', [True, False])
async def test_order_fail_performer_cancel_need_reorder(
        happy_path_state_orders_created,
        taxi_cargo_dispatch,
        mock_cargo_orders_bulk_info,
        testpoint,
        set_up_cargo_dispatch_reorder_exp,
        reason: str,
        perf_cancel_need_reorder: bool,
        need_reorder: bool,
        waybill_id='waybill_smart_1',
):
    await set_up_cargo_dispatch_reorder_exp(
        performer_cancel_need_reorder=perf_cancel_need_reorder,
        is_reorder_required=need_reorder,
    )
    mock_cargo_orders_bulk_info()

    @testpoint('order-fail::is_reorder_required')
    def _is_reorder_required(data):
        assert data['is_reorder_required'] == (
            reason == 'performer_cancel'
            and need_reorder
            and perf_cancel_need_reorder
        )

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json={
            'order_id': '6dac297a-33ed-42e7-9101-af81ddf59602',
            'waybill_id': waybill_id,
            'taxi_order_id': 'taxi-order',
            'reason': reason,
            'lookup_version': 0,
            'performer_cancel_need_reorder': perf_cancel_need_reorder,
        },
    )
    assert response.status_code == 200
