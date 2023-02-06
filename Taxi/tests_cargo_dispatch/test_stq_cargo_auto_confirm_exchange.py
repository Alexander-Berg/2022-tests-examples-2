import datetime

import pytest


@pytest.fixture(name='mock_waybill_exchange_confirm')
def _mock_driver_push(
        mockserver, read_waybill_info, happy_path_state_performer_found,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/exchange/confirm')
    async def _handler(request):
        response = {
            'result': 'confirmed',
            'new_status': 'delivered',
            'new_route': [],
            'waybill_info': await read_waybill_info(
                request.query['waybill_external_ref'],
            ),
        }
        return response

    return _handler


@pytest.mark.parametrize('already_resolved', [False, True])
async def test_happy_path(
        stq_runner,
        mock_waybill_exchange_confirm,
        read_waybill_info,
        happy_path_claims_segment_db,
        already_resolved,
        waybill_id='waybill_fb_1',
):
    if already_resolved:
        segment = happy_path_claims_segment_db.get_segment('seg1')
        segment.set_point_visit_status('p5', 'visited')

    waybill_info = await read_waybill_info(waybill_id)
    point = waybill_info['execution']['points'][-3]
    assert point['type'] == 'destination'
    assert point['is_resolved'] == already_resolved

    await stq_runner.cargo_waybill_auto_confirm_exchange.call(
        task_id='123',
        kwargs={
            'claim_point_id': point['claim_point_id'],
            'waybill_ref': waybill_id,
            'ticket': 'some_ticket',
            'comment': 'some_comment',
        },
    )

    if already_resolved:
        assert mock_waybill_exchange_confirm.times_called == 0
    else:
        assert mock_waybill_exchange_confirm.times_called == 1
        request = mock_waybill_exchange_confirm.next_call()['request']
        assert request.json == {
            'point_id': point['claim_point_id'],
            'support': {'comment': 'some_comment', 'ticket': 'some_ticket'},
            'async_timer_calculation_supported': False,
        }


@pytest.mark.now('2022-01-01T01:00:00+00:00')
async def test_wait_robocall(
        mockserver,
        stq,
        stq_runner,
        mock_waybill_exchange_confirm,
        happy_path_state_performer_found,
        read_waybill_info,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    waybill_info = await read_waybill_info(waybill_ref)
    cargo_order_id = waybill_info['diagnostics']['order_id']

    @mockserver.json_handler(
        '/cargo-orders/internal/cargo-orders/v1/robocall/state',
    )
    async def mock_robocall_state(request):
        assert request.query['cargo_order_id'] == cargo_order_id
        assert request.query['point_id'] == point['point_id']
        response = {
            'robocall_state_info': {
                'algorithm_state': 'program_is_running',
                'robocall_requested_at': '2022-01-01T01:00:00+00:00',
                'estimated_robocall_program_finish_at': (
                    '2022-01-01T02:00:00+00:00'
                ),
                'estimated_robocall_algorithm_finish_at': (
                    '2022-01-01T03:00:00+00:00'
                ),
            },
        }
        return response

    await stq_runner.cargo_waybill_auto_confirm_exchange.call(
        task_id='123',
        kwargs={
            'claim_point_id': point['claim_point_id'],
            'waybill_ref': waybill_ref,
            'ticket': 'some_ticket',
            'comment': 'some_comment',
        },
    )

    assert mock_robocall_state.times_called == 1
    assert mock_waybill_exchange_confirm.times_called == 0

    assert stq.cargo_waybill_auto_confirm_exchange.times_called == 1
    stq_call = stq.cargo_waybill_auto_confirm_exchange.next_call()
    assert stq_call['id'] == '123'
    assert stq_call['kwargs'] is None  # Reschedule() does not accept kwargs
    # eta == estimated_robocall_algorithm_finish_at
    assert stq_call['eta'] == datetime.datetime(2022, 1, 1, 3, 0, 0)


async def test_robocall_is_finished(
        mockserver,
        stq,
        stq_runner,
        mock_waybill_exchange_confirm,
        happy_path_state_performer_found,
        read_waybill_info,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    waybill_info = await read_waybill_info(waybill_ref)
    cargo_order_id = waybill_info['diagnostics']['order_id']

    @mockserver.json_handler(
        '/cargo-orders/internal/cargo-orders/v1/robocall/state',
    )
    async def mock_robocall_state(request):
        assert request.query['cargo_order_id'] == cargo_order_id
        assert request.query['point_id'] == point['point_id']
        response = {
            'robocall_state_info': {
                'algorithm_state': 'finished',
                'robocall_requested_at': '2022-01-01T01:00:00+00:00',
                'robocall_program_finished_at': '2022-01-01T02:00:00+00:00',
                'estimated_robocall_program_finish_at': (
                    '2022-01-01T02:00:00+00:00'
                ),
                'estimated_robocall_algorithm_finish_at': (
                    '2022-01-01T03:00:00+00:00'
                ),
            },
        }
        return response

    await stq_runner.cargo_waybill_auto_confirm_exchange.call(
        task_id='123',
        kwargs={
            'claim_point_id': point['claim_point_id'],
            'waybill_ref': waybill_ref,
            'ticket': 'some_ticket',
            'comment': 'some_comment',
        },
    )

    assert mock_robocall_state.times_called == 1
    assert mock_waybill_exchange_confirm.times_called == 1
    assert stq.cargo_waybill_auto_confirm_exchange.times_called == 0
