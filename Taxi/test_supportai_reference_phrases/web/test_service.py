# pylint: disable=C0103
import pytest


@pytest.fixture
def taxi_supportai_reference_phrases_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_supportai_reference_phrases_mocks')
async def test_ping(taxi_supportai_reference_phrases_web):
    response = await taxi_supportai_reference_phrases_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
