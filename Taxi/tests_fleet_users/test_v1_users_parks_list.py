import pytest

ENDPOINT = 'v1/users/parks/list'


@pytest.mark.parametrize(
    'user_phone, expected_park_ids',
    [('phone_id1', ['111', '222']), ('phone_id2', [])],
)
async def test_success(taxi_fleet_users, pgsql, user_phone, expected_park_ids):
    request_body = {'phone_pd_id': user_phone}
    response = await taxi_fleet_users.post(ENDPOINT, json=request_body)

    assert response.status == 200
    assert response.json()['park_ids'] == expected_park_ids
