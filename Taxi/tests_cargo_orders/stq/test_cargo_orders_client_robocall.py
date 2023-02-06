import pytest

MOCK_TIME = '2021-10-10T10:00:00+03:00'
CLIENT_PHONE_ID = 'client_personal_phone_id_1'
EATS_ORDER_NR = '000000-000001'
EATS_ROBOCALL_TEMPLATE_CODE = 'robocall_code_1'
EATS_ROBOCALL_TASK_ID = 'robocall_task_id_1'

CLIENT_ROBOCALL_CONFIG = {
    'robocall_template_code': EATS_ROBOCALL_TEMPLATE_CODE,
    'total_timeout_sec': 300,
    'new_calls_timeout_sec': 180,
    'maximal_calls_number': 5,
    'minimal_calls_number_to_cancel_order': 3,
    'delay_between_attempts_sec': 30,
    'delay_between_call_status_checking_sec': 5,
    'delay_after_robocall_error_sec': 5,
    'single_attempt_timeout_sec': 60,
    'maximal_orphan_calls_number': 1,
}

CLIENT_ROBOCALL_CONFIG_DISABLE_CANCEL = {
    'robocall_template_code': EATS_ROBOCALL_TEMPLATE_CODE,
    'total_timeout_sec': 300,
    'new_calls_timeout_sec': 180,
    'maximal_calls_number': 5,
    'minimal_calls_number_to_cancel_order': 6,  # > maximal_calls_number
    'delay_between_attempts_sec': 30,
    'delay_between_call_status_checking_sec': 5,
    'delay_after_robocall_error_sec': 5,
    'single_attempt_timeout_sec': 60,
    'maximal_orphan_calls_number': 1,
}
MARK_ROBOCALL_CONFIG_DISABLE_CANCEL = pytest.mark.config(
    CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG_DISABLE_CANCEL,
)

EXP_CANCEL_AFTER_ROBOCALL = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_orders_cancel_after_robocall',
    consumers=['cargo-orders/cancel-after-robocall'],
    clauses=[],
    default_value={
        'eats_core_cancel': {
            'enabled': True,
            'config': {'reason_code': 'reason_code_1'},
        },
    },
)


@pytest.fixture(name='mock_eats_core_cancel')
def _mock_eats_core_cancel(mockserver):
    @mockserver.json_handler(
        '/eats-core-cancel-order/internal-api/v1/cancel-order',
    )
    def mock(request):
        return mockserver.make_response(
            status=200, json={'is_cancelled': True},
        )

    return mock


def prepare_robocall_attempts(
        prepare_robocall_attempt,
        num_attempts,
        order_id,
        point_id,
        resolution,
        eats_core_robocall_data=None,
):
    for attempt_id in range(num_attempts):
        prepare_robocall_attempt(
            order_id,
            point_id,
            attempt_id,
            eats_core_robocall_data=eats_core_robocall_data,
            resolution=resolution,
        )


@pytest.mark.now(MOCK_TIME)
@pytest.mark.config(CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG)
@EXP_CANCEL_AFTER_ROBOCALL
@pytest.mark.pgsql('cargo_orders', files=['pg_cargo_orders.sql'])
@pytest.mark.parametrize(
    """
    num_unanswered_calls, expected_db_resolution, expected_calls_to_cancel,
    expected_calls_to_state_update
    """,
    [
        (
            3,  # >= minimal_calls_number_to_cancel_order
            'order_cancelled',
            1,
            0,
        ),
        (
            2,  # < minimal_calls_number_to_cancel_order
            'finished_by_timeout',
            0,
            1,
        ),
    ],
)
async def test_total_timeout(
        stq_runner,
        stq,
        mock_eats_core_cancel,
        my_waybill_info,
        default_order_id,
        prepare_order_client_robocall,
        fetch_order_client_robocall,
        prepare_robocall_attempt,
        num_unanswered_calls,
        expected_db_resolution,
        expected_calls_to_cancel,
        expected_calls_to_state_update,
):
    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = EATS_ORDER_NR

    point_id = my_waybill_info['execution']['points'][0]['point_id']

    prepare_order_client_robocall(
        default_order_id,
        point_id,
        status='calling',
        created_ts='2021-10-10T09:54:59+03:00',  # older than total_timeout_sec
    )
    prepare_robocall_attempts(
        prepare_robocall_attempt,
        num_unanswered_calls,
        default_order_id,
        point_id,
        resolution='no_answer',
    )

    await stq_runner.cargo_orders_client_robocall.call(
        task_id='task_id_1',
        kwargs={'cargo_order_id': default_order_id, 'point_id': point_id},
    )

    order_client_robocall = fetch_order_client_robocall(
        default_order_id, point_id,
    )
    assert order_client_robocall.status == 'finished'
    assert order_client_robocall.resolution == expected_db_resolution

    assert stq.cargo_orders_client_robocall.times_called == 0
    assert mock_eats_core_cancel.times_called == expected_calls_to_cancel
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called
        == expected_calls_to_state_update
    )


@pytest.mark.now(MOCK_TIME)
@pytest.mark.config(CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG)
@pytest.mark.pgsql('cargo_orders', files=['pg_cargo_orders.sql'])
@pytest.mark.parametrize(
    'num_unanswered_calls',
    [
        3,  # >= minimal_calls_number_to_cancel_order
        2,  # < minimal_calls_number_to_cancel_order
    ],
)
async def test_new_calls_timeout(
        stq_runner,
        stq,
        my_waybill_info,
        default_order_id,
        prepare_order_client_robocall,
        fetch_order_client_robocall,
        prepare_robocall_attempt,
        num_unanswered_calls,
):
    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = EATS_ORDER_NR

    point_id = my_waybill_info['execution']['points'][0]['point_id']

    prepare_order_client_robocall(
        default_order_id,
        point_id,
        status='calling',
        # older than new_calls_timeout_sec
        created_ts='2021-10-10T09:56:59+03:00',
    )
    prepare_robocall_attempts(
        prepare_robocall_attempt,
        num_unanswered_calls,
        default_order_id,
        point_id,
        resolution='no_answer',
    )

    await stq_runner.cargo_orders_client_robocall.call(
        task_id='task_id_1',
        kwargs={'cargo_order_id': default_order_id, 'point_id': point_id},
    )

    order_client_robocall = fetch_order_client_robocall(
        default_order_id, point_id,
    )
    # It is not finished until the total timeout is reached.
    assert order_client_robocall.status == 'calling'

    assert stq.cargo_orders_client_robocall.times_called == 1


@pytest.mark.now(MOCK_TIME)
@pytest.mark.config(CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG)
@pytest.mark.pgsql('cargo_orders', files=['pg_cargo_orders.sql'])
@pytest.mark.parametrize(
    """
    robocall_created_ts, promise_max_at,
    expected_db_status, expected_db_resolution, expected_stq_reschedule,
    expected_calls_robocall
    """,
    [
        # now = '2021-10-10T10:00:00+03:00'
        # now - total_timeout_sec = '2021-10-10T09:55:00+03:00'
        # now - new_calls_timeout_sec = '2021-10-10T09:57:00+03:00'
        # promise_max_at is not reached
        (
            '2021-10-10T09:54:59+03:00',  # older than total_timeout_sec
            '2021-10-10T10:00:01+03:00',
            'calling',
            None,
            1,
            1,
        ),
        (
            '2021-10-10T09:55:01+03:00',  # newer than total_timeout_sec
            '2021-10-10T10:00:01+03:00',
            'calling',
            None,
            1,
            1,
        ),
        (
            '2021-10-10T09:56:59+03:00',  # older than new_calls_timeout_sec
            '2021-10-10T10:00:01+03:00',
            'calling',
            None,
            1,
            1,
        ),
        (
            '2021-10-10T09:57:01+03:00',  # newer than new_calls_timeout_sec
            '2021-10-10T10:00:01+03:00',
            'calling',
            None,
            1,
            1,
        ),
        # promise_max_at is reached
        (
            '2021-10-10T09:54:59+03:00',  # older than total_timeout_sec
            '2021-10-10T09:59:59+03:00',
            'finished',
            'finished_by_timeout',
            0,
            0,
        ),
        (
            '2021-10-10T09:55:01+03:00',  # newer than total_timeout_sec
            '2021-10-10T09:59:59+03:00',
            'calling',
            None,
            1,
            0,
        ),
        (
            '2021-10-10T09:56:59+03:00',  # older than new_calls_timeout_sec
            '2021-10-10T09:59:59+03:00',
            'calling',
            None,
            1,
            0,
        ),
        (
            '2021-10-10T09:57:01+03:00',  # newer than new_calls_timeout_sec
            '2021-10-10T09:59:59+03:00',
            'calling',
            None,
            1,
            1,
        ),
        # promise_max_at is not specified
        (
            '2021-10-10T09:54:59+03:00',  # older than total_timeout_sec
            None,
            'finished',
            'finished_by_timeout',
            0,
            0,
        ),
        (
            '2021-10-10T09:55:01+03:00',  # newer than total_timeout_sec
            None,
            'calling',
            None,
            1,
            0,
        ),
        (
            '2021-10-10T09:56:59+03:00',  # older than new_calls_timeout_sec
            None,
            'calling',
            None,
            1,
            0,
        ),
        (
            '2021-10-10T09:57:01+03:00',  # newer than new_calls_timeout_sec
            None,
            'calling',
            None,
            1,
            1,
        ),
    ],
)
async def test_timeout_with_promise(
        mockserver,
        stq_runner,
        stq,
        my_waybill_info,
        default_order_id,
        prepare_order_client_robocall,
        fetch_order_client_robocall,
        robocall_created_ts,
        promise_max_at,
        expected_db_status,
        expected_db_resolution,
        expected_stq_reschedule,
        expected_calls_robocall,
):
    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = EATS_ORDER_NR
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'promise_min_at': '2021-10-10T10:00:00+03:00',  # any time in the past
        'promise_max_at': promise_max_at,
    }

    point_id = my_waybill_info['execution']['points'][0]['point_id']

    prepare_order_client_robocall(
        default_order_id,
        point_id,
        status='calling',
        created_ts=robocall_created_ts,
    )

    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/robocall',
    )
    def mock_robocall(request):
        return mockserver.make_response(
            status=200, json={'task_id': EATS_ROBOCALL_TASK_ID},
        )

    await stq_runner.cargo_orders_client_robocall.call(
        task_id='task_id_1',
        kwargs={'cargo_order_id': default_order_id, 'point_id': point_id},
    )

    order_client_robocall = fetch_order_client_robocall(
        default_order_id, point_id,
    )
    assert order_client_robocall.status == expected_db_status
    assert order_client_robocall.resolution == expected_db_resolution

    assert (
        stq.cargo_orders_client_robocall.times_called
        == expected_stq_reschedule
    )
    assert mock_robocall.times_called == expected_calls_robocall


@pytest.mark.now(MOCK_TIME)  # Before new_calls_timeout_sec.
@pytest.mark.config(CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG)
@pytest.mark.pgsql('cargo_orders', files=['pg_cargo_orders.sql'])
@pytest.mark.parametrize(
    """
    robocall_response_status, robocall_response_body, expected_db_status,
    expected_db_resolution, expected_db_eats_core_data,
     expected_stq_reschedule, expected_calls_to_state_update
    """,
    [
        (500, None, 'calling', None, None, 1, 0),
        (
            400,
            {'code': 'invalid_parameter', 'message': 'invalid parameter'},
            'finished',
            'finished_by_error',
            None,
            0,
            1,
        ),
        (
            404,
            {'code': 'not_found', 'message': 'not found'},
            'finished',
            'finished_by_error',
            None,
            0,
            1,
        ),
        (
            200,
            {'task_id': EATS_ROBOCALL_TASK_ID},
            'calling',
            None,
            {'task_id': EATS_ROBOCALL_TASK_ID},
            1,
            0,
        ),
    ],
)
async def test_start_robocall(
        mockserver,
        my_waybill_info,
        default_order_id,
        stq_runner,
        stq,
        prepare_order_client_robocall,
        fetch_order_client_robocall,
        fetch_robocall_attempt,
        robocall_response_status,
        robocall_response_body,
        expected_db_status,
        expected_db_resolution,
        expected_db_eats_core_data,
        expected_stq_reschedule,
        expected_calls_to_state_update,
):
    point_id = my_waybill_info['execution']['points'][0]['point_id']

    prepare_order_client_robocall(default_order_id, point_id, status='calling')

    my_waybill_info['segments'][0]['points'][0]['contact'][
        'personal_phone_id'
    ] = CLIENT_PHONE_ID

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = EATS_ORDER_NR

    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/robocall',
    )
    def _mock_robocall(request):
        assert request.json['order_nr'] == EATS_ORDER_NR
        assert request.json['personal_phone_id'] == CLIENT_PHONE_ID
        assert (
            request.json['robocall_template_code']
            == EATS_ROBOCALL_TEMPLATE_CODE
        )
        return mockserver.make_response(
            status=robocall_response_status, json=robocall_response_body,
        )

    await stq_runner.cargo_orders_client_robocall.call(
        task_id='task_id_1',
        kwargs={'cargo_order_id': default_order_id, 'point_id': point_id},
    )

    order_client_robocall = fetch_order_client_robocall(
        default_order_id, point_id,
    )
    assert order_client_robocall.status == expected_db_status
    assert order_client_robocall.resolution == expected_db_resolution

    if expected_db_eats_core_data is not None:
        robocall_attempt = fetch_robocall_attempt(
            default_order_id, point_id, 0,
        )
        assert (
            robocall_attempt.eats_core_robocall_data
            == expected_db_eats_core_data
        )

    assert (
        stq.cargo_orders_client_robocall.times_called
        == expected_stq_reschedule
    )
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called
        == expected_calls_to_state_update
    )


@pytest.mark.now(MOCK_TIME)  # Before new_calls_timeout_sec.
@pytest.mark.config(CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG)
@pytest.mark.pgsql('cargo_orders', files=['pg_cargo_orders.sql'])
async def test_robocall_changed_order(
        my_waybill_info,
        default_order_id,
        stq_runner,
        stq,
        prepare_order_client_robocall,
        fetch_order_client_robocall,
):
    point_id = my_waybill_info['execution']['points'][0]['point_id']

    prepare_order_client_robocall(default_order_id, point_id, status='calling')

    my_waybill_info['segments'][0]['points'][0]['contact'][
        'personal_phone_id'
    ] = CLIENT_PHONE_ID

    my_waybill_info['execution']['segments'][0]['status'] = 'delivered_finish'
    my_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = EATS_ORDER_NR

    await stq_runner.cargo_orders_client_robocall.call(
        task_id='task_id_1',
        kwargs={'cargo_order_id': default_order_id, 'point_id': point_id},
    )

    order_client_robocall = fetch_order_client_robocall(
        default_order_id, point_id,
    )
    assert order_client_robocall.status == 'finished'
    assert order_client_robocall.resolution == 'aborted_by_changed_order'

    assert stq.cargo_orders_client_robocall.times_called == 0
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )


@pytest.mark.now(MOCK_TIME)  # Before new_calls_timeout_sec.
@pytest.mark.config(CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG)
@pytest.mark.pgsql('cargo_orders', files=['pg_cargo_orders.sql'])
@pytest.mark.parametrize(
    """
    robocall_response_status, robocall_response_body, expected_db_status,
    expected_db_resolution, expected_db_attempt_resolution,
    expected_stq_reschedule, expected_calls_to_state_update
    """,
    [
        (500, None, 'calling', None, None, 1, 0),
        (
            400,
            {'code': 'invalid_parameter', 'message': 'invalid parameter'},
            'calling',
            None,
            'error',
            1,
            0,
        ),
        (
            404,
            {'code': 'not_found', 'message': 'not found'},
            'calling',
            None,
            'error',
            1,
            0,
        ),
        (200, {'task_status': 'pending'}, 'calling', None, None, 1, 0),
        (200, {'task_status': 'in_progress'}, 'calling', None, None, 1, 0),
        (
            200,
            {'task_status': 'partially_complete'},
            'finished',
            'client_answered',
            'answer',
            0,
            1,
        ),
        (
            200,
            {'task_status': 'fully_complete'},
            'finished',
            'client_answered',
            'answer',
            0,
            1,
        ),
        (200, {'task_status': 'error'}, 'calling', None, 'error', 1, 0),
        (
            200,
            {'task_status': 'recoverable_error'},
            'calling',
            None,
            'error',
            1,
            0,
        ),
        (200, {'task_status': 'cancelled'}, 'calling', None, 'error', 1, 0),
        # robocall task statuses 'no_answer' and 'auto_responder' are tested in
        # test_robocall_is_unanswered
    ],
)
async def test_robocall_is_calling(
        mockserver,
        stq_runner,
        stq,
        my_waybill_info,
        default_order_id,
        prepare_order_client_robocall,
        fetch_order_client_robocall,
        prepare_robocall_attempt,
        fetch_robocall_attempt,
        robocall_response_status,
        robocall_response_body,
        expected_db_status,
        expected_db_resolution,
        expected_db_attempt_resolution,
        expected_stq_reschedule,
        expected_calls_to_state_update,
):
    attempt_id = 0

    point_id = my_waybill_info['execution']['points'][0]['point_id']

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'

    prepare_order_client_robocall(default_order_id, point_id, status='calling')
    prepare_robocall_attempt(
        default_order_id,
        point_id,
        attempt_id,
        eats_core_robocall_data=f'{{"task_id": "{EATS_ROBOCALL_TASK_ID}"}}',
    )

    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/'
        + 'robocall-status',
    )
    def _mock_robocall_status(request):
        assert request.args['task_id'] == EATS_ROBOCALL_TASK_ID
        return mockserver.make_response(
            status=robocall_response_status, json=robocall_response_body,
        )

    await stq_runner.cargo_orders_client_robocall.call(
        task_id='task_id_1',
        kwargs={'cargo_order_id': default_order_id, 'point_id': point_id},
    )

    order_client_robocall = fetch_order_client_robocall(
        default_order_id, point_id,
    )
    assert order_client_robocall.status == expected_db_status
    assert order_client_robocall.resolution == expected_db_resolution

    robocall_attempt = fetch_robocall_attempt(
        default_order_id, point_id, attempt_id,
    )
    assert robocall_attempt.eats_core_robocall_data == {
        'task_id': EATS_ROBOCALL_TASK_ID,
    }
    assert robocall_attempt.resolution == expected_db_attempt_resolution

    assert (
        stq.cargo_orders_client_robocall.times_called
        == expected_stq_reschedule
    )
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called
        == expected_calls_to_state_update
    )


@pytest.mark.now(MOCK_TIME)
@pytest.mark.config(CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG)
@pytest.mark.pgsql('cargo_orders', files=['pg_cargo_orders.sql'])
async def test_robocall_orphan_call(
        mockserver,
        stq_runner,
        stq,
        my_waybill_info,
        default_order_id,
        prepare_order_client_robocall,
        fetch_order_client_robocall,
        prepare_robocall_attempt,
        fetch_robocall_attempt,
):
    attempt_id = 0

    point_id = my_waybill_info['execution']['points'][0]['point_id']

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'

    prepare_order_client_robocall(default_order_id, point_id, status='calling')
    prepare_robocall_attempt(
        default_order_id,
        point_id,
        attempt_id,
        eats_core_robocall_data=f'{{"task_id": "{EATS_ROBOCALL_TASK_ID}"}}',
        # single_attempt_timeout_sec = 60 seconds
        # MOCK_TIME = '2021-10-10T10:00:00+03:00'
        created_ts='2021-10-10T09:59:00+03:00',
        updated_ts='2021-10-10T09:59:00+03:00',
    )

    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/'
        + 'robocall-status',
    )
    def _mock_robocall_status(request):
        assert request.args['task_id'] == EATS_ROBOCALL_TASK_ID
        return mockserver.make_response(
            status=200, json={'task_status': 'in_progress'},
        )

    await stq_runner.cargo_orders_client_robocall.call(
        task_id='task_id_1',
        kwargs={'cargo_order_id': default_order_id, 'point_id': point_id},
    )

    order_client_robocall = fetch_order_client_robocall(
        default_order_id, point_id,
    )
    assert order_client_robocall.status == 'finished'
    assert order_client_robocall.resolution == 'finished_by_error'

    robocall_attempt = fetch_robocall_attempt(
        default_order_id, point_id, attempt_id,
    )
    assert robocall_attempt.eats_core_robocall_data == {
        'task_id': EATS_ROBOCALL_TASK_ID,
    }
    assert robocall_attempt.resolution == 'orphan'

    assert stq.cargo_orders_client_robocall.times_called == 0
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )


@pytest.mark.now(MOCK_TIME)
@pytest.mark.config(CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG)
@EXP_CANCEL_AFTER_ROBOCALL
@pytest.mark.pgsql('cargo_orders', files=['pg_cargo_orders.sql'])
@pytest.mark.parametrize(
    'robocall_response_body, expected_db_attempt_resolution',
    [
        pytest.param(
            {'task_status': 'no_answer'}, 'no_answer', id='no_answer',
        ),
        pytest.param(
            {'task_status': 'auto_responder'},
            'auto_responder',
            id='auto_responder',
        ),
    ],
)
@pytest.mark.parametrize(
    """
    num_unanswered_calls, created_ts, expected_db_status,
    expected_db_resolution, expected_stq_reschedule, expected_calls_to_cancel,
    expected_calls_to_state_update
    """,
    [
        pytest.param(
            # +1 >= maximal_calls_number
            #    >= minimal_calls_number_to_cancel_order
            4,
            MOCK_TIME,
            'finished',
            'order_cancelled',
            0,
            1,
            0,
            id='attempts limit, cancelled',
        ),
        pytest.param(
            # +1 >= maximal_calls_number
            #    < minimal_calls_number_to_cancel_order
            4,
            MOCK_TIME,
            'finished',
            'finished_by_attempts_limit',
            0,
            0,
            1,
            marks=MARK_ROBOCALL_CONFIG_DISABLE_CANCEL,
            id='attempts limit, not cancelled',
        ),
        pytest.param(
            3,  # +1 < maximal_calls_number
            MOCK_TIME,
            'calling',
            None,
            1,
            0,
            0,
            id='next attempt',
        ),
        pytest.param(
            # +1 < maximal_calls_number
            #    >= minimal_calls_number_to_cancel_order
            2,
            # older than (new_calls_timeout_sec - delay_between_attempts_sec)
            '2021-10-10T09:57:29+03:00',
            'finished',
            'order_cancelled',
            0,
            1,
            0,
            id='timeout, cancelled',
        ),
        pytest.param(
            # +1 < maximal_calls_number
            #    < minimal_calls_number_to_cancel_order
            1,
            # older than (new_calls_timeout_sec - delay_between_attempts_sec)
            '2021-10-10T09:57:29+03:00',
            'finished',
            'finished_by_timeout',
            0,
            0,
            1,
            id='timeout, not cancelled',
        ),
    ],
)
async def test_robocall_is_unanswered(
        mockserver,
        stq_runner,
        stq,
        mock_eats_core_cancel,
        my_waybill_info,
        default_order_id,
        prepare_order_client_robocall,
        fetch_order_client_robocall,
        prepare_robocall_attempt,
        fetch_robocall_attempt,
        robocall_response_body,
        expected_db_attempt_resolution,
        num_unanswered_calls,
        created_ts,
        expected_db_status,
        expected_db_resolution,
        expected_stq_reschedule,
        expected_calls_to_cancel,
        expected_calls_to_state_update,
):
    latest_attempt_id = num_unanswered_calls

    point_id = my_waybill_info['execution']['points'][0]['point_id']

    my_waybill_info['segments'][0]['points'][0]['contact'][
        'personal_phone_id'
    ] = CLIENT_PHONE_ID

    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = EATS_ORDER_NR

    prepare_order_client_robocall(
        default_order_id, point_id, status='calling', created_ts=created_ts,
    )
    prepare_robocall_attempts(
        prepare_robocall_attempt,
        num_unanswered_calls,
        default_order_id,
        point_id,
        resolution='no_answer',
    )
    prepare_robocall_attempt(
        default_order_id,
        point_id,
        latest_attempt_id,
        eats_core_robocall_data=f'{{"task_id": "{EATS_ROBOCALL_TASK_ID}"}}',
    )

    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/'
        + 'robocall-status',
    )
    def _mock_robocall_status(request):
        assert request.args['task_id'] == EATS_ROBOCALL_TASK_ID
        return mockserver.make_response(
            status=200, json=robocall_response_body,
        )

    await stq_runner.cargo_orders_client_robocall.call(
        task_id='task_id_1',
        kwargs={'cargo_order_id': default_order_id, 'point_id': point_id},
    )

    order_client_robocall = fetch_order_client_robocall(
        default_order_id, point_id,
    )
    assert order_client_robocall.status == expected_db_status
    assert order_client_robocall.resolution == expected_db_resolution

    robocall_attempt = fetch_robocall_attempt(
        default_order_id, point_id, latest_attempt_id,
    )
    assert robocall_attempt.resolution == expected_db_attempt_resolution

    assert (
        stq.cargo_orders_client_robocall.times_called
        == expected_stq_reschedule
    )
    assert mock_eats_core_cancel.times_called == expected_calls_to_cancel
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called
        == expected_calls_to_state_update
    )


@pytest.mark.now(MOCK_TIME)
@pytest.mark.config(CARGO_ORDERS_EATS_CORE_ROBOCALL=CLIENT_ROBOCALL_CONFIG)
@pytest.mark.pgsql('cargo_orders', files=['pg_cargo_orders.sql'])
async def test_cancel_is_disabled(
        stq_runner,
        stq,
        mock_eats_core_cancel,
        my_waybill_info,
        default_order_id,
        prepare_order_client_robocall,
        fetch_order_client_robocall,
        prepare_robocall_attempt,
):
    my_waybill_info['execution']['segments'][0]['status'] = 'delivery_arrived'
    my_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = EATS_ORDER_NR

    point_id = my_waybill_info['execution']['points'][0]['point_id']

    prepare_order_client_robocall(
        default_order_id,
        point_id,
        status='calling',
        created_ts='2021-10-10T09:54:59+03:00',  # older than total_timeout_sec
    )
    prepare_robocall_attempts(
        prepare_robocall_attempt,
        3,  # num_unanswered_calls >= minimal_calls_number_to_cancel_order
        default_order_id,
        point_id,
        resolution='no_answer',
    )

    await stq_runner.cargo_orders_client_robocall.call(
        task_id='task_id_1',
        kwargs={'cargo_order_id': default_order_id, 'point_id': point_id},
    )

    order_client_robocall = fetch_order_client_robocall(
        default_order_id, point_id,
    )
    assert order_client_robocall.status == 'finished'
    assert order_client_robocall.resolution == 'finished_by_timeout'

    assert stq.cargo_orders_client_robocall.times_called == 0
    assert mock_eats_core_cancel.times_called == 0
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )
