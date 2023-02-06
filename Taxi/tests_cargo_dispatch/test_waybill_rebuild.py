from testsuite.utils import matching


async def test_reorder_success(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mockserver,
        mock_order_cancel,
        waybill_id='waybill_fb_3',
):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    mock_order_cancel.expected_request = {
        'order_id': matching.AnyString(),
        'cancel_state': 'free',
        'cancel_reason': 'waybill_rebuild_reorder_required',
    }

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/rebuild', json={'waybill_external_ref': waybill_id},
    )
    assert response.status_code == 200
    assert (
        response.json()['result']
        == 'Successfully sent cancel request to initiate reordering'
    )

    assert mock_order_cancel.handler.times_called == 1


async def test_free_cancel_forbidden(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        mock_order_cancel,
        waybill_id='waybill_fb_3',
):
    mock_order_cancel.status_code = 409

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/rebuild', json={'waybill_external_ref': waybill_id},
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'performer_assigned',
        'message': 'Cannot restart',
    }


async def test_waybill_not_found(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        mock_order_cancel,
        waybill_id='not_a_waybill_id',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/rebuild', json={'waybill_external_ref': waybill_id},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'not_found',
        'message': 'Waybill was not found',
    }
