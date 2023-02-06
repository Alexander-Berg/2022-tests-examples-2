async def test_dump_write_read(taxi_driver_ratings):
    await taxi_driver_ratings.write_cache_dumps(names=['driver-ratings-cache'])
    await taxi_driver_ratings.read_cache_dumps(names=['driver-ratings-cache'])
