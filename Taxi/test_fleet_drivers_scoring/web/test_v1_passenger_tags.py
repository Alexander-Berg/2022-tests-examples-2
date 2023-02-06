import pytest

from test_fleet_drivers_scoring import utils as global_utils
from test_fleet_drivers_scoring.web import defaults
from test_fleet_drivers_scoring.web import utils

ENDPOINT = 'v1/paid/drivers/scoring/passenger-tags/retrieve'


@pytest.mark.config(**defaults.SCORING_ENABLED_CONFIG1)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_ok.sql'])
@pytest.mark.parametrize(
    'check_id, expected_response',
    [
        (
            'req_done',
            {
                'response': {
                    'data': {
                        'top_negative_tags': [
                            {
                                'frequency_commpared_with_average_percent': 20,
                                'name': 'driver_impolite',
                            },
                            {
                                'frequency_commpared_with_average_percent': (
                                    12.5
                                ),
                                'name': 'smelly_vehicle',
                            },
                        ],
                        'top_positive_tags': [
                            {
                                'frequency_commpared_with_average_percent': (
                                    -10
                                ),
                                'name': 'tag_mood',
                            },
                        ],
                    },
                    'version': '1',
                },
            },
        ),
        ('req_no_data', {}),
    ],
)
async def test_ok(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        check_id,
        expected_response,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}],
    )

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={'request_id': check_id},
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text
    response_json = await response.json()
    assert global_utils.date_parsed(response_json) == global_utils.date_parsed(
        expected_response,
    )
