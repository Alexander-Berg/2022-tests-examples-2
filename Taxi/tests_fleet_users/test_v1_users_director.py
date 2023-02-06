import pytest

from tests_fleet_users import utils

ENDPOINT = 'v1/users/director'

PARK_ID = 'park_id1'

CONFIG = {
    'cities': [],
    'cities_disable': [],
    'countries': ['rus'],
    'countries_disable': [],
    'dbs': [],
    'dbs_disable': [],
    'enable': True,
}


@pytest.mark.config(DISPATCHER_ACCESS_CONTROL_MULTIFACTOR_AUTH=CONFIG)
@pytest.mark.now('2019-01-01T01:00:00+00:00')
async def test_success(taxi_fleet_users, pgsql):
    request_body = {
        'park': {'city_id': 'city_id', 'country_id': 'rus'},
        'user': {
            'name': 'User',
            'phone_pd_id': 'phone_id1',
            'group_id': 'super',
        },
    }
    response = await taxi_fleet_users.post(
        ENDPOINT, headers={'X-Park-ID': PARK_ID}, json=request_body,
    )

    assert response.status == 204

    utils.check_created_user(pgsql, request_body['user'], PARK_ID, True)
