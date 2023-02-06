import pytest
import redis


@pytest.mark.asyncio
async def test_ping(redis_client: redis.StrictRedis):
    redis_client.ping()
