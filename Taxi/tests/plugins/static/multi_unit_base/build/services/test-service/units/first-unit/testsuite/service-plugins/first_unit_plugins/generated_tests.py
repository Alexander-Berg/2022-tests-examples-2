import pytest

__all__ = [
    'test_ping',
    'test_incremental_cache_update',
]


# Every service must have this handler
@pytest.mark.servicetest
async def test_ping(taxi_first_unit):
    response = await taxi_first_unit.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''


async def test_incremental_cache_update(taxi_first_unit):
    await taxi_first_unit.update_server_state()
    await taxi_first_unit.invalidate_caches(clean_update=False)


