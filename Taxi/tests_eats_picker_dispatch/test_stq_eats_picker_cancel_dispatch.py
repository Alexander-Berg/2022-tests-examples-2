import pytest

from . import utils


EATS_ID = '111'
PLACE_ID = 100000


@utils.periodic_dispatcher_config3()
@pytest.mark.parametrize(
    'reason_code, full_reason',
    [
        ['PLACE_HAS_NO_PICKER', 'Place hasn\'t had pickers for long time'],
        ['NO_ESTIMATED_PICKING_TIME', 'No estimated_picking_time in order'],
        ['PICKER_FAIL_ASSIGNMENT', 'Picker assignation failed'],
        ['PLACE_HAS_TOO_MANY_ORDERS', 'Place has too many orders'],
        ['PLACE_CLOSES_SOON', 'Place will close soon'],
        ['PLACE_FINISHED_WORK_TIME', 'Place has finished its work time'],
        ['UNKNOWN_CANCEL_REASON', 'UNKNOWN_CANCEL_REASON'],
        ['', 'UNKNOWN_CANCEL_REASON'],
    ],
)
@pytest.mark.parametrize('place_id', [PLACE_ID, None])
@pytest.mark.parametrize(
    'expect_success,order_status_response,apply_state_response',
    [
        pytest.param(True, 200, 200, id='happy_path'),
        pytest.param(False, 404, None, id='order_status_404'),
        pytest.param(False, 500, None, id='order_status_500'),
        pytest.param(False, 200, 404, id='apply_state_404'),
        pytest.param(False, 200, 503, id='apply_state_503'),
    ],
)
@pytest.mark.now('2021-01-22T18:00:00')
async def test_stq_eats_picker_cancel_dispatch(
        taxi_eats_picker_dispatch,
        stq_runner,
        mockserver,
        taxi_eats_picker_dispatch_monitor,
        get_dispatch_cancel_reasons,
        expect_success,
        order_status_response,
        apply_state_response,
        place_id,
        reason_code,
        full_reason,
):
    @mockserver.json_handler('/eats-picker-orders/api/v1/order/status')
    def mock_status_change(request):
        assert request.method == 'POST'
        assert request.args['eats_id'] == EATS_ID
        assert request.json['status'] == 'dispatch_failed'
        assert request.json['comment'] == f'Picker Dispatch: {full_reason}'
        assert (
            request.json['reason_code'] == reason_code
            if reason_code
            else 'UNKNOWN_CANCEL_REASON'
        )
        return mockserver.make_response(json={}, status=order_status_response)

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        assert request.json['eats_id'] == EATS_ID
        assert request.json['status'] == 'dispatch_failed'
        assert request.json['timestamp'] == '2021-01-22T18:00:00+00:00'
        assert request.json['reason'] == full_reason
        assert (
            request.json['reason_code'] == reason_code
            if reason_code
            else 'UNKNOWN_CANCEL_REASON'
        )

        if apply_state_response == 200:
            response_jsons = {'isSuccess': True}
        else:
            response_jsons = {
                'isSuccess': False,
                'statusCode': apply_state_response,
                'type': '',
                'errors': [],
            }
        return mockserver.make_response(
            json=response_jsons, status=apply_state_response,
        )

    await taxi_eats_picker_dispatch.tests_control(reset_metrics=True)

    await stq_runner.eats_picker_cancel_dispatch.call(
        task_id=EATS_ID,  # 'eats_id' is passed as 'task_id'
        kwargs={'reason_code': reason_code, 'place_id': place_id},
    )

    metric_failed = await taxi_eats_picker_dispatch_monitor.get_metric(
        'dispatch-autocancel-failed',
    )

    expect_apply_state_call = apply_state_response is not None

    assert mock_status_change.times_called == 1
    assert mock_eats_core_picker_orders.times_called == int(
        expect_apply_state_call,
    )
    cancel_reasons_expected = {}

    if expect_apply_state_call:
        cancel_reasons_expected = {
            'PLACE_HAS_NO_PICKER': 0,
            'NO_ESTIMATED_PICKING_TIME': 0,
            'PICKER_FAIL_ASSIGNMENT': 0,
            'PLACE_HAS_TOO_MANY_ORDERS': 0,
            'PLACE_FINISHED_WORK_TIME': 0,
            'PLACE_CLOSES_SOON': 0,
            'UNKNOWN_CANCEL_REASON': 0,
            reason_code if reason_code else 'UNKNOWN_CANCEL_REASON': 1,
        }

    dispatch_cancel_reasons = await get_dispatch_cancel_reasons(place_id)
    assert dispatch_cancel_reasons == cancel_reasons_expected
    assert metric_failed == int(not expect_success)
