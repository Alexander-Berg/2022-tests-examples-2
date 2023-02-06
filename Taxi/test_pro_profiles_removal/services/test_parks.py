from testsuite.utils import http

from pro_profiles_removal.entities import contractor
from pro_profiles_removal.generated.cron import cron_context as context


async def test_fire_profile(cron_context: context.Context, mock_parks):
    @mock_parks('/internal/driver-profiles/profile')
    async def _fire_profile(request: http.Request):
        assert request.query == {'park_id': 'parkid', 'id': 'profileid'}
        assert request.json == {
            'driver_profile': {'set': {'work_status': 'fired'}},
        }
        return {
            'driver_profile': {
                'id': 'profileid',
                'park_id': 'parkid',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phones': ['phone'],
                'work_status': 'fired',
            },
        }

    await cron_context.services.parks.fire_profile(
        profile=contractor.Profile(
            park_id='parkid', contractor_profile_id='profileid',
        ),
    )
