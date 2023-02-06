import pytest


@pytest.mark.pgsql('communication_scenario', files=['test_cache.sql'])
async def test_cache_not_empty(taxi_communication_scenario, testpoint):
    @testpoint('scenario-cache/cache_size')
    def cache_size(data):
        assert data == 3

    response = await taxi_communication_scenario.get('/ping')
    await cache_size.wait_call()
    assert response.status_code == 200
