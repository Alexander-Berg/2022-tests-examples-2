# pylint: disable=invalid-name
import pytest


@pytest.fixture
def eda_eats_testing_simplifier_responser_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('eda_eats_testing_simplifier_responser_mocks')
async def test_ping(taxi_eats_testing_simplifier_responser_web):
    response = await taxi_eats_testing_simplifier_responser_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
