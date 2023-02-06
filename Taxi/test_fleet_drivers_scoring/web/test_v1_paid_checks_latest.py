import pytest

from test_fleet_drivers_scoring import utils as global_utils
from test_fleet_drivers_scoring.web import defaults
from test_fleet_drivers_scoring.web import utils

ENDPOINT = 'v1/paid/drivers/scoring/checks/latest'


@pytest.mark.config(**defaults.SCORING_ENABLED_CONFIG1)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_ok.sql'])
@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {
                'query': {
                    'driver': {
                        'license_pd_id': 'extra_super_driver_license_pd1',
                    },
                },
            },
            {'request_id': 'extra_super_check_id1'},
        ),
        (
            {
                'query': {
                    'driver': {
                        'license_pd_id': 'extra_super_driver_license_pd2',
                    },
                },
            },
            {'request_id': 'extra_super_check_id5'},
        ),
        (
            {
                'query': {
                    'driver': {
                        'license_pd_id': 'extra_super_driver_license_pd3',
                    },
                },
            },
            {},
        ),
    ],
)
async def test_ok(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        request_body,
        expected_response,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}],
    )

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json=request_body,
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text
    response_json = await response.json()
    assert global_utils.date_parsed(response_json) == global_utils.date_parsed(
        expected_response,
    )


@pytest.mark.config(**defaults.SCORING_ENABLED_CONFIG1)
@pytest.mark.parametrize(
    'parks_call_times, expected_response',
    [
        pytest.param(
            0,
            {'code': '400', 'message': 'Scoring is disabled'},
            marks=pytest.mark.config(
                FLEET_DRIVERS_SCORING_PAID_ENABLED={
                    'cities': [],
                    'countries': ['rus', 'kaz'],
                    'dbs': [],
                    'dbs_disable': [],
                    'enable': False,
                },
            ),
            id='paid disabled',
        ),
        pytest.param(
            1,
            {'code': '400', 'message': 'Scoring is disabled for park park2'},
            marks=pytest.mark.config(
                FLEET_DRIVERS_SCORING_PAID_ENABLED={
                    'cities': [],
                    'countries': [],
                    'dbs': [],
                    'dbs_disable': [],
                    'enable': True,
                },
            ),
            id='no paid scoring in country',
        ),
    ],
)
async def test_paid_disabled(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        parks_call_times,
        expected_response,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS2]}],
    )
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license_pd2'},
            },
        },
        params={'park_id': 'park2'},
    )
    assert response.status == 400, response.text
    response_json = await response.json()
    assert response_json == expected_response
    assert _mock_fleet_parks.parks_list.times_called == parks_call_times
