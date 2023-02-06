# pylint: disable=invalid-name
import pytest


@pytest.fixture
def taxi_eats_automation_statistics_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_eats_automation_statistics_mocks')
async def test_ping(taxi_eats_automation_statistics_web):
    response = await taxi_eats_automation_statistics_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
