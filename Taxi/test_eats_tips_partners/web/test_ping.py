import pytest


@pytest.mark.servicetest
async def test_ping(taxi_eats_tips_partners_web):
    response = await taxi_eats_tips_partners_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
