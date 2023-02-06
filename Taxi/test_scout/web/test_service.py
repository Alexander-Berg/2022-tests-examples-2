import pytest


@pytest.mark.servicetest
@pytest.mark.usefixtures('mock_tvm_rules')
async def test_ping(taxi_scout_web_oneshot):
    response = await taxi_scout_web_oneshot.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
