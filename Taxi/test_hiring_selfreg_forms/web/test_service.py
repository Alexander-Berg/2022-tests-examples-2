import pytest

from test_hiring_selfreg_forms import conftest


@pytest.fixture
def taxi_hiring_selfreg_forms_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_hiring_selfreg_forms_mocks')
@conftest.main_configuration
async def test_ping(taxi_hiring_selfreg_forms_web):
    response = await taxi_hiring_selfreg_forms_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
