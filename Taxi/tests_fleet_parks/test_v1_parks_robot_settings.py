import pytest

from testsuite.utils import ordered_object

from tests_fleet_parks import utils


ENDPOINT = '/v1/parks/robot-settings'

TEST_PARAMS = [
    (
        {'query': {'park': {'ids': ['park_with_robot_settings_1']}}},
        {
            'settings': [
                {
                    'park_id': 'park_with_robot_settings_1',
                    'robot_settings': ['disable_standard'],
                },
            ],
        },
    ),
    (
        {'query': {'park': {'ids': ['park_with_robot_settings_2']}}},
        {
            'settings': [
                {
                    'park_id': 'park_with_robot_settings_2',
                    'robot_settings': ['disable_standard', 'disable_econom'],
                },
            ],
        },
    ),
    ({'query': {'park': {'ids': ['park_valid3']}}}, {'settings': []}),
    ({'query': {'park': {'ids': ['park_unknown']}}}, {'settings': []}),
]


@pytest.mark.parametrize('payload, expected_response', TEST_PARAMS)
async def test_handler(taxi_fleet_parks, payload, expected_response):
    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    response = await taxi_fleet_parks.post(
        ENDPOINT, json=payload, headers=headers,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), expected_response, ['settings.robot_settings'],
    )
