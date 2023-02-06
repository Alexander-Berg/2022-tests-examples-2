import pytest


@pytest.fixture
def taxi_wfm_bot_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_wfm_bot_mocks')
async def test_ping(taxi_workforce_management_bot_web):
    response = await taxi_workforce_management_bot_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
