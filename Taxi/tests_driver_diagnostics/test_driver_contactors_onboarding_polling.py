import pytest

from tests_driver_diagnostics import utils


@pytest.mark.experiments3(filename='ui_restrictions_configs.json')
@pytest.mark.parametrize(
    'experiments3_json, request_body, expected_response, reasons',
    [
        (
            'diagnostics_contractos_onbording_polling.json',
            'contractors_polling_request_became_free.json',
            'contractors_polling_response_block_empty.json',
            {'some_filter': [], 'zone_not_found': []},
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
        '/driver/v1/driver-diagnostics/v1/contractors/onboarding-polling',
        headers=utils.get_auth_headers(contractor_profile_id='driver_id2'),
        json=load_json(request_body),
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
