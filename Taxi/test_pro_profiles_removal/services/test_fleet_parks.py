from testsuite.utils import http

from pro_profiles_removal.entities import contractor
from pro_profiles_removal.generated.cron import cron_context as context


async def test_parks_list(cron_context: context.Context, mock_fleet_parks):
    @mock_fleet_parks('/v1/parks/list')
    async def _parks_list(request: http.Request):
        assert request.json == {'query': {'park': {'ids': ['parkid']}}}
        return {
            'parks': [
                {
                    'id': 'parkid',
                    'login': 'login',
                    'name': 'Тестовый Парк',
                    'is_active': True,
                    'city_id': 'Москва',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'country_id': 'rus',
                    'demo_mode': False,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    country_id = await cron_context.services.fleet_parks.get_park_info(
        profile=contractor.Profile(
            park_id='parkid', contractor_profile_id='profileid',
        ),
    )
    assert country_id == 'rus'
