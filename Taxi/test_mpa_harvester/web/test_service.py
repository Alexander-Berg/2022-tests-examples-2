import pytest


@pytest.mark.servicetest
async def test_ping(taxi_mpa_harvester_web):
    response = await taxi_mpa_harvester_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
