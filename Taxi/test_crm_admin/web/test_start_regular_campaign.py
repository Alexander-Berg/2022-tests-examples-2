# pylint: disable=unused-argument,too-many-arguments

import pytest

from crm_admin import settings
from crm_admin import storage


@pytest.fixture(autouse=True)
def skip_parametrization_validation(patch):
    @patch(
        'crm_admin.utils.validation'
        '.extra_data_validators.validate_personalization_params',
    )
    async def validation(*agrs, **kwargs):  # pylint: disable=unused-variable
        return []


@pytest.mark.parametrize(
    'campaign_id, status, msg',
    [
        (1, 201, 'success'),
        (10, 201, 'success'),
        (11, 201, 'success'),
        (12, 201, 'success'),
        (2, 400, 'campaign is stopped'),
        (3, 400, 'campaign is already activ'),
        (4, 400, 'not a regular campaign'),
        (5, 400, 'must be approved'),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.now('2021-05-05 05:05:05')
async def test_start_regular_campaign(
        web_context, web_app_client, campaign_id, status, msg,
):
    response = await web_app_client.post(
        '/v1/regular-campaigns/start', params={'campaign_id': campaign_id},
    )
    assert response.status == status
    if msg:
        response = await response.json()
        assert msg in response.get('message', response.get('data', None))

    if response == 201:
        db_campaign = storage.DbCampaign(web_context)
        campaign = await db_campaign.fetch(campaign_id)
        assert campaign.is_active
        assert campaign.state == settings.REGULAR_SCHEDULED


@pytest.mark.parametrize('campaign_id, status, msg', [(1, 201, 'success')])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.now('2021-05-05 05:05:05')
async def test_user_login(
        web_context, web_app_client, campaign_id, status, msg, patch,
):
    # pylint: disable=unused-variable,
    @patch('crm_admin.utils.validation.serializers.process_campaign_errors')
    async def process_campaign_errors(
            context, campaign_id, user_login, *args, **kwargs,
    ):
        assert user_login == 'test'

    await web_app_client.post(
        '/v1/regular-campaigns/start',
        params={'campaign_id': campaign_id},
        headers={'X-Yandex-Login': 'test'},
    )
