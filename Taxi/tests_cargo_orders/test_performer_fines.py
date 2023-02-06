import pytest


TAXI_ORDER_ID_1 = '7f06810c84b11f0e976805fbf6c4408e'
DBID_UUID_1 = (
    '4aa0b77ad317440aaa2b5c13a5868151_2a12ca336ec5c7d6f1b10e4b8668bf14'
)
CARGO_CANCEL_REASON_1 = 'order_cancel_reason_Pro_so_far'
ROBOT_YANDEX_UID_STR = '1111'
ROBOT_YANDEX_LOGIN = 'login'
PERFORMER_FINES_API_KEY = 'OAuth performer-fines-api-key'


@pytest.fixture(name='mock_job_settings')
async def _mock_job_settings(taxi_cargo_orders, taxi_config):
    taxi_config.set(
        CARGO_ORDERS_PERFORMER_FINES_SETTINGS={
            'enabled': True,
            'yt_table_path': '//home/testsuite/cargo_orders_performer_fines',
            'job_awake_hour': 10,
            'job_iteration_pause_ms': 0,
            'execute_fine_sleep_ms': 0,
            'rate_limit': {'limit': 1000, 'interval': 1, 'burst': 0},
            'force_execute': False,
        },
    )
    await taxi_cargo_orders.invalidate_caches()


@pytest.fixture(name='mock_stq_settings')
async def _mock_stq_settings(taxi_cargo_orders, taxi_config):
    taxi_config.set(
        CARGO_ORDERS_PERFORMER_FINES_STQ_SETTINGS={
            'enabled': True,
            'reschedule_delay_ms': 1000,
            'reschedule_count': -1,
            'robot_yandex_login': ROBOT_YANDEX_LOGIN,
            'robot_yandex_uid': int(ROBOT_YANDEX_UID_STR),
        },
    )
    await taxi_cargo_orders.invalidate_caches()


@pytest.fixture(name='mock_stq_settings_with_reschedule')
async def _mock_stq_settings_with_reschedule(taxi_cargo_orders, taxi_config):
    taxi_config.set(
        CARGO_ORDERS_PERFORMER_FINES_STQ_SETTINGS={
            'enabled': True,
            'reschedule_delay_ms': 1000,
            'reschedule_count': 1,
            'robot_yandex_login': ROBOT_YANDEX_LOGIN,
            'robot_yandex_uid': int(ROBOT_YANDEX_UID_STR),
        },
    )
    await taxi_cargo_orders.invalidate_caches()


@pytest.fixture(name='mock_stq_settings_with_ticket_and_comment')
async def _mock_stq_settings_with_ticket_and_comment(
        taxi_cargo_orders, taxi_config,
):
    taxi_config.set(
        CARGO_ORDERS_PERFORMER_FINES_STQ_SETTINGS={
            'enabled': True,
            'reschedule_delay_ms': 1000,
            'reschedule_count': -1,
            'robot_yandex_login': ROBOT_YANDEX_LOGIN,
            'robot_yandex_uid': int(ROBOT_YANDEX_UID_STR),
            'st_ticket_stub': 'TICKET',
            'automated_fine_comment': 'COMMENT',
        },
    )
    await taxi_cargo_orders.invalidate_caches()


@pytest.fixture(name='mock_mapping_cancel_reason_to_fine_code')
async def _mock_mapping_cancel_reason_to_fine_code(
        taxi_cargo_orders, experiments3,
):
    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_orders_order_cancel_performer_reason_to_fine_code',
        consumers=['cargo-orders/order-cancel-performer-reason-to-fine-code'],
        clauses=[],
        default_value={'enabled': True, 'fine_code': 'cancel_after_confirm'},
    )
    await taxi_cargo_orders.invalidate_caches()


@pytest.mark.yt(static_table_data=['yt_performer_fines.yaml'])
async def test_performers_bulk_info(
        taxi_cargo_orders,
        taxi_config,
        yt_apply,
        stq,
        mock_job_settings,
        mock_stq_settings,
        testpoint,
        yt_rows_count=3,
):
    @testpoint('cargo-orders-performer-fines::result')
    def _testpoint_job_result_callback(data):
        assert data['stats']['yt']['read-rows-count'] == yt_rows_count
        assert data['stats']['fines']['set-execute-fine-stq-failed'] == 0

    await taxi_cargo_orders.run_task('cargo-orders-performer-fines')

    assert stq.cargo_orders_performer_fines.times_called == yt_rows_count


@pytest.mark.yt(static_table_data=['yt_performer_fines.yaml'])
async def test_performers_fines_job_three_iteration(
        taxi_cargo_orders,
        taxi_config,
        yt_apply,
        stq,
        mock_stq_settings,
        testpoint,
        yt_rows_count=3,
):
    taxi_config.set(
        CARGO_ORDERS_PERFORMER_FINES_SETTINGS={
            'enabled': True,
            'yt_table_path': '//home/testsuite/cargo_orders_performer_fines',
            'job_awake_hour': 10,
            'job_iteration_pause_ms': 0,
            'execute_fine_sleep_ms': 0,
            'rate_limit': {'limit': 1, 'interval': 1, 'burst': 0},
            'force_execute': True,
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    @testpoint('cargo-orders-performer-fines::result')
    def _testpoint_job_result_callback(data):
        assert data['stats']['yt']['read-rows-count'] == 1
        assert data['stats']['fines']['set-execute-fine-stq-failed'] == 0

    await taxi_cargo_orders.run_task('cargo-orders-performer-fines')
    assert stq.cargo_orders_performer_fines.times_called == 1
    await taxi_cargo_orders.run_task('cargo-orders-performer-fines')
    assert stq.cargo_orders_performer_fines.times_called == 2
    await taxi_cargo_orders.run_task('cargo-orders-performer-fines')
    assert stq.cargo_orders_performer_fines.times_called == 3


@pytest.mark.yt(static_table_data=['yt_performer_fines.yaml'])
async def test_performer_fines_stq_input_data(
        taxi_cargo_orders,
        yt_apply,
        stq,
        mock_job_settings,
        mock_stq_settings,
        mock_mapping_cancel_reason_to_fine_code,
        yt_rows_count=3,
):
    await taxi_cargo_orders.run_task('cargo-orders-performer-fines')

    assert stq.cargo_orders_performer_fines.times_called == yt_rows_count
    stq_call = stq.cargo_orders_performer_fines.next_call()
    assert (
        stq_call['id'] == f'cargo_orders_performer_fines_'
        f'{TAXI_ORDER_ID_1}_{DBID_UUID_1}_{CARGO_CANCEL_REASON_1}'
    )

    kwargs = stq_call['kwargs']
    assert kwargs['taxi_order_id'] == TAXI_ORDER_ID_1
    assert kwargs['dbid_uuid'] == DBID_UUID_1
    assert kwargs['cargo_cancel_reason'] == CARGO_CANCEL_REASON_1


@pytest.mark.yt(static_table_data=['yt_performer_fines.yaml'])
async def test_performer_fines_stq_happy_path(
        taxi_cargo_orders,
        mockserver,
        yt_apply,
        stq,
        stq_runner,
        mock_job_settings,
        mock_stq_settings,
        mock_mapping_cancel_reason_to_fine_code,
):
    @mockserver.json_handler(
        '/order-fines-via-abk/order-fines/internal/order/fines/automated-fine',
    )
    def _mock_internal_fine_update(request):
        assert request.headers['Authorization'] == PERFORMER_FINES_API_KEY
        assert request.args['order_id'] == TAXI_ORDER_ID_1
        return mockserver.make_response(
            json={
                'decisions': [],
                'pending_decisions': [],
                'new_decision': {'operation_id': '1-0-100000123456789'},
            },
            status=200,
        )

    await taxi_cargo_orders.run_task('cargo-orders-performer-fines')

    stq_call = stq.cargo_orders_performer_fines.next_call()
    await stq_runner.cargo_orders_performer_fines.call(
        task_id='test_stq', kwargs=stq_call['kwargs'],
    )


async def test_performer_fines_stq_disabled(stq_runner, testpoint):
    @testpoint('cargo-orders-performer-fines-disabled')
    def stq_disabled(data):
        pass

    await stq_runner.cargo_orders_performer_fines.call(
        task_id='test_stq',
        kwargs={
            'taxi_order_id': 'id',
            'dbid_uuid': 'dbid_uuid',
            'cargo_cancel_reason': 'reason',
        },
    )

    assert stq_disabled.times_called == 1


@pytest.mark.parametrize(
    'state_fail_reason',
    ['order_does_not_exist', 'too_late_to_rebill', 'order_without_performer'],
)
async def test_performer_fines_critical_fail(
        mockserver,
        stq,
        stq_runner,
        testpoint,
        state_fail_reason,
        mock_stq_settings_with_reschedule,
        mock_mapping_cancel_reason_to_fine_code,
):
    @mockserver.json_handler(
        '/order-fines-via-abk/order-fines/internal/order/fines/automated-fine',
    )
    def _mock_internal_automated_fine(request):
        return mockserver.make_response(
            json={'code': state_fail_reason, 'message': 'text', 'details': {}},
            status=409,
        )

    @testpoint('cargo-orders-performer-fines-critical-fail')
    def check_testpoint(data):
        assert data['fail_reason_code'] == state_fail_reason

    assert stq.cargo_orders_performer_fines.times_called == 0
    await stq_runner.cargo_orders_performer_fines.call(
        task_id=f'test_stq_{state_fail_reason}',
        kwargs={
            'taxi_order_id': TAXI_ORDER_ID_1,
            'dbid_uuid': DBID_UUID_1,
            'cargo_cancel_reason': CARGO_CANCEL_REASON_1,
        },
    )
    assert stq.cargo_orders_performer_fines.times_called == 0
    assert check_testpoint.times_called == 1


@pytest.mark.parametrize(
    'state_fail_reason',
    [
        'order_unfinished',
        'has_pending_operations',
        'race_condition',
        'billing_reject',
    ],
)
async def test_performer_fines_non_critical_fail(
        mockserver,
        stq,
        stq_runner,
        testpoint,
        state_fail_reason,
        mock_stq_settings_with_reschedule,
        mock_mapping_cancel_reason_to_fine_code,
):
    @mockserver.json_handler(
        '/order-fines-via-abk/order-fines/internal/order/fines/automated-fine',
    )
    def _mock_internal_automated_fine(request):
        return mockserver.make_response(
            json={'code': state_fail_reason, 'message': 'text', 'details': {}},
            status=409,
        )

    @testpoint('cargo-orders-performer-fines-non-critical-fail')
    def check_testpoint(data):
        assert data['fail_reason_code'] == state_fail_reason

    assert stq.cargo_orders_performer_fines.times_called == 0
    await stq_runner.cargo_orders_performer_fines.call(
        task_id=f'test_stq_{state_fail_reason}',
        kwargs={
            'taxi_order_id': TAXI_ORDER_ID_1,
            'dbid_uuid': DBID_UUID_1,
            'cargo_cancel_reason': CARGO_CANCEL_REASON_1,
        },
    )
    assert stq.cargo_orders_performer_fines.times_called == 1
    assert check_testpoint.times_called == 1

    await stq_runner.cargo_orders_performer_fines.call(
        task_id=f'test_stq_{state_fail_reason}',
        kwargs={
            'taxi_order_id': TAXI_ORDER_ID_1,
            'dbid_uuid': DBID_UUID_1,
            'cargo_cancel_reason': CARGO_CANCEL_REASON_1,
        },
        reschedule_counter=1,
    )
    assert stq.cargo_orders_performer_fines.times_called == 1
    assert check_testpoint.times_called == 2


async def test_performer_fines_automated_fine_500(
        mockserver,
        stq,
        stq_runner,
        mock_stq_settings_with_reschedule,
        mock_mapping_cancel_reason_to_fine_code,
):
    @mockserver.json_handler(
        '/order-fines-via-abk/order-fines/internal/order/fines/automated-fine',
    )
    def _mock_internal_automated_fine(request):
        return mockserver.make_response('fail', status=500)

    assert stq.cargo_orders_performer_fines.times_called == 0
    await stq_runner.cargo_orders_performer_fines.call(
        task_id=f'test_stq',
        kwargs={
            'taxi_order_id': TAXI_ORDER_ID_1,
            'dbid_uuid': DBID_UUID_1,
            'cargo_cancel_reason': CARGO_CANCEL_REASON_1,
        },
    )
    assert stq.cargo_orders_performer_fines.times_called == 1

    await stq_runner.cargo_orders_performer_fines.call(
        task_id=f'test_stq',
        kwargs={
            'taxi_order_id': TAXI_ORDER_ID_1,
            'dbid_uuid': DBID_UUID_1,
            'cargo_cancel_reason': CARGO_CANCEL_REASON_1,
        },
        reschedule_counter=1,
    )
    assert stq.cargo_orders_performer_fines.times_called == 1


async def test_performer_fines_stq_update_codes_mapping_not_found(
        mockserver,
        stq,
        stq_runner,
        testpoint,
        mock_stq_settings_with_reschedule,
):
    @mockserver.json_handler(
        '/order-fines-via-abk/order-fines/internal/order/fines/automated-fine',
    )
    def _mock_internal_automated_fine(request):
        return mockserver.make_response(
            json={
                'decisions': [],
                'pending_decisions': [],
                'new_decision': {'operation_id': '1-0-100000123456789'},
            },
            status=200,
        )

    @testpoint('cargo-orders-performer-fines-codes-mapping-not-found')
    def check_testpoint(data):
        pass

    assert stq.cargo_orders_performer_fines.times_called == 0
    await stq_runner.cargo_orders_performer_fines.call(
        task_id=f'test_stq',
        kwargs={
            'taxi_order_id': TAXI_ORDER_ID_1,
            'dbid_uuid': DBID_UUID_1,
            'cargo_cancel_reason': CARGO_CANCEL_REASON_1,
        },
    )
    assert stq.cargo_orders_performer_fines.times_called == 1
    assert check_testpoint.times_called == 1

    await stq_runner.cargo_orders_performer_fines.call(
        task_id=f'test_stq',
        kwargs={
            'taxi_order_id': TAXI_ORDER_ID_1,
            'dbid_uuid': DBID_UUID_1,
            'cargo_cancel_reason': CARGO_CANCEL_REASON_1,
        },
        reschedule_counter=1,
    )
    assert stq.cargo_orders_performer_fines.times_called == 1
    assert check_testpoint.times_called == 2


async def test_performer_fines_stq_fine_code_disabled(
        taxi_cargo_orders,
        mockserver,
        stq,
        stq_runner,
        testpoint,
        mock_stq_settings_with_reschedule,
        experiments3,
):
    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_orders_order_cancel_performer_reason_to_fine_code',
        consumers=['cargo-orders/order-cancel-performer-reason-to-fine-code'],
        clauses=[],
        default_value={'enabled': False, 'fine_code': 'cancel_after_confirm'},
    )
    await taxi_cargo_orders.invalidate_caches()

    @mockserver.json_handler(
        '/order-fines-via-abk/order-fines/internal/order/fines/automated-fine',
    )
    def _mock_internal_automated_fine(request):
        return mockserver.make_response(
            json={
                'decisions': [],
                'pending_decisions': [],
                'new_decision': {'operation_id': '1-0-100000123456789'},
            },
            status=200,
        )

    @testpoint('cargo-orders-performer-fines-fine-code-disabled')
    def check_testpoint(data):
        pass

    assert stq.cargo_orders_performer_fines.times_called == 0
    await stq_runner.cargo_orders_performer_fines.call(
        task_id=f'test_stq',
        kwargs={
            'taxi_order_id': TAXI_ORDER_ID_1,
            'dbid_uuid': DBID_UUID_1,
            'cargo_cancel_reason': CARGO_CANCEL_REASON_1,
        },
    )
    assert stq.cargo_orders_performer_fines.times_called == 0
    assert check_testpoint.times_called == 1


async def test_performer_fines_stq_automated_fine_400(
        mockserver,
        stq,
        stq_runner,
        mock_stq_settings_with_reschedule,
        mock_mapping_cancel_reason_to_fine_code,
):
    @mockserver.json_handler(
        '/order-fines-via-abk/order-fines/internal/order/fines/automated-fine',
    )
    def _mock_internal_fine_update(request):
        return mockserver.make_response(
            json={'code': 'invalid_cursor', 'message': 'some_message'},
            status=400,
        )

    assert stq.cargo_orders_performer_fines.times_called == 0
    await stq_runner.cargo_orders_performer_fines.call(
        task_id=f'test_stq',
        kwargs={
            'taxi_order_id': TAXI_ORDER_ID_1,
            'dbid_uuid': DBID_UUID_1,
            'cargo_cancel_reason': CARGO_CANCEL_REASON_1,
        },
    )
    assert stq.cargo_orders_performer_fines.times_called == 0


async def test_performer_fines_stq_automated_fine_st_ticket(
        mockserver,
        stq,
        stq_runner,
        mock_stq_settings_with_ticket_and_comment,
        mock_mapping_cancel_reason_to_fine_code,
):
    @mockserver.json_handler(
        '/order-fines-via-abk/order-fines/internal/order/fines/automated-fine',
    )
    def _mock_internal_fine_update(request):
        assert request.json['reason']['st_ticket'] == 'TICKET'
        assert request.json['reason']['comment'] == 'COMMENT'
        return mockserver.make_response(json={}, status=200)

    assert stq.cargo_orders_performer_fines.times_called == 0
    await stq_runner.cargo_orders_performer_fines.call(
        task_id=f'test_stq',
        kwargs={
            'taxi_order_id': TAXI_ORDER_ID_1,
            'dbid_uuid': DBID_UUID_1,
            'cargo_cancel_reason': CARGO_CANCEL_REASON_1,
        },
    )
    assert stq.cargo_orders_performer_fines.times_called == 0
