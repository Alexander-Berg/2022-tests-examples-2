import pytest


@pytest.mark.servicetest
async def test_ping(taxi_selfemployed_fns_receipts_web):
    response = await taxi_selfemployed_fns_receipts_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
