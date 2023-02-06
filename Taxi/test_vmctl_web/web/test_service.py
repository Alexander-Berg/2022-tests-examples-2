import pytest


@pytest.fixture
def taxi_vmctl_web_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_vmctl_web_mocks')
async def test_ping(taxi_vmctl_web_web):
    response = await taxi_vmctl_web_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
