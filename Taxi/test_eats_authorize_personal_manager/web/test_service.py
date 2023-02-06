# pylint: disable=W0612,C0103
import pytest


@pytest.fixture
def eda_eats_authorize_personal_manager_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('eda_eats_authorize_personal_manager_mocks')
async def test_ping(taxi_eats_authorize_personal_manager_web):
    response = await taxi_eats_authorize_personal_manager_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
