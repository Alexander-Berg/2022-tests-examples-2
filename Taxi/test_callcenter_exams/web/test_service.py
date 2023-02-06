import pytest


@pytest.fixture
def taxi_callcenter_exams_mocks():
    """Put your mocks here"""


async def test_ping(web_app_client, simple_secdist):
    response = await web_app_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
