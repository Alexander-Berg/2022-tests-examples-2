from testsuite.utils import http

from pro_profiles_removal.entities import contractor
from pro_profiles_removal.generated.cron import cron_context as context


async def test_add_block(cron_context: context.Context, mock_driver_login):
    @mock_driver_login('/driver-login/v1/bulk-logout')
    async def _logout(request: http.Request):
        assert request.json == {
            'comment': 'comment',
            'is_full_logout': True,
            'drivers': [
                {'park_id': 'parkid', 'driver_profile_id': 'profileid'},
            ],
        }
        return {
            'drivers': [
                {
                    'driver': {
                        'park_id': 'parkid',
                        'driver_profile_id': 'profileid',
                    },
                    'is_logged_out': True,
                },
            ],
        }

    profiles = await cron_context.services.driver_login.logout(
        is_full_logout=True,
        comment='comment',
        profiles=[
            contractor.Profile(
                park_id='parkid', contractor_profile_id='profileid',
            ),
        ],
    )
    assert len(profiles) == 1
    assert profiles[0].is_logged_out
