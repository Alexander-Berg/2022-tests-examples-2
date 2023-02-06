CACHE_NAME = 'pickup-points-coordinates'


async def test_pikup_points_coordinates_cache_dump_write_read(
        taxi_dispatch_check_in,
):
    await taxi_dispatch_check_in.write_cache_dumps(names=[CACHE_NAME])
    await taxi_dispatch_check_in.read_cache_dumps(names=[CACHE_NAME])
