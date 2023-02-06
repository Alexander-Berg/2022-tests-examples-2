import pytest


@pytest.fixture
def mock_fleet_parks_list(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _park_list(request):
        return {
            'parks': [
                {
                    'city_id': 'city1',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'park1',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'locale1',
                    'login': 'login1',
                    'name': 'super_park1',
                    'provider_config': context.provider_config,
                    'tz_offset': 3,
                    'geodata': {'lat': 12, 'lon': 23, 'zoom': 0},
                },
            ],
        }

    class Context:
        def __init__(self):
            self.handler = _park_list
            self.provider_config = {'clid': 'clid1', 'type': 'production'}

    context = Context()

    return context
