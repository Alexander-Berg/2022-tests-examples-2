from testsuite.utils import http

from pro_profiles_removal.entities import contractor
from pro_profiles_removal.generated.cron import cron_context as context


async def test_get_display_profile(
        cron_context: context.Context, mock_driver_ui_profile,
):
    @mock_driver_ui_profile('/v1/mode')
    def _v1_mode(request: http.Request):
        assert request.query['park_id'] == 'parkid'
        assert request.query['driver_profile_id'] == 'profileid'
        assert request.query['concern'] == 'cached'
        return {
            'display_mode': 'display_mode',
            'display_profile': 'display_profile',
        }

    display_profile = (
        await cron_context.services.driver_ui_profile.get_ui_mode(
            profile=contractor.Profile(
                park_id='parkid', contractor_profile_id='profileid',
            ),
        )
    )
    assert display_profile == 'display_profile'
