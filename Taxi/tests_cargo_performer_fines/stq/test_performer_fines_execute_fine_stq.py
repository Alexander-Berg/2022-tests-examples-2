async def test_execute_fine_stq_disabled(
        stq_runner,
        testpoint,
        default_payload,
        default_dbid_uuid,
        default_cargo_order_id,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    @testpoint('cargo-performer-fines-execute-fine-disabled')
    def stq_disabled(data):
        pass

    await stq_runner.cargo_performer_fines_execute_fine.call(
        task_id='test_stq',
        kwargs={
            'taxi_order_id': 'id',
            'cargo_order_id': default_cargo_order_id,
            'park_id': park_id,
            'driver_id': driver_id,
            'cargo_cancel_reason': 'reason',
            'payload': default_payload,
        },
    )

    assert stq_disabled.times_called == 1


async def test_execute_fine_stq_fine_code_disabled(
        taxi_cargo_performer_fines,
        mockserver,
        mock_execute_fine_stq_settings,
        stq,
        stq_runner,
        testpoint,
        experiments3,
        default_payload,
        default_dbid_uuid,
        default_cargo_order_id,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_performer_fines_cancel_reason_to_fine_code',
        consumers=['cargo-performer-fines/execute-fine-args'],
        clauses=[],
        default_value={'enabled': False, 'fine_code': 'cancel_after_confirm'},
    )
    await taxi_cargo_performer_fines.invalidate_caches()

    @testpoint('cargo-performer-fines-execute-fine-fine-code-disabled')
    def check_testpoint(data):
        pass

    assert stq.cargo_performer_fines_execute_fine.times_called == 0
    await stq_runner.cargo_performer_fines_execute_fine.call(
        task_id=f'test_stq',
        kwargs={
            'taxi_order_id': 'id',
            'cargo_order_id': default_cargo_order_id,
            'park_id': park_id,
            'driver_id': driver_id,
            'cargo_cancel_reason': 'reason',
            'payload': default_payload,
        },
    )
    assert stq.cargo_performer_fines_execute_fine.times_called == 0
    assert check_testpoint.times_called == 1


async def test_performer_fines_stq_happy_path(
        taxi_cargo_performer_fines,
        mockserver,
        stq,
        stq_runner,
        mock_analytics_job_settings,
        mock_execute_fine_stq_settings,
        mock_mapping_cancel_reason_to_fine_code,
        performer_fines_api_key,
        default_taxi_order_id,
        default_fine_code,
        default_ticket,
        default_dbid_uuid,
        default_cancel_reason,
        default_cargo_order_id,
        default_payload,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    @mockserver.json_handler(
        '/cargo-finance-via-abk/'
        'internal/cargo-finance/performer/fines/automated-fine',
    )
    def _mock_internal_fine_update(request):
        assert request.headers['Authorization'] == performer_fines_api_key
        assert request.args['taxi_order_id'] == default_taxi_order_id
        assert request.json == {
            'decision': {
                'driver_uuid': driver_id,
                'fine_code': default_fine_code,
                'park_id': park_id,
            },
            'reason': {'st_ticket': default_ticket},
        }
        return mockserver.make_response(
            json={
                'decisions': [],
                'pending_decisions': [],
                'new_decision': {'operation_id': '1-0-100000123456789'},
            },
            status=200,
        )

    await stq_runner.cargo_performer_fines_execute_fine.call(
        task_id='test_stq',
        kwargs={
            'cargo_cancel_reason': default_cancel_reason,
            'cargo_order_id': default_cargo_order_id,
            'driver_id': driver_id,
            'park_id': park_id,
            'payload': default_payload,
            'taxi_order_id': default_taxi_order_id,
        },
    )

    assert _mock_internal_fine_update.times_called == 1


async def test_performer_fines_automated_fine_500(
        mockserver,
        stq,
        stq_runner,
        mock_execute_fine_stq_settings_with_reschedule,
        mock_mapping_cancel_reason_to_fine_code,
        default_cancel_reason,
        default_cargo_order_id,
        default_dbid_uuid,
        default_payload,
        default_taxi_order_id,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    @mockserver.json_handler(
        '/cargo-finance-via-abk/'
        'internal/cargo-finance/performer/fines/automated-fine',
    )
    def _mock_internal_automated_fine(request):
        return mockserver.make_response('fail', status=500)

    assert stq.cargo_performer_fines_execute_fine.times_called == 0
    await stq_runner.cargo_performer_fines_execute_fine.call(
        task_id=f'test_stq',
        kwargs={
            'cargo_cancel_reason': default_cancel_reason,
            'cargo_order_id': default_cargo_order_id,
            'driver_id': driver_id,
            'park_id': park_id,
            'payload': default_payload,
            'taxi_order_id': default_taxi_order_id,
        },
    )
    assert stq.cargo_performer_fines_execute_fine.times_called == 1

    await stq_runner.cargo_performer_fines_execute_fine.call(
        task_id=f'test_stq',
        kwargs={
            'cargo_cancel_reason': default_cancel_reason,
            'cargo_order_id': default_cargo_order_id,
            'driver_id': driver_id,
            'park_id': park_id,
            'payload': default_payload,
            'taxi_order_id': default_taxi_order_id,
        },
        reschedule_counter=1,
    )
    assert stq.cargo_performer_fines_execute_fine.times_called == 1


async def test_performer_fines_critical_fail(
        mockserver,
        stq,
        stq_runner,
        testpoint,
        mock_execute_fine_stq_critical_fails,
        mock_mapping_cancel_reason_to_fine_code,
        taxi_config,
        default_cancel_reason,
        default_cargo_order_id,
        default_dbid_uuid,
        default_payload,
        default_taxi_order_id,
        code='critical1',
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    @mockserver.json_handler(
        '/cargo-finance-via-abk/'
        'internal/cargo-finance/performer/fines/automated-fine',
    )
    def _mock_internal_automated_fine(request):
        return mockserver.make_response(
            json={'code': code, 'message': 'text', 'details': {}}, status=409,
        )

    @testpoint('cargo-performer-fines-execute-critical-fail')
    def check_testpoint(data):
        assert data['fail_reason_code'] == code

    assert stq.cargo_performer_fines_execute_fine.times_called == 0
    await stq_runner.cargo_performer_fines_execute_fine.call(
        task_id=f'test_stq',
        kwargs={
            'cargo_cancel_reason': default_cancel_reason,
            'cargo_order_id': default_cargo_order_id,
            'driver_id': driver_id,
            'park_id': park_id,
            'payload': default_payload,
            'taxi_order_id': default_taxi_order_id,
        },
    )
    assert stq.cargo_performer_fines_execute_fine.times_called == 0
    assert check_testpoint.times_called == 1


async def test_performer_fines_non_critical_fail(
        mockserver,
        stq,
        stq_runner,
        testpoint,
        mock_execute_fine_stq_critical_fails,
        mock_mapping_cancel_reason_to_fine_code,
        taxi_config,
        default_cancel_reason,
        default_cargo_order_id,
        default_dbid_uuid,
        default_payload,
        default_taxi_order_id,
        code='non_critical1',
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    @mockserver.json_handler(
        '/cargo-finance-via-abk/'
        'internal/cargo-finance/performer/fines/automated-fine',
    )
    def _mock_internal_automated_fine(request):
        return mockserver.make_response(
            json={'code': code, 'message': 'text', 'details': {}}, status=409,
        )

    @testpoint('cargo-performer-fines-execute-non-critical-fail')
    def check_testpoint(data):
        assert data['fail_reason_code'] == code

    assert stq.cargo_performer_fines_execute_fine.times_called == 0
    await stq_runner.cargo_performer_fines_execute_fine.call(
        task_id=f'test_stq',
        kwargs={
            'cargo_cancel_reason': default_cancel_reason,
            'cargo_order_id': default_cargo_order_id,
            'driver_id': driver_id,
            'park_id': park_id,
            'payload': default_payload,
            'taxi_order_id': default_taxi_order_id,
        },
    )
    assert stq.cargo_performer_fines_execute_fine.times_called == 1
    assert check_testpoint.times_called == 1

    await stq_runner.cargo_performer_fines_execute_fine.call(
        task_id=f'test_stq',
        kwargs={
            'cargo_cancel_reason': default_cancel_reason,
            'cargo_order_id': default_cargo_order_id,
            'driver_id': driver_id,
            'park_id': park_id,
            'payload': default_payload,
            'taxi_order_id': default_taxi_order_id,
        },
        reschedule_counter=1,
    )
    assert stq.cargo_performer_fines_execute_fine.times_called == 1
    assert check_testpoint.times_called == 2
