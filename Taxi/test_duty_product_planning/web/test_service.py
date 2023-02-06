import pytest


@pytest.mark.servicetest
async def test_ping(taxi_duty_product_planning_web):
    response = await taxi_duty_product_planning_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
