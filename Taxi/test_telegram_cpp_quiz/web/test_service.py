import pytest


@pytest.fixture
def taxi_telegram_cpp_quiz_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_telegram_cpp_quiz_mocks')
async def test_ping(taxi_telegram_cpp_quiz_web):
    response = await taxi_telegram_cpp_quiz_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
