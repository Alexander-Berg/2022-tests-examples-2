import pytest


CACHE_NAME = 'driver-id-id-2-dbid-uuid-cache'


@pytest.mark.pgsql('reposition', files=['drivers.sql'])
async def test_dump_write_read(taxi_reposition_api):
    await taxi_reposition_api.write_cache_dumps(names=[CACHE_NAME])
    await taxi_reposition_api.read_cache_dumps(names=[CACHE_NAME])
