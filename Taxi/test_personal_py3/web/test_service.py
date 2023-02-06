import pytest


@pytest.fixture
def taxi_personal_py3_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_personal_py3_mocks')
async def test_ping(taxi_personal_py3_web):
    response = await taxi_personal_py3_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
