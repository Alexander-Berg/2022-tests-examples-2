import pytest

import test_fleet_drivers_scoring.utils as global_utils
from test_fleet_drivers_scoring.web import defaults
from test_fleet_drivers_scoring.web import utils


ENDPOINT = 'v1/paid/drivers/scoring/status'


@pytest.mark.config(**defaults.SCORING_ENABLED_CONFIG1)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_status_ok.sql'])
@pytest.mark.parametrize(
    'request_id, expected_response',
    [
        (
            'req_pending',
            {
                'scoring': {'status': 'pending'},
                'meta_info': {'created_at': '2020-08-01T00:00:00.000000Z'},
            },
        ),
        (
            'req_done',
            {
                'scoring': {'status': 'done'},
                'meta_info': {'created_at': '2020-08-01T00:00:00.000000Z'},
            },
        ),
        (
            'req_internal_error',
            {
                'scoring': {'status': 'internal_error'},
                'meta_info': {'created_at': '2020-08-01T00:00:00.000000Z'},
            },
        ),
        ('not_found', {'scoring': {'status': 'pending'}}),
        (
            'req_failed',
            {
                'scoring': {'status': 'failed', 'reason': 'not_enough_money'},
                'meta_info': {'created_at': '2020-08-01T00:00:00.000000Z'},
            },
        ),
    ],
)
async def test_status_ok(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        request_id,
        expected_response,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}],
    )

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={'request_id': request_id},
        params={'park_id': 'park1'},
    )

    assert _mock_fleet_parks.parks_list.times_called == 1

    assert response.status == 200, response.text
    response_json = await response.json()
    assert global_utils.date_parsed(response_json) == global_utils.date_parsed(
        expected_response,
    )


@pytest.mark.parametrize(
    'config, park_id, response_fleet_parks, fleet_parks_call_number,'
    'expected_response',
    [
        (
            defaults.SCORING_ENABLED_CONFIG3,
            'park2',
            {'parks': [defaults.RESPONSE_FLEET_PARKS2]},
            0,
            {'code': '400', 'message': 'Scoring is disabled'},
        ),
        (
            defaults.SCORING_ENABLED_CONFIG2,
            'park4',
            {'parks': [defaults.RESPONSE_FLEET_PARKS3]},
            1,
            {'code': '400', 'message': 'Park park4 was not found'},
        ),
        (
            defaults.SCORING_ENABLED_CONFIG2,
            'park3',
            {'parks': [defaults.RESPONSE_FLEET_PARKS2]},
            0,
            {'code': '400', 'message': 'Scoring is disabled for park park3'},
        ),
    ],
)
async def test_scoring_disabled(
        taxi_fleet_drivers_scoring_web,
        taxi_config,
        _mock_fleet_parks,
        config,
        park_id,
        response_fleet_parks,
        fleet_parks_call_number,
        expected_response,
):
    taxi_config.set_values(config)
    _mock_fleet_parks.set_parks_list_responses([response_fleet_parks])

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={'request_id': 'req1'},
        params={'park_id': park_id},
    )

    assert _mock_fleet_parks.parks_list.times_called == fleet_parks_call_number

    assert response.status == 400, response.text
    response_json = await response.json()
    assert response_json == expected_response
