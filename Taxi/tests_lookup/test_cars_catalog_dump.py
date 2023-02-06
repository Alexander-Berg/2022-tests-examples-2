CACHE_NAME = 'car-color-cache'


async def test_dump_write_read(taxi_lookup):
    await taxi_lookup.write_cache_dumps(names=[CACHE_NAME])
    await taxi_lookup.read_cache_dumps(names=[CACHE_NAME])
