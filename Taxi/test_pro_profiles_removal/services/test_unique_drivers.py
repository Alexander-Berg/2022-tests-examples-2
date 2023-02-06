import pytest

from testsuite.utils import http

from pro_profiles_removal.entities import contractor
from pro_profiles_removal.generated.cron import cron_context as context


@pytest.mark.config(
    PRO_PROFILES_REMOVAL_DRAFT_INFO={
        'description': 'draft description',
        'author': 'author',
        'summon_users': ['summon_user'],
        'ticket_info': {
            'description': 'ticket description',
            'summary': 'ticket summary',
        },
        'link_to_profile': (
            'https://tariff-editor.taxi.tst.yandex-team.ru/show-driver?uuid='
        ),
    },
)
async def test_remove_profiles(
        cron_context: context.Context, mock_unique_drivers,
):
    @mock_unique_drivers('/internal/unique-drivers/v1/remove-profiles')
    async def _remove_profiles(request: http.Request):
        assert request.query == {'consumer': 'pro-profiles-removal'}
        assert request.headers['X-Yandex-Login'] == 'author'
        assert request.json == {'profile_id_in_set': ['parkid_profileid']}
        return {}

    await cron_context.services.unique_drivers.remove_profiles(
        profiles=[
            contractor.Profile(
                park_id='parkid', contractor_profile_id='profileid',
            ),
        ],
    )
