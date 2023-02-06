import pytest

from tests_driver_diagnostics import utils


@pytest.mark.parametrize(
    'data,'
    'status,'
    'expected_testpoint,'
    'courier_external_id,'
    'client_resolved_reasons,'
    'billing_status,'
    'fns_step',
    [
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'Any Status',
            ['schedule_activation_flow', 'receive_uniform_flow'],
            '123',
            None,
            'success',
            'finish',
            id='No client resolved reasons',
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'Any Status',
            ['schedule_activation_flow', 'receive_uniform_flow'],
            '123',
            [],
            'success',
            'finish',
            id='Empty client resolved reasons',
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'Any Status',
            ['schedule_activation_flow', 'receive_uniform_flow'],
            '123',
            [
                {
                    'reason': 'hub_invitation_not_finished',
                    'resolved_at': '2020-07-07T16:30:00.00Z',
                },
            ],
            'success',
            'finish',
            id='Check client resolved reasons',
        ),
    ],
)
@pytest.mark.experiments3(filename='ui_restrictions_configs.json')
async def test_client_resolved_reasons(
        testpoint,
        taxi_driver_diagnostics,
        data,
        status,
        expected_testpoint,
        driver_profiles,
        eats_core_context,
        mock_eats_core,
        courier_external_id,
        hiring_candidates_context,
        mock_hiring_candidates,
        client_resolved_reasons,
        billing_status,
        fns_step,
        mock_driver_lessons,
):
    @testpoint('ReportEatsHubInvitationStatusNotFinished')
    def _hub_invitation_testpoint(data: str):
        assert data == expected_testpoint

    @testpoint('CollectReasons')
    def _collect_reasons(data: list):
        if client_resolved_reasons:
            for reason in data:
                assert reason not in client_resolved_reasons

    fields = [{'name': 'status', 'value': status}]

    hiring_candidates_context.set_context(
        x_consumer_id='driver-diagnostics',
        external_ids=[courier_external_id],
        fields=fields,
    )

    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID,
        external_ids=data['external_ids'],
        orders_provider=data['orders_provider'],
    )

    eats_core_context.set_context(
        courier_external_id=courier_external_id,
        billing_status=billing_status,
        fns_step=fns_step,
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/onboarding-restrictions/',
        headers=utils.get_auth_headers(),
        json={
            'client_reasons': [],
            'client_resolved_reasons': client_resolved_reasons,
        },
    )

    assert response.status_code == 200
    if expected_testpoint:
        assert _hub_invitation_testpoint.times_called == 1
    assert _collect_reasons.times_called == 1


@pytest.mark.parametrize(
    'data,'
    'status,'
    'expected_testpoints,'
    'courier_external_id,'
    'client_resolved_reasons,'
    'expected_response_file,'
    'billing_status,'
    'fns_step,'
    'kiosk_session_id',
    [
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'Test Passed',
            ['schedule_activation_flow', 'receive_uniform_flow'],
            '123',
            None,
            'ui_hub_invitation_failure_response.json',
            'success',
            'finish',
            '0707f938-affe-4027-9c6c-55273e5b39dd',
            marks=(
                pytest.mark.experiments3(
                    filename='ui_restrictions_configs.json',
                )
            ),
            id='All but hub invitation passed',
        ),
    ],
)
async def test_ui_full(
        testpoint,
        taxi_driver_diagnostics,
        data,
        status,
        expected_testpoints,
        driver_profiles,
        eats_core_context,
        mock_eats_core,
        courier_external_id,
        hiring_candidates_context,
        mock_hiring_candidates,
        client_resolved_reasons,
        load_json,
        expected_response_file,
        billing_status,
        fns_step,
        kiosk_session_id,
        mock_driver_lessons,
        driver_lessons_context,
        taxi_config,
):
    @testpoint('CollectReasons')
    def _collect_reasons(data: list):
        if client_resolved_reasons:
            for reason in data:
                assert reason not in client_resolved_reasons
        if expected_testpoints:
            for reason in data:
                assert reason in expected_testpoints

    lesson_id_ = 'lesson_id'
    taxi_config.set_values(
        {'DRIVER_DIAGNOSTICS_EATS_TRAINING_CONFIG': {'lesson_id': lesson_id_}},
    )

    fields = [{'name': 'status', 'value': status}]
    if kiosk_session_id:
        fields.append({'name': 'kiosk_session_id', 'value': kiosk_session_id})

    hiring_candidates_context.set_context(
        x_consumer_id='driver-diagnostics',
        external_ids=[courier_external_id],
        fields=fields,
    )

    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID,
        external_ids=data['external_ids'],
        orders_provider=data['orders_provider'],
    )

    eats_core_context.set_context(
        courier_external_id=courier_external_id,
        billing_status=billing_status,
        fns_step=fns_step,
    )

    driver_lessons_context.add_lesson_progress(
        lesson_id=lesson_id_,
        progress=100,
        driver_id=utils.CONTRACTOR_PROFILE_ID,
        park_id=utils.PARK_ID,
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/onboarding-restrictions/',
        headers=utils.get_auth_headers(),
        json={
            'client_reasons': [],
            'client_resolved_reasons': client_resolved_reasons,
        },
    )

    assert response.status_code == 200
    assert _collect_reasons.times_called == 1

    assert response.json() == load_json(expected_response_file)


@pytest.mark.parametrize(
    'lesson_id,response_id',
    [
        pytest.param(None, 'no_lesson_id', id='lesson_id=None'),
        pytest.param('some_lesson_id', 'lesson_id_1', id='lesson_id_1'),
        pytest.param('some_other_lesson_id', 'lesson_id_2', id='lesson_id_2'),
    ],
)
@pytest.mark.experiments3(filename='ui_restrictions_configs.json')
async def test_format_lesson_id(
        testpoint,
        taxi_driver_diagnostics,
        driver_profiles,
        eats_core_context,
        mock_eats_core,
        hiring_candidates_context,
        mock_hiring_candidates,
        mock_driver_lessons,
        load_json,
        taxi_config,
        lesson_id,
        response_id,
):
    taxi_config.set_values(
        {'DRIVER_DIAGNOSTICS_EATS_TRAINING_CONFIG': {'lesson_id': lesson_id}},
    )

    fields = [{'name': 'status', 'value': 'Any Status'}]
    courier_external_id = '123'

    hiring_candidates_context.set_context(
        x_consumer_id='driver-diagnostics',
        external_ids=[courier_external_id],
        fields=fields,
    )

    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID, external_ids={'eats': '12345'},
    )

    eats_core_context.set_context(
        courier_external_id=courier_external_id,
        billing_status='success',
        fns_step='finish',
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/onboarding-restrictions/',
        headers=utils.get_auth_headers(),
        json={'client_reasons': [], 'client_resolved_reasons': []},
    )

    assert response.status_code == 200
    assert (
        response.json()
        == load_json('format_lesson_id_responses.json')[response_id]
    )
