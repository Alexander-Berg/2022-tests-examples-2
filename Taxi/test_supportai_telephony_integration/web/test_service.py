import pytest


@pytest.mark.servicetest
async def test_ping(taxi_supportai_telephony_integration_web):
    response = await taxi_supportai_telephony_integration_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
