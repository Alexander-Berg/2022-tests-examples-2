import pytest

from tests_driver_diagnostics import utils


DEFAULT_PARK = {
    'id': utils.PARK_ID,
    'login': 'login_1',
    'name': 'name_1',
    'is_active': False,
    'city_id': 'city-id-1',
    'locale': 'ru',
    'is_billing_enabled': False,
    'is_franchising_enabled': False,
    'country_id': 'rus',
    'demo_mode': False,
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}


@pytest.mark.parametrize(
    'data, expected_response, work_status',
    [
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            {
                'scenario': 'onboarding',
                'api_prefix': 'onboarding-',
                'screen_locked': False,
            },
            'candidate',
            id='Onboarding required',
            marks=(
                pytest.mark.experiments3(
                    filename='experiments_always_true.json',
                )
            ),
        ),
        pytest.param(
            {'orders_provider': {'eda': True}},
            {'scenario': 'default', 'screen_locked': False},
            'candidate',
            id='No external ids',
            marks=(
                pytest.mark.experiments3(
                    filename='experiments_always_true.json',
                )
            ),
        ),
        pytest.param(
            {'external_ids': {}, 'orders_provider': {'eda': False}},
            {'scenario': 'default', 'screen_locked': False},
            'candidate',
            id='No eats external id',
            marks=(
                pytest.mark.experiments3(
                    filename='experiments_always_true.json',
                )
            ),
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'taxi': True, 'eda': False},
            },
            {
                'scenario': 'onboarding',
                'api_prefix': 'onboarding-',
                'screen_locked': False,
            },
            'candidate',
            id='Taxi onboarding required',
            marks=(
                pytest.mark.experiments3(
                    filename='experiments_always_true.json',
                )
            ),
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'taxi': True, 'eda': False},
            },
            {'scenario': 'default', 'screen_locked': False},
            'candidate',
            id='Only eats service false',
            marks=(
                pytest.mark.experiments3(
                    filename='experiments_only_eats_provider.json',
                )
            ),
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'taxi': False, 'eda': True},
            },
            {
                'api_prefix': 'onboarding-',
                'scenario': 'onboarding',
                'screen_locked': True,
            },
            'candidate',
            id='Only eats service true with screen_locked',
            marks=(
                pytest.mark.experiments3(
                    filename='experiments_only_eats_provider.json',
                )
            ),
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True},
            },
            {'scenario': 'default', 'screen_locked': False},
            'active',
            id='Is not candidate',
            marks=(
                pytest.mark.experiments3(
                    filename='experiments_always_true.json',
                )
            ),
        ),
        pytest.param(
            {
                'external_ids': {'eats': '12345'},
                'orders_provider': {'eda': True, 'taxi': False},
            },
            {
                'api_prefix': 'onboarding-',
                'scenario': 'onboarding',
                'screen_locked': True,
            },
            'candidate',
            id='Check coutry in kwargs',
            marks=(
                pytest.mark.experiments3(
                    filename='experiments_fleet_fetcher.json',
                )
            ),
        ),
    ],
)
async def test_onboarding_required(
        taxi_driver_diagnostics,
        mockserver,
        data,
        expected_response,
        work_status,
        driver_profiles,
        eats_core_context,
        mock_eats_core,
        fleet_parks,
):
    eats_core_context.set_context(work_status=work_status)

    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID,
        external_ids=data.get('external_ids'),
        orders_provider=data['orders_provider'],
    )

    fleet_parks.set_parks({f'{utils.PARK_ID}': DEFAULT_PARK})

    response = await taxi_driver_diagnostics.post(
        '/driver/v1/driver-diagnostics/v1/settings',
        headers=utils.get_auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == expected_response


async def test_onboarding_polling(taxi_driver_diagnostics):
    response = await taxi_driver_diagnostics.post(
        '/driver/v1/driver-diagnostics/v1/onboarding-polling',
        json=utils.get_default_body(),
        headers=utils.get_auth_headers(),
    )
    assert response.json() == {'checks_failed': 1, 'show_fullscreen': True}
