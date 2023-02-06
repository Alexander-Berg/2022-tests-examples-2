# pylint: disable=unused-argument,too-many-arguments,unused-variable

import pytest

from crm_admin import settings
from crm_admin import storage
from crm_admin.entity import error


@pytest.mark.parametrize(
    'campaign_id, status, msg',
    [
        (1, 201, 'success'),
        (2, 201, 'success'),
        (3, 400, 'not a regular campaign'),
        (4, 400, 'campaign is not active'),
        (5, 400, 'not found'),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_stop_regular_campaign(
        web_context, web_app_client, patch, campaign_id, status, msg,
):
    @patch('crm_admin.utils.startrek.trigger.on_regular')
    async def summon_on_regular(*args, **kwargs):
        pass

    @patch('crm_admin.utils.regular.common.send.cancel')
    async def cancel(*args, **kwargs):
        pass

    db_campaign = storage.DbCampaign(web_context)
    try:
        campaign = await db_campaign.fetch(campaign_id)

        sending_states = [
            settings.SENDING_PREPARE_STATE,
            settings.SENDING_PROCESSING_STATE,
        ]
        is_sending = campaign.state in sending_states
    except error.EntityNotFound:
        is_sending = False

    response = await web_app_client.post(
        '/v1/regular-campaigns/stop', params={'campaign_id': campaign_id},
    )
    assert response.status == status
    if msg:
        response = await response.json()
        assert msg in response.get('message', response.get('data', None))

    if response == 201:
        campaign = await db_campaign.fetch(campaign_id)
        assert not campaign.is_active
        assert campaign.state == settings.REGULAR_STOPPED

        if is_sending:
            assert cancel.calls
        else:
            assert not cancel.calls


@pytest.mark.pgsql('crm_admin', files=['draft_delete.sql'])
@pytest.mark.now('2020-03-20 10:00:00')
async def test_delete_draft(web_context, web_app_client, patch):
    @patch('crm_admin.utils.startrek.trigger.on_regular')
    async def summon_on_regular(*args, **kwargs):
        pass

    @patch('crm_admin.utils.regular.common.send.cancel')
    async def cancel(*args, **kwargs):
        pass

    response = await web_app_client.post(
        '/v1/regular-campaigns/stop', params={'campaign_id': 1},
    )

    assert response.status == 201

    db_campaign = storage.DbCampaign(web_context)
    draft_campaign = await db_campaign.fetch(2)

    assert draft_campaign.deleted_at
