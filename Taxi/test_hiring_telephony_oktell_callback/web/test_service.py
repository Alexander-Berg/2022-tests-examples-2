import pytest


@pytest.mark.servicetest
@pytest.mark.usefixtures('personal')
async def test_ping(taxi_hiring_telephony_oktell_callback_web):
    response = await taxi_hiring_telephony_oktell_callback_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
