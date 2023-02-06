import pytest

from tests_driver_diagnostics import utils


@pytest.mark.parametrize(
    'data, step, expected_testpoint',
    [
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'init',
            ['eats_fns_not_started', 'self_employed_profile_flow'],
            id='Init step',
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'binding',
            ['eats_fns_not_started', 'self_employed_profile_flow'],
            id='Binding step',
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'bindingCheck',
            ['self_employed_profile_flow'],
            id='Fns not finished',
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'finish',
            [],
            id='No reasons',
        ),
        pytest.param(
            {
                'external_ids': {},
                'orders_provider': {'taxi': True, 'eda': False},
            },
            '',
            [],
            id='No eats id',
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': False},
            },
            '',
            [],
            id='Orders provider eda=False',
        ),
    ],
)
@pytest.mark.experiments3(filename='fns_provider_configs.json')
async def test_fns_provider(
        testpoint,
        taxi_driver_diagnostics,
        driver_profiles,
        data,
        step,
        expected_testpoint,
        eats_core_context,
        mock_eats_core,
):
    @testpoint('FnsStepToReasonMap')
    def _fns_testpoint(data: list):
        assert sorted(data) == sorted(expected_testpoint)

    eats_core_context.set_context(fns_step=step)

    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID,
        external_ids=data['external_ids'],
        orders_provider=data['orders_provider'],
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions/category',
        headers=utils.get_auth_headers(),
        json={
            'client_reasons': [],
            'category': 'econom',
            'position': {'lon': 37.590533, 'lat': 55.733863},
        },
    )

    assert response.status_code == 200
    if expected_testpoint:
        assert _fns_testpoint.times_called == 1


@pytest.mark.parametrize(
    'data, status, expected_testpoint',
    [
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'problem',
            'bank_and_passport_filling_flow',
            id='Problem',
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'success',
            '',
            id='No reasons',
        ),
        pytest.param(
            {
                'external_ids': {},
                'orders_provider': {'taxi': True, 'eda': False},
            },
            '',
            '',
            id='No eats id',
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': False},
            },
            '',
            '',
            id='Orders provider eda=False',
        ),
    ],
)
@pytest.mark.experiments3(filename='billing_providers_configs.json')
async def test_billing_provider(
        testpoint,
        taxi_driver_diagnostics,
        data,
        status,
        expected_testpoint,
        driver_profiles,
        eats_core_context,
        mock_eats_core,
):
    @testpoint('ReportEatsBillingDataMissing')
    def _billing_testpoint(data: str):
        assert data == expected_testpoint

    eats_core_context.set_context(billing_status=status)

    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID,
        external_ids=data['external_ids'],
        orders_provider=data['orders_provider'],
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions/category',
        headers=utils.get_auth_headers(),
        json={
            'client_reasons': [],
            'category': 'econom',
            'position': {'lon': 37.590533, 'lat': 55.733863},
        },
    )

    assert response.status_code == 200
    if expected_testpoint:
        assert _billing_testpoint.times_called == 1


@pytest.mark.parametrize('lesson_progress', [0, 50, 100])
@pytest.mark.parametrize('correct_driver_id', [True, False])
@pytest.mark.parametrize('correct_park_id', [True, False])
@pytest.mark.parametrize('correct_lesson_id', [True, False])
@pytest.mark.experiments3(filename='training_status_provider_configs.json')
async def test_training_status_provider(
        testpoint,
        taxi_driver_diagnostics,
        mock_eats_core,
        driver_profiles,
        lesson_progress,
        correct_driver_id,
        correct_park_id,
        correct_lesson_id,
        driver_lessons_context,
        mock_driver_lessons,
        taxi_config,
):
    expected_testpoint = (
        ''
        if lesson_progress == 100
        and correct_driver_id
        and correct_park_id
        and correct_lesson_id
        else 'service_onboarding_flow'
    )

    @testpoint('ReportEatsTrainingStatusNotFinished')
    def _training_testpoint(data: str):
        assert data == expected_testpoint

    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID, external_ids={'eats': '12345'},
    )

    lesson_id_ = 'lesson_id'
    taxi_config.set_values(
        {'DRIVER_DIAGNOSTICS_EATS_TRAINING_CONFIG': {'lesson_id': lesson_id_}},
    )

    driver_lessons_context.add_lesson_progress(
        lesson_id=lesson_id_ if correct_lesson_id else 'some_lesson_id',
        progress=lesson_progress,
        driver_id=(
            utils.CONTRACTOR_PROFILE_ID
            if correct_driver_id
            else 'some_driver_id'
        ),
        park_id=utils.PARK_ID if correct_park_id else 'some_park_id',
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions/category',
        headers=utils.get_auth_headers(),
        json={
            'client_reasons': [],
            'category': 'econom',
            'position': {'lon': 37.590533, 'lat': 55.733863},
        },
    )

    assert response.status_code == 200
    if expected_testpoint:
        assert _training_testpoint.times_called == 1


@pytest.mark.parametrize(
    'data, status, expected_testpoint, courier_external_id',
    [
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'Any Status',
            ['schedule_activation_flow', 'receive_uniform_flow'],
            '123',
            id='Status training not finished',
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'Invited to HUB',
            '',
            '123',
            id='Status "Invited to HUB" OK',
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'Active',
            '',
            '123',
            id='Status "Active" OK',
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            'Active',
            '',
            None,
            id='No courier external id',
        ),
    ],
)
@pytest.mark.experiments3(filename='hub_invitation_provider.json')
async def test_hub_invitation_status_provider(
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
        mock_driver_lessons,
):
    @testpoint('ReportEatsHubInvitationStatusNotFinished')
    def _hub_invitation_testpoint(data: str):
        assert data == expected_testpoint

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

    eats_core_context.set_context(courier_external_id=courier_external_id)

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions/category',
        headers=utils.get_auth_headers(),
        json={
            'client_reasons': [],
            'category': 'econom',
            'position': {'lon': 37.590533, 'lat': 55.733863},
        },
    )

    assert response.status_code == 200
    if expected_testpoint:
        assert _hub_invitation_testpoint.times_called == 1
