import pytest


@pytest.fixture
def taxi_hiring_data_markup_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_hiring_data_markup_mocks')
async def test_ping(taxi_hiring_data_markup_web):
    response = await taxi_hiring_data_markup_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
