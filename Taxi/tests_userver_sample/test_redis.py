async def test_redis_set_get(taxi_userver_sample):
    params_set = {'hello': 'world', 'foo': 'bar'}
    response = await taxi_userver_sample.get('redis-set', params=params_set)
    assert response.status_code == 200
    assert response.content == b''
    params_get = {'hello': 1, 'foo': 1}
    response = await taxi_userver_sample.get('redis-get', params=params_get)
    assert response.status_code == 200
    assert response.json() == params_set


async def test_redis_nonexist(taxi_userver_sample):
    params_get = {'nonexist_field': 1}
    response = await taxi_userver_sample.get('redis-get', params=params_get)
    assert response.status_code == 200
    assert response.json()['nonexist_field'] is None


async def test_redis_test_commands(taxi_userver_sample):
    response = await taxi_userver_sample.get('redis-test-commands')
    assert response.status_code == 200
