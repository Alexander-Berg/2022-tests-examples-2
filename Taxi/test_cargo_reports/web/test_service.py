import pytest


@pytest.fixture
def taxi_cargo_reports_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_cargo_reports_mocks')
async def test_ping(taxi_cargo_reports_web):
    response = await taxi_cargo_reports_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
