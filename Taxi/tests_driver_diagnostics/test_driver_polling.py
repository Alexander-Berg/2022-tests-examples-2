import pytest

from tests_driver_diagnostics import utils

QC_BRANDING_REASON_RESPONSE = [
    {
        'code': 'branding',
        'modified': '2019-02-07T17:28:23.009000Z',
        'present': {'sanctions': ['sticker_off']},
    },
]


@pytest.mark.experiments3(filename='diagnostics_polling_blocks.json')
@pytest.mark.config(DRIVER_DIAGNOSTICS_CHECK_PROVIDERS=True)
@pytest.mark.parametrize(
    'reasons, details, providers, checks_failed, returning_checks',
    [
        (
            {'DriverLicenseBlacklisted': []},
            {},
            ['yandex'],
            1,
            ['DriverLicenseBlacklisted'],
        ),
        (
            {'DriverLicenseBlacklisted': [], 'zone_not_found': []},
            {'some_filter': []},
            ['yandex'],
            2,
            ['DriverLicenseBlacklisted', 'some_filter', 'zone_not_found'],
        ),
        ({}, {'some_filter': []}, ['yandex'], 1, ['some_filter']),
        ({'DriverLicenseBlacklisted': []}, {}, [], 0, None),
    ],
)
async def test_driver_polling(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_profiles,
        reasons,
        details,
        providers,
        checks_failed,
        returning_checks,
):
    candidates.set_response_reasons(reasons, details)
    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID, providers=providers,
    )
    expected_response = {
        'checks_failed': checks_failed,
        'show_fullscreen': False,
    }
    expected_response.update(
        {}
        if returning_checks is None
        else {'meta': {'reasons': returning_checks}},
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/polling',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == expected_response
    assert response.headers['X-Polling-Delay'] == '1'


@pytest.mark.experiments3(filename='diagnostics_nested_screens.json')
async def test_driver_polling_multiple_levels(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_profiles,
        qc_cpp,
):
    candidates.set_response_reasons(
        {'some_filter': [], 'some_hidden_filter': []}, {},
    )
    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID, vehicle_id='12345',
    )
    qc_cpp.set_exams('park_id1_12345', QC_BRANDING_REASON_RESPONSE)

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/polling',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'checks_failed': 2,
        'show_fullscreen': False,
        'meta': {'reasons': ['qc/branding', 'some_filter']},
    }


@pytest.mark.experiments3(
    filename='diagnostics_polling_blocks_query_positions.json',
)
async def test_driver_polling_query_positions(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_profiles,
        mockserver,
):
    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def yagr_handler(request):
        # pylint: disable=unused-variable
        return ''

    candidates.set_response_reasons({}, {'some_filter': []})

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/polling',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(position=None),
    )
    assert response.status_code == 200
    assert response.json() == {
        'checks_failed': 1,
        'show_fullscreen': False,
        'meta': {'reasons': ['zone_not_found']},
    }
    assert response.headers['X-Polling-Delay'] == '1'


@pytest.mark.experiments3(filename='diagnostics_polling_fullscreen.json')
@pytest.mark.config(DRIVER_DIAGNOSTICS_CHECK_PROVIDERS=True)
@pytest.mark.parametrize(
    'reasons,'
    'details,'
    'providers,'
    'checks_failed,'
    'returning_checks,'
    'last_reasons,'
    'fullscreen',
    [
        (
            {'DriverLicenseBlacklisted': []},
            {},
            ['yandex'],
            1,
            ['DriverLicenseBlacklisted'],
            None,
            False,
        ),
        (
            {'DriverLicenseBlacklisted': [], 'zone_not_found': []},
            {'some_filter': []},
            ['yandex'],
            2,
            ['DriverLicenseBlacklisted', 'some_filter', 'zone_not_found'],
            ['DriverLicenseBlacklisted', 'zone_not_found'],
            True,
        ),
        (
            {},
            {'some_filter': []},
            ['yandex'],
            1,
            ['some_filter'],
            ['some_filter'],
            False,
        ),
        ({'DriverLicenseBlacklisted': []}, {}, [], 0, None, None, False),
    ],
)
async def test_driver_polling_show_fullscreen(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_profiles,
        reasons,
        details,
        providers,
        checks_failed,
        returning_checks,
        last_reasons,
        fullscreen,
):
    candidates.set_response_reasons(reasons, details)
    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID, providers=providers,
    )
    expected_response = {
        'checks_failed': checks_failed,
        'show_fullscreen': fullscreen,
    }
    expected_response.update(
        {}
        if returning_checks is None
        else {'meta': {'reasons': returning_checks}},
    )

    request_body = utils.get_default_body()
    request_body.update(
        {} if last_reasons is None else {'last_reasons': last_reasons},
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/polling',
        headers=utils.get_auth_headers(),
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == expected_response
    assert response.headers['X-Polling-Delay'] == '1'
