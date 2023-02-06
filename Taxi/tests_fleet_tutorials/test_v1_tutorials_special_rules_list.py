from tests_fleet_tutorials import utils

ENDPOINT = '/v1/tutorials/special-rules/list'


async def test_ok(taxi_fleet_tutorials):

    response = await taxi_fleet_tutorials.get(
        ENDPOINT, headers={'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'special_rules': ['new_users_only']}
