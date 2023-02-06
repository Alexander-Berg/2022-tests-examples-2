import pytest


@pytest.fixture
def taxi_supportai_license_server_mocks():  # pylint: disable=invalid-name
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_supportai_license_server_mocks')
async def test_ping(taxi_supportai_license_server_web):
    response = await taxi_supportai_license_server_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
