import pytest


# Every service must have this handler
@pytest.mark.servicetest
async def test_ping(taxi_routestats):
    response = await taxi_routestats.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''


async def test_incremental_cache_update(taxi_routestats):
    await taxi_routestats.invalidate_caches(clean_update=False)
