import pytest


@pytest.mark.servicetest
async def test_ping(taxi_contractor_merch_payments_bot_web):
    response = await taxi_contractor_merch_payments_bot_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
