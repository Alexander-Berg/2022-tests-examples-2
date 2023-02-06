import pytest


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.features_on('enable_clowny_alert_manager_settings')
async def test_configure_duty_group_for_alert_manger(
        call_cube_handle, clowny_alert_manager_recipients_set_default,
):
    recipients_set_default = clowny_alert_manager_recipients_set_default

    await call_cube_handle(
        'ConfigureUnifiedRecipientsForAlertManager',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {'service_id': 1},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )

    assert recipients_set_default.times_called == 1
    assert recipients_set_default.next_call()['request'].json == {
        'clown_service_id': 1,
        'duty_group_id': 'taxidutyhejmdal',
        'cluster_type': 'nanny',
    }


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.features_on('enable_clowny_alert_manager_settings')
async def test_configure_duty_group_for_alert_manger_no_duty_group(
        call_cube_handle, clowny_alert_manager_recipients_set_default,
):
    recipients_set_default = clowny_alert_manager_recipients_set_default

    await call_cube_handle(
        'ConfigureUnifiedRecipientsForAlertManager',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {'service_id': 2},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )

    assert recipients_set_default.times_called == 0


@pytest.mark.parametrize(
    ['expected_cam_times_called', 'policy_response', 'content_expected'],
    [
        pytest.param(
            0, None, {'payload': {'job_id': None}, 'status': 'success'},
        ),
        pytest.param(
            1,
            {
                'json': {
                    'clown_branch_id': 228,
                    'juggler_host': 'some_juggler_host',
                },
            },
            {'payload': {'job_id': None}, 'status': 'success'},
            marks=pytest.mark.features_on(
                'enable_clowny_alert_manager_policy',
            ),
        ),
        pytest.param(
            1,
            {
                'json': {
                    'clown_branch_id': 228,
                    'juggler_host': 'some_juggler_host',
                    'job_id': 123,
                },
            },
            {'payload': {'job_id': 123}, 'status': 'success'},
            marks=pytest.mark.features_on(
                'enable_clowny_alert_manager_policy',
            ),
        ),
        pytest.param(
            1,
            {
                'json': {
                    'message': 'message',
                    'code': 'CLOWNDUCTOR_MISSING_DIRECT_LINK',
                },
                'status': 400,
            },
            {
                'payload': {'job_id': None},
                'sleep_duration': 30,
                'status': 'in_progress',
            },
            marks=pytest.mark.features_on(
                'enable_clowny_alert_manager_policy',
            ),
        ),
    ],
)
async def test_create_alert_manager_policy(
        mockserver,
        call_cube_handle,
        mock_clowny_alert_manager,
        expected_cam_times_called,
        policy_response,
        content_expected,
):
    @mock_clowny_alert_manager('/v1/policy')
    def _create_policy_mock(request):
        assert request.method == 'POST'
        assert request.query['clown_branch_id'] == '228'
        assert request.query['generate_default_check_file']

        return mockserver.make_response(**policy_response)

    await call_cube_handle(
        'CreateAlertManagerPolicy',
        {
            'content_expected': content_expected,
            'data_request': {
                'input_data': {'branch_id': 228},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )

    assert _create_policy_mock.times_called == expected_cam_times_called


@pytest.mark.parametrize(
    ['expected_cam_times_called', 'policy_response', 'content_expected'],
    [
        pytest.param(
            0, None, {'payload': {'job_id': None}, 'status': 'success'},
        ),
        pytest.param(
            1,
            {'json': {}, 'status': 200},
            {'payload': {'job_id': None}, 'status': 'success'},
            marks=pytest.mark.features_on(
                'enable_clowny_alert_manager_policy',
            ),
        ),
        pytest.param(
            1,
            {'json': {'job_id': 123}, 'status': 200},
            {'payload': {'job_id': 123}, 'status': 'success'},
            marks=pytest.mark.features_on(
                'enable_clowny_alert_manager_policy',
            ),
        ),
    ],
)
async def test_delete_alert_manager_policy(
        mockserver,
        call_cube_handle,
        mock_clowny_alert_manager,
        expected_cam_times_called,
        policy_response,
        content_expected,
):
    @mock_clowny_alert_manager('/v1/policy')
    def _delete_policy_mock(request):
        assert request.method == 'DELETE'
        assert request.query['clown_branch_id'] == '228'
        assert request.query['delete_default_check_file']

        return mockserver.make_response(**policy_response)

    await call_cube_handle(
        'DeleteAlertManagerPolicy',
        {
            'content_expected': content_expected,
            'data_request': {
                'input_data': {'branch_id': 228},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )

    assert _delete_policy_mock.times_called == expected_cam_times_called
