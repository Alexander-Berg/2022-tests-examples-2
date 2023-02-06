import pytest


@pytest.mark.servicetest
async def test_ping(taxi_admin_surger_web):
    response = await taxi_admin_surger_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
