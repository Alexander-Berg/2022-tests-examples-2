import pytest


CACHE_NAME = 'surge-points-cache'


@pytest.mark.config(SURGE_FIXED_POINTS_FROM_ADMIN=True)
async def test_dump_write_read(taxi_heatmap_sample_storage):
    await taxi_heatmap_sample_storage.write_cache_dumps(names=[CACHE_NAME])
    await taxi_heatmap_sample_storage.read_cache_dumps(names=[CACHE_NAME])
