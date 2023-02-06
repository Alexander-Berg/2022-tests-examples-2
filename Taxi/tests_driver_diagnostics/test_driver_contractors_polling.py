import pytest

from tests_driver_diagnostics import utils


@pytest.mark.parametrize(
    'experiments3_json, park_id, request_body, expected_response',
    [
        (
            'diagnostics_kis_art_provider.json',
            'park_disabled',
            'contractors_polling_request_empty.json',
            'contractors_polling_response_kis_art_disabled.json',
        ),
        (
            'diagnostics_kis_art_provider.json',
            'park_enabled',
            'contractors_polling_request_empty.json',
            'contractors_polling_response_kis_art_enabled.json',
        ),
        (
            'diagnostics_absolute_block.json',
            'park_id1',
            'contractors_polling_request_empty.json',
            'contractors_polling_response_ok.json',
        ),
    ],
)
@pytest.mark.now('2020-01-01T19:00:00.000Z')
async def test_contactors_polling_kis_art(
        taxi_driver_diagnostics,
        park_id,
        load_json,
        request_body,
        expected_response,
        experiments3_json,
        experiments3,
):
    experiments3.add_experiments_json(load_json(experiments3_json))

    request_body = load_json(request_body)
    request_body['position'] = utils.get_position()

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/contractors/polling',
        headers=utils.get_auth_headers(park_id=park_id),
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.parametrize(
    'experiments3_json, request_body, expected_response, reasons',
    [
        (
            'diagnostics_contractors_polling_all_underlying.json',
            'contractors_polling_request_empty.json',
            'contractors_polling_response_all_levels.json',
            {
                'DriverLicenseBlacklisted': [],
                'coordinates_not_found': [],
                'some_filter': [],
                'zone_not_found': [],
                'GpsDisabled': [],
                'Network': [],
            },
        ),
        (
            'diagnostics_contractors_polling_no_underlying.json',
            'contractors_polling_request_empty.json',
            'contractors_polling_response_absolute_blocks.json',
            {
                'DriverLicenseBlacklisted': [],
                'coordinates_not_found': [],
                'some_filter': [],
                'zone_not_found': [],
                'GpsDisabled': [],
                'Network': [],
            },
        ),
        (
            'diagnostics_contractors_polling_all_underlying.json',
            'contractors_polling_request_empty.json',
            'contractors_polling_response_blocks_warnings.json',
            {
                'some_filter': [],
                'zone_not_found': [],
                'GpsDisabled': [],
                'Network': [],
            },
        ),
        (
            'diagnostics_contractors_polling_no_underlying.json',
            'contractors_polling_request_empty.json',
            'contractors_polling_response_blocks.json',
            {
                'some_filter': [],
                'zone_not_found': [],
                'GpsDisabled': [],
                'Network': [],
            },
        ),
        (
            'diagnostics_contractors_polling_all_underlying.json',
            'contractors_polling_request_empty.json',
            'contractors_polling_response_warnings.json',
            {'GpsDisabled': [], 'Network': []},
        ),
        (
            'diagnostics_contractors_polling_all_underlying.json',
            'contractors_polling_request_empty.json',
            'contractors_polling_response_time_blocks.json',
            {
                'efficiency/driver_weariness': [
                    'blocked till 2020-01-01T19:01:00.0+0000',
                ],
            },
        ),
        (
            'diagnostics_contractors_polling_all_underlying.json',
            'contractors_polling_request_empty.json',
            'contractors_polling_response_time_blocks_comes_soon.json',
            {
                'efficiency/driver_weariness': [
                    'blocked till 2020-01-01T18:59:00.0+0000',
                ],
            },
        ),
        (
            'diagnostics_contractors_polling_all_underlying.json',
            'contractors_polling_request_first.json',
            'contractors_polling_response_ok_first.json',
            {},
        ),
        (
            'diagnostics_contractors_polling_no_underlying.json',
            'contractors_polling_request_state_block.json',
            'contractors_polling_response_block_empty.json',
            {
                'some_filter': [],
                'zone_not_found': [],
                'GpsDisabled': [],
                'Network': [],
            },
        ),
        (
            'diagnostics_contractors_polling_no_underlying.json',
            'contractors_polling_request_became_free.json',
            'contractors_polling_response_blocks_with_driver_status.json',
            {
                'some_filter': [],
                'zone_not_found': [],
                'GpsDisabled': [],
                'Network': [],
            },
        ),
        (
            'diagnostics_contractors_polling_no_underlying.json',
            'contractors_polling_request_became_busy.json',
            'contractors_polling_response_empty_became_busy.json',
            {},
        ),
    ],
)
@pytest.mark.now('2020-01-01T19:00:00.000Z')
async def test_contractors_polling(
        taxi_driver_diagnostics,
        candidates,
        driver_profiles,
        load_json,
        request_body,
        expected_response,
        experiments3_json,
        experiments3,
        reasons,
):
    experiments3.add_experiments_json(load_json(experiments3_json))
    candidates.set_response_reasons(reasons, {}, 'driver_id2')
    driver_profiles.set_contractor_data(
        park_contractor_profile_id='park_id1_driver_id2',
    )
    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/contractors/polling',
        headers=utils.get_auth_headers(contractor_profile_id='driver_id2'),
        json=load_json(request_body),
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
