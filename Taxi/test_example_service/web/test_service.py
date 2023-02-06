import pytest


@pytest.fixture
def taxi_example_service_mocks(mock_yet_another_service):
    @mock_yet_another_service('/talk')
    def _handler(request):
        return 'It\'s some string'


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_example_service_mocks')
async def test_ping(taxi_example_service_web):
    response = await taxi_example_service_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
