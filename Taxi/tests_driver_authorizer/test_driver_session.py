import pytest


@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg1',
        {'client_id': 'taximeter', 'driver_profile_id': '1234'},
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg1': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg1'])
async def test_auth_use_sessions_check_by_default(taxi_driver_authorizer):
    params = {'session': 'asdfg1', 'db': 'zxcvb'}

    response = await taxi_driver_authorizer.get(
        'driver_session', params=params,
    )
    assert response.status_code == 200
    assert response.json() == {'uuid': '1234'}


@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg1',
        {'driver_profile_id': '1234', 'client_id': 'taximeter'},
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg1': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg1'])
async def test_auth_use_sessions_check_by_default_hmset(
        taxi_driver_authorizer,
):
    params = {'session': 'asdfg1', 'db': 'zxcvb'}

    response = await taxi_driver_authorizer.get(
        'driver_session', params=params,
    )
    assert response.status_code == 200
    assert response.json() == {'uuid': '1234'}
