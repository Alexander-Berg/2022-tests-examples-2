import pytest


@pytest.fixture
def eda_eats_support_telephony_mocks():  # pylint: disable=invalid-name
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('eda_eats_support_telephony_mocks')
async def test_ping(taxi_eats_support_telephony_web):
    response = await taxi_eats_support_telephony_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
