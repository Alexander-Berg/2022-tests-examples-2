import pytest


@pytest.fixture
def taxi_segment_splitter_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_segment_splitter_mocks')
async def test_ping(taxi_segment_splitter_web):
    response = await taxi_segment_splitter_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
