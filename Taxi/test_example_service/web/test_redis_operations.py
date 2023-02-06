import pytest


@pytest.mark.skip('flaps, fix in TAXITOOLS-781')
async def test_redis_get_and_set(web_app_client):
    response = await web_app_client.post(
        '/redis/set', params={'key': 'John', 'value': 'Hello'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == 'OK'

    response = await web_app_client.get('/redis/get', params={'key': 'John'})
    assert response.status == 200
    content = await response.json()
    assert content == 'Hello'


@pytest.mark.skip('flaps, fix in TAXITOOLS-781')
async def test_redis_get_absent_key(web_app_client):
    response = await web_app_client.get('/redis/get', params={'key': 'John'})
    assert response.status == 404
    content = await response.json()
    assert content == {
        'code': 'not-found',
        'message': 'Value with required key is not found',
    }


@pytest.mark.skip('flaps, fix in TAXITOOLS-781')
async def test_redis_set_twice(web_app_client):
    await web_app_client.post(
        '/redis/set', params={'key': 'John', 'value': 'Hello'},
    )
    response = await web_app_client.post(
        '/redis/set', params={'key': 'John', 'value': 'Goodbye'},
    )
    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'conflict',
        'message': 'Trying to insert already added key',
    }


@pytest.mark.skip('flaps, fix in TAXITOOLS-781')
async def test_redis_hget(web_context):
    redis = web_context.redis
    master_pool = redis.test_base_shard0.master

    await master_pool.set('foo', 'bar')
    await master_pool.hset('baz', 'quux', 'bat')
    assert await master_pool.get('foo') == b'bar'
    assert await master_pool.hgetall('baz') == {b'quux': b'bat'}
