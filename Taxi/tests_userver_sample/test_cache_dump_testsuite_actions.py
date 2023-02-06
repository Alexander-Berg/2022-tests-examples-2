import pytest


CACHE_NAME = 'failing-dumped-cache'


async def test_write_read_cache_dumps_throws(taxi_userver_sample):
    with pytest.raises(AssertionError):
        await taxi_userver_sample.write_cache_dumps(names=[CACHE_NAME])

    with pytest.raises(AssertionError):
        await taxi_userver_sample.read_cache_dumps(names=[CACHE_NAME])

    # Check that the cache is alive after the errors above
    await taxi_userver_sample.invalidate_caches(cache_names=[CACHE_NAME])
