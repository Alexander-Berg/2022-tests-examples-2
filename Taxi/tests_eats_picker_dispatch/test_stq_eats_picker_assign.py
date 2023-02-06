import pytest

from . import utils


EATS_ID = '1'
PLACE_ID = 100000


def order_get_response(eats_id, status, picker_id, estimated_picking_time):
    return {
        'json': {
            'payload': {
                'id': eats_id,
                'status': status,
                'status_updated_at': '2020-10-15T15:00:00Z',
                'ordered_total': '1',
                'eats_id': eats_id,
                'currency': {'code': 'RUB', 'sign': 'Р'},
                'categories': [],
                'picker_items': [],
                'require_approval': True,
                'flow_type': 'picking_only',
                'place_id': 1,
                'picker_id': picker_id,
                'estimated_picking_time': estimated_picking_time,
                'created_at': '2020-10-15T14:59:59Z',
                'updated_at': '2020-10-15T15:00:00Z',
            },
            'meta': {},
        },
        'status': 200,
    }


SELECT_PICKER_RESPONSE = {
    'status': 200,
    'json': {
        'picker_id': '1',
        'requisite_type': 'TinkoffCard',
        'requisite_value': '0011223344556677',
        'picker_name': 'Picker Huicker',
        'picker_phone_id': 'abcd12345',
    },
}


def make_courier_update_response(mockserver, status):
    data = {}
    if status in [429, 503]:
        data['code'] = 'TIMEOUT'
        data['message'] = 'timeout'
    return mockserver.make_response(json=data, status=status)


@utils.periodic_dispatcher_config3()
@pytest.mark.config(
    EATS_PICKER_ASSIGN_STQ_SETTINGS={
        'retries': 1,
        'stq_timeout_sec': 1,
        'picker_exclusion_time_sec': 10,
    },
)
@pytest.mark.parametrize(
    'order_status, order_picker, estimated_picking_time, '
    'picker_response, courier_update_status,'
    'exec_tries, reschedule_called, order_get_called, '
    'status_change_called, courier_update_called, '
    'select_picker_called, hold_supply_called, '
    'change_priority_called, dispatch_restart, '
    'assign_reschedule, reschedule_counter, dispatch_failed',
    [
        pytest.param(
            # retries number exceeded, no picker set
            'dispatching',
            None,
            200,
            SELECT_PICKER_RESPONSE,
            202,
            15,
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            15,
            0,
            0,
            True,
            marks=[pytest.mark.now('2020-10-15T15:00:02Z')],
        ),
        pytest.param(
            # retries number exceeded, picker is not changed
            'dispatching',
            '1',
            200,
            SELECT_PICKER_RESPONSE,
            202,
            15,
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            15,
            0,
            0,
            True,
            marks=[pytest.mark.now('2020-10-15T15:00:02Z')],
        ),
        pytest.param(
            # order status was unexpectedly changed to 'new'
            'new',
            None,
            200,
            SELECT_PICKER_RESPONSE,
            202,
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            False,
            marks=[pytest.mark.now('2020-10-15T15:00:00Z')],
        ),
        pytest.param(
            # ok
            'dispatching',
            None,
            200,
            SELECT_PICKER_RESPONSE,
            202,
            0,
            0,
            1,
            0,
            1,
            1,
            0,
            1,
            0,
            0,
            0,
            False,
            marks=[pytest.mark.now('2020-10-15T15:00:00Z')],
        ),
        pytest.param(
            # timeout
            'dispatching',
            None,
            200,
            SELECT_PICKER_RESPONSE,
            202,
            0,
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            2,
            2,
            True,
            marks=[pytest.mark.now('2020-10-15T15:00:02Z')],
        ),
        pytest.param(
            # 500 error on courier update
            'dispatching',
            None,
            200,
            SELECT_PICKER_RESPONSE,
            500,
            0,
            1,
            1,
            0,
            1,
            1,
            1,
            1,
            0,
            0,
            0,
            False,
            marks=[pytest.mark.now('2020-10-15T15:00:00Z')],
        ),
        pytest.param(
            # 40x error on courier update
            'dispatching',
            None,
            200,
            SELECT_PICKER_RESPONSE,
            400,
            0,
            0,
            1,
            1,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            True,
            marks=[pytest.mark.now('2020-10-15T15:00:00Z')],
        ),
        pytest.param(
            # 409 error on courier update
            'dispatching',  # order_status
            None,  # order_picker
            200,  # estimated_picking_time
            SELECT_PICKER_RESPONSE,  # picker_response
            409,  # courier_update_status
            0,  # exec_tries
            1,  # reschedule_called
            1,  # order_get_called
            0,  # status_change_called
            1,  # courier_update_called
            1,  # select_picker_called
            0,  # hold_supply_called
            0,  # change_priority_called
            0,  # dispatch_restart
            1,  # assign_reschedule
            1,  # reschedule_counter
            False,  # dispatch_failed
            marks=[pytest.mark.now('2020-10-15T15:00:00Z')],
        ),
        pytest.param(
            # 423 error on courier update
            'dispatching',  # order_status
            None,  # order_picker
            200,  # estimated_picking_time
            SELECT_PICKER_RESPONSE,  # picker_response
            423,  # courier_update_status
            0,  # exec_tries
            0,  # reschedule_called
            1,  # order_get_called
            1,  # status_change_called
            1,  # courier_update_called
            1,  # select_picker_called
            0,  # hold_supply_called
            0,  # change_priority_called
            0,  # dispatch_restart
            0,  # assign_reschedule
            0,  # reschedule_counter
            False,  # dispatch_failed
            marks=[pytest.mark.now('2020-10-15T15:00:00Z')],
        ),
        pytest.param(
            # 429 error on courier update
            'dispatching',  # order_status
            None,  # order_picker
            200,  # estimated_picking_time
            SELECT_PICKER_RESPONSE,  # picker_response
            429,  # courier_update_status
            0,  # exec_tries
            1,  # reschedule_called
            1,  # order_get_called
            0,  # status_change_called
            1,  # courier_update_called
            1,  # select_picker_called
            0,  # hold_supply_called
            0,  # change_priority_called
            0,  # dispatch_restart
            1,  # assign_reschedule
            1,  # reschedule_counter
            False,  # dispatch_failed
            marks=[pytest.mark.now('2020-10-15T15:00:00Z')],
        ),
        pytest.param(
            # 503 error on courier update
            'dispatching',  # order_status
            None,  # order_picker
            200,  # estimated_picking_time
            SELECT_PICKER_RESPONSE,  # picker_response
            503,  # courier_update_status
            0,  # exec_tries
            1,  # reschedule_called
            1,  # order_get_called
            0,  # status_change_called
            1,  # courier_update_called
            1,  # select_picker_called
            0,  # hold_supply_called
            0,  # change_priority_called
            0,  # dispatch_restart
            1,  # assign_reschedule
            1,  # reschedule_counter
            False,  # dispatch_failed
            marks=[pytest.mark.now('2020-10-15T15:00:00Z')],
        ),
        pytest.param(
            # picker not found
            'dispatching',
            None,
            200,
            {
                'status': 404,
                'json': {'message': 'Picker not found', 'code': '404'},
            },
            202,
            0,
            0,
            1,
            1,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            False,
            marks=[pytest.mark.now('2020-10-15T15:00:00Z')],
        ),
        pytest.param(
            # no estimated_picking_time
            'dispatching',
            None,
            None,
            SELECT_PICKER_RESPONSE,
            202,
            0,
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            True,
            marks=[pytest.mark.now('2020-10-15T15:00:00Z')],
        ),
    ],
)
async def test_stq_eats_picker_assign(
        stq_runner,
        mockserver,
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        get_dispatch_cancel_reasons,
        order_status,
        order_picker,
        estimated_picking_time,
        picker_response,
        courier_update_status,
        exec_tries,
        reschedule_called,
        order_get_called,
        status_change_called,
        courier_update_called,
        select_picker_called,
        hold_supply_called,
        change_priority_called,
        dispatch_restart,
        assign_reschedule,
        reschedule_counter,
        dispatch_failed,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler('/eats-picker-orders/api/v1/order')
    def mock_order(request):
        assert request.method == 'GET'
        assert request.args['eats_id'] == EATS_ID
        response = order_get_response(EATS_ID, order_status, order_picker, 0)
        return mockserver.make_response(**response)

    @mockserver.json_handler('/eats-picker-orders/api/v1/order/status')
    def mock_status_change(request):
        assert request.method == 'POST'
        assert request.args['eats_id'] == EATS_ID
        status = request.json['status']
        comment = (
            request.json['comment'] if 'comment' in request.json else None
        )
        if dispatch_failed:
            assert status == 'dispatch_failed'
            if estimated_picking_time is None:
                assert (
                    comment
                    == 'Picker Dispatch: No estimated_picking_time in order'
                )
            else:
                assert comment == 'Picker Dispatch: Picker assignation failed'

        return mockserver.make_response(status=200)

    @mockserver.json_handler('/eats-picker-orders/api/v1/order/courier')
    def mock_courier_update(request):
        assert request.args['eats_id'] == EATS_ID
        return make_courier_update_response(mockserver, courier_update_status)

    @mockserver.json_handler('/eats-picker-supply/api/v1/select-picker')
    def mock_select_picker(request):
        return mockserver.make_response(**picker_response)

    @mockserver.json_handler('/eats-picker-supply/api/v1/picker/hold-supply')
    def mock_hold_supply(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_notify_core(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/eats-picker-supply/api/v1/picker/change-priority',
    )
    def mock_change_priority(request):
        return mockserver.make_response(status=200)

    await taxi_eats_picker_dispatch.tests_control(reset_metrics=True)

    await stq_runner.eats_picker_assign.call(
        task_id=EATS_ID,
        kwargs={
            'place_id': PLACE_ID,
            'dispatch_context': {
                'estimated_picking_time': estimated_picking_time,
            },
        },
        exec_tries=exec_tries,
        reschedule_counter=reschedule_counter,
    )

    metric_dispatch_restart = (
        await taxi_eats_picker_dispatch_monitor.get_metric('assign-restart')
    )
    metric_assign_reschedule = (
        await taxi_eats_picker_dispatch_monitor.get_metric('assign-reschedule')
    )
    assert mock_stq_reschedule.times_called == reschedule_called
    assert mock_order.times_called == order_get_called
    assert mock_status_change.times_called == status_change_called
    assert mock_courier_update.times_called == courier_update_called
    assert mock_select_picker.times_called == select_picker_called
    assert mock_hold_supply.times_called == hold_supply_called
    assert mock_change_priority.times_called == change_priority_called
    assert metric_dispatch_restart == dispatch_restart
    assert metric_assign_reschedule == assign_reschedule
    cancel_reasons_expected = {}
    if dispatch_failed:
        cancel_reasons_expected = {
            'PLACE_HAS_NO_PICKER': 0,
            'NO_ESTIMATED_PICKING_TIME': 0,
            'PICKER_FAIL_ASSIGNMENT': 0,
            'PLACE_HAS_TOO_MANY_ORDERS': 0,
            'PLACE_FINISHED_WORK_TIME': 0,
            'PLACE_CLOSES_SOON': 0,
            'UNKNOWN_CANCEL_REASON': 0,
        }
        if not estimated_picking_time:
            cancel_reasons_expected['NO_ESTIMATED_PICKING_TIME'] = 1
        else:
            cancel_reasons_expected['PICKER_FAIL_ASSIGNMENT'] = 1
    dispatch_cancel_reasons = await get_dispatch_cancel_reasons(PLACE_ID)
    assert dispatch_cancel_reasons == cancel_reasons_expected


@pytest.mark.now('2020-10-15T15:00:00Z')
@utils.periodic_dispatcher_config3()
@pytest.mark.config(
    EATS_PICKER_ASSIGN_STQ_SETTINGS={
        'retries': 1,
        'stq_timeout_sec': 1,
        'picker_exclusion_time_sec': 10,
    },
)
async def test_stq_eats_picker_assign_old_schema(
        stq_runner,
        mockserver,
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        get_dispatch_cancel_reasons,
):
    estimated_picking_time = 200

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler('/eats-picker-orders/api/v1/order')
    def mock_order(request):
        assert request.method == 'GET'
        assert request.args['eats_id'] == EATS_ID
        response = order_get_response(EATS_ID, 'dispatching', None, 0)
        return mockserver.make_response(**response)

    @mockserver.json_handler('/eats-picker-orders/api/v1/order/status')
    def mock_status_change(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/eats-picker-orders/api/v1/order/courier')
    def mock_courier_update(request):
        assert request.args['eats_id'] == EATS_ID
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/eats-picker-supply/api/v1/select-picker')
    def mock_select_picker(request):
        return mockserver.make_response(**SELECT_PICKER_RESPONSE)

    @mockserver.json_handler('/eats-picker-supply/api/v1/picker/hold-supply')
    def mock_hold_supply(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_notify_core(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/eats-picker-supply/api/v1/picker/change-priority',
    )
    def mock_change_priority(request):
        return mockserver.make_response(status=200)

    await taxi_eats_picker_dispatch.tests_control(reset_metrics=True)

    await stq_runner.eats_picker_assign.call(
        task_id=EATS_ID,
        kwargs={
            'eats_id': EATS_ID,
            'dispatch_context': {
                'estimated_picking_time': estimated_picking_time,
            },
        },
        exec_tries=0,
        reschedule_counter=0,
    )

    metric_dispatch_restart = (
        await taxi_eats_picker_dispatch_monitor.get_metric('assign-restart')
    )
    metric_assign_reschedule = (
        await taxi_eats_picker_dispatch_monitor.get_metric('assign-reschedule')
    )
    assert mock_stq_reschedule.times_called == 0
    assert mock_order.times_called == 1
    assert mock_status_change.times_called == 1
    assert mock_courier_update.times_called == 1
    assert mock_select_picker.times_called == 1
    assert mock_hold_supply.times_called == 0
    assert mock_change_priority.times_called == 0
    assert metric_dispatch_restart == 0
    assert metric_assign_reschedule == 0
    dispatch_cancel_reasons = await get_dispatch_cancel_reasons(None)
    assert dispatch_cancel_reasons == {
        'PLACE_HAS_NO_PICKER': 0,
        'NO_ESTIMATED_PICKING_TIME': 0,
        'PICKER_FAIL_ASSIGNMENT': 1,
        'PLACE_HAS_TOO_MANY_ORDERS': 0,
        'PLACE_FINISHED_WORK_TIME': 0,
        'PLACE_CLOSES_SOON': 0,
        'UNKNOWN_CANCEL_REASON': 0,
    }
