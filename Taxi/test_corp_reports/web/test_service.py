import pytest


@pytest.mark.servicetest
async def test_ping(taxi_corp_reports_web):
    response = await taxi_corp_reports_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
