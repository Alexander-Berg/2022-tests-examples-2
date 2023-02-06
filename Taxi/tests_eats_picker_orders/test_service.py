import pytest


# Every service must have this handler
@pytest.mark.servicetest
async def test_ping(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''


async def test_incremental_cache_update(taxi_eats_picker_orders):
    await taxi_eats_picker_orders.invalidate_caches(clean_update=False)
