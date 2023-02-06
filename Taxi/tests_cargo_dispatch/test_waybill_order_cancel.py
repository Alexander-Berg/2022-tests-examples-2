import pytest


def make_request(waybill_ref, *, reorder_required: bool = False):
    return {'waybill_ref': waybill_ref, 'reorder_required': reorder_required}


@pytest.mark.parametrize(['reorder_required'], [(False,), (True,)])
async def test_cancel_reason(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mock_order_cancel,
        read_waybill_info,
        mock_cargo_orders_performer_info,
        reorder_required: bool,
        waybill_id='waybill_fb_3',
):
    mock_cargo_orders_performer_info.no_performers = True

    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    mock_order_cancel.expected_request = {
        'order_id': cargo_order_id,
        'cancel_state': 'free',
        'cancel_reason': (
            'dispatch_reorder_required'
            if reorder_required
            else 'dispatch_delivery_out_of_time'
        ),
    }

    response = await taxi_cargo_dispatch.post(
        'v1/waybill/lookup/cancel',
        json=make_request(waybill_id, reorder_required=reorder_required),
    )

    assert response.status_code == 200


async def test_no_waybill(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mock_cargo_orders_performer_info,
        waybill_id='waybill_not_found',
):
    mock_cargo_orders_performer_info.no_performers = True

    response = await taxi_cargo_dispatch.post(
        'v1/waybill/lookup/cancel', json=make_request(waybill_id),
    )

    assert response.status_code == 404


async def test_performer_found(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mock_order_cancel,
        waybill_id='waybill_fb_3',
):
    response = await taxi_cargo_dispatch.post(
        'v1/waybill/lookup/cancel', json=make_request(waybill_id),
    )

    assert response.status_code == 410
