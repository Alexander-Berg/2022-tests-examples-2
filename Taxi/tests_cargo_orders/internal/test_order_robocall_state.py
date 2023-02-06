import pytest

CLIENT_ROBOCALL_CONFIG = {
    'robocall_template_code': 'robocall_task_id_1',
    'total_timeout_sec': 300,
    'new_calls_timeout_sec': 180,
    'maximal_calls_number': 5,
    'minimal_calls_number_to_cancel_order': 3,
    'delay_between_attempts_sec': 30,
    'delay_between_call_status_checking_sec': 5,
    'delay_after_robocall_error_sec': 5,
    'timeouts_after_robocall': {
        'timeout_if_client_answered_sec': 1200,
        'timeout_if_order_cancelled_sec': 30,
        'timeout_if_not_answered_not_cancelled_sec': 600,
    },
}


@pytest.mark.config(CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG)
@pytest.mark.parametrize(
    'promise_max_at, estimated_finish_ts',
    [
        # promise_max_at is before end of total_timeout_sec.
        ('2021-10-10T10:04:59+00:00', '2021-10-10T10:05:00+00:00'),
        # promise_max_at is after end of total_timeout_sec.
        ('2021-10-10T10:05:01+00:00', '2021-10-10T10:05:01+00:00'),
    ],
)
async def test_robocall_calling(
        taxi_cargo_orders,
        my_waybill_info,
        default_order_id,
        prepare_order_client_robocall,
        promise_max_at,
        estimated_finish_ts,
):
    point_id = my_waybill_info['execution']['points'][0]['point_id']
    claim_id = 'test_claim_id_1'
    created_ts = '2021-10-10T10:00:00+00:00'
    updated_ts = '2021-10-10T10:10:00+00:00'

    prepare_order_client_robocall(
        default_order_id,
        point_id,
        claim_id=claim_id,
        reason='client_not_responding',
        status='calling',
        created_ts=created_ts,
        updated_ts=updated_ts,
    )

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': '2021-10-10T10:00:00+03:00',  # any time in the past
        'promise_max_at': promise_max_at,
    }

    response = await taxi_cargo_orders.get(
        'internal/cargo-orders/v1/robocall/state'
        + f'?cargo_order_id={default_order_id}&point_id={point_id}',
    )
    assert response.status_code == 200
    assert response.json() == {
        'robocall_state_info': {
            'algorithm_state': 'program_is_running',
            'robocall_requested_at': created_ts,
            'estimated_robocall_program_finish_at': estimated_finish_ts,
            'estimated_robocall_algorithm_finish_at': estimated_finish_ts,
        },
    }


@pytest.mark.config(CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG)
@pytest.mark.parametrize(
    'resolution, expected_finish_time',
    [
        # updated_ts + timeout_if_client_answered_sec
        ('client_answered', '2021-10-10T10:30:00+00:00'),
        # updated_ts + timeout_if_order_cancelled_sec
        ('order_cancelled', '2021-10-10T10:10:30+00:00'),
        # updated_ts + timeout_if_not_answered_not_cancelled_sec
        ('finished_by_attempts_limit', '2021-10-10T10:20:00+00:00'),
        ('finished_by_timeout', '2021-10-10T10:20:00+00:00'),
        ('finished_by_error', '2021-10-10T10:20:00+00:00'),
        ('disabled_by_experiment', '2021-10-10T10:20:00+00:00'),
        # updated_ts
        ('aborted_by_changed_order', '2021-10-10T10:10:00+00:00'),
    ],
)
async def test_robocall_finished(
        taxi_cargo_orders,
        prepare_order_client_robocall,
        resolution,
        expected_finish_time,
):
    order_id = '9db1622e-582d-4091-b6fc-4cb2ffdc12c0'
    point_id = 'point_id_1'
    claim_id = 'test_claim_id_1'
    created_ts = '2021-10-10T10:00:00+00:00'
    updated_ts = '2021-10-10T10:10:00+00:00'

    prepare_order_client_robocall(
        order_id,
        point_id,
        claim_id=claim_id,
        reason='client_not_responding',
        status='finished',
        resolution=resolution,
        created_ts=created_ts,
        updated_ts=updated_ts,
    )

    response = await taxi_cargo_orders.get(
        'internal/cargo-orders/v1/robocall/state'
        + f'?cargo_order_id={order_id}&point_id={point_id}',
    )
    assert response.status_code == 200
    assert response.json() == {
        'robocall_state_info': {
            'algorithm_state': 'finished',
            'robocall_requested_at': created_ts,
            'robocall_program_finished_at': updated_ts,
            'estimated_robocall_program_finish_at': updated_ts,
            'estimated_robocall_algorithm_finish_at': expected_finish_time,
        },
    }


async def test_robocall_not_found(taxi_cargo_orders):
    order_id = '9db1622e-582d-4091-b6fc-4cb2ffdc12c0'
    point_id = 'point_id_1'

    response = await taxi_cargo_orders.get(
        'internal/cargo-orders/v1/robocall/state'
        + f'?cargo_order_id={order_id}&point_id={point_id}',
    )
    assert response.status_code == 200
    assert response.json() == {}
