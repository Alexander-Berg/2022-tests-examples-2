import pytest

__all__ = [
    'test_ping',
    'test_incremental_cache_update',
]


# Every service must have this handler
@pytest.mark.servicetest
async def test_ping(taxi_test_service):
    response = await taxi_test_service.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''


async def test_incremental_cache_update(taxi_test_service):
    await taxi_test_service.update_server_state()
    await taxi_test_service.invalidate_caches(clean_update=False)


