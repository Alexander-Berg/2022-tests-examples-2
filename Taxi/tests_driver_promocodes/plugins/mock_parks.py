import pytest


@pytest.fixture(name='parks')
def parks(mockserver):
    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _mock_parks(request):
        if request.json['query']['park']['id'] == 'unknown':
            return {
                'driver_profiles': [],
                'offset': 0,
                'parks': [{'id': 'unknown'}],
                'total': 0,
                'limit': 1,
            }
        return {
            'driver_profiles': [
                {
                    'accounts': [{'currency': 'RUB', 'id': 'driver_0'}],
                    'driver_profile': {'id': 'driver_0'},
                },
            ],
            'offset': 0,
            'parks': [{'id': 'park_0', 'country_id': 'rus', 'city': 'Москва'}],
            'total': 1,
            'limit': 1,
        }
