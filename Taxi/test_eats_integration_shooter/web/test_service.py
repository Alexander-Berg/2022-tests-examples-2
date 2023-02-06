# pylint: disable=invalid-name

import pytest


@pytest.fixture
def eda_eats_integration_shooter_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('eda_eats_integration_shooter_mocks')
async def test_ping(taxi_eats_integration_shooter_web):
    response = await taxi_eats_integration_shooter_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
