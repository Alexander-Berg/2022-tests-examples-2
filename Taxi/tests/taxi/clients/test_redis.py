import pytest

from taxi.clients import redis as taxi_redis


@pytest.mark.skip('Enable after TAXITOOLS-781')
@pytest.mark.redis_store(['set', 'foo', 'bar'], ['hset', 'baz', 'quux', 'bat'])
@pytest.mark.nofilldb()
async def test_redis(redis_store, redis_settings, unittest_settings):
    redis = await taxi_redis.create_redis(redis_settings, unittest_settings)
    master_pool = redis.test_shard0.master

    assert await master_pool.get('foo') == b'bar'
    assert await master_pool.hgetall('baz') == {b'quux': b'bat'}

    await redis.close()

    assert all(sentinel.closed for sentinel in redis.sentinels.values())
