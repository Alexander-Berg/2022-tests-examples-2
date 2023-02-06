CACHE_NAME = 'simple-dumped-cache'


async def test_dump_write_read(taxi_userver_sample):
    await taxi_userver_sample.write_cache_dumps(names=[CACHE_NAME])
    await taxi_userver_sample.read_cache_dumps(names=[CACHE_NAME])
