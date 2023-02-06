import pytest

from crm_admin import settings
from crm_admin import storage
from test_crm_admin.utils import campaign as cutils

CAN_BE_CANCELED = [
    settings.NEW_CAMPAIGN,
    settings.SEGMENT_EXPECTED_STATE,
    settings.SEGMENT_PROCESSING_STATE,
    settings.SEGMENT_RESULT_STATE,
    settings.SEGMENT_ERROR,
    settings.GROUPS_READY_FOR_CALCULATION,
    settings.GROUPS_EXPECTED_STATE,
    settings.GROUPS_CALCULATING_STATE,
    settings.GROUPS_RESULT_STATE,
    settings.GROUPS_ERROR,
    settings.VERIFY_EXPECTED_STATE,
    settings.VERIFY_PREPARE_STATE,
    settings.VERIFY_PROCESSING_STATE,
    settings.VERIFY_RESULT_STATE,
    settings.VERIFY_ERROR,
    settings.APPROVED_STATE,
    settings.SENDING_EXPECTED_STATE,
    settings.SENDING_ERROR,
]

CAN_NOT_BE_CANCELED = [
    settings.SENDING_PREPARE_STATE,
    settings.SENDING_PROCESSING_STATE,
    settings.SENDING_RESULT_STATE,
    settings.CANCELED,
]

CRM_ADMIN_SETTINGS = {
    'StartrekSettings': {
        'campaign_queue': 'CRMTEST',
        'creative_queue': 'CRMTEST',
        'idea_approved_statuses': [
            'idea_approved_state',
            'final_approved_state',
        ],
        'target_statuses': ['Одобрено', 'Закрыт'],
        'unapproved_statuses': ['В работе'],
        'agreement_statuses': ['Согласование', 'Требует согласования'],
    },
}


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_countries_list(web_context, web_app_client):
    db_campaign = storage.DbCampaign(web_context)

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context, entity='User',
    )
    campaign_id = campaign.campaign_id

    for state in CAN_BE_CANCELED:
        campaign.state = state
        await db_campaign.update_state(campaign)

        response = await web_app_client.post(
            f'/v1/process/cancel?id={campaign_id}',
        )
        assert response.status == 200

        fetched = await db_campaign.fetch(campaign_id)
        assert fetched.state == settings.CANCELED

    for state in CAN_NOT_BE_CANCELED:
        campaign.state = state
        await db_campaign.update_state(campaign)

        response = await web_app_client.post(
            f'/v1/process/cancel?id={campaign_id}',
        )
        assert response.status == 404
        answer = await response.json()
        assert 'Campaign state' in answer['message']

        fetched = await db_campaign.fetch(campaign_id)
        assert fetched.state == state


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['draft_delete.sql'])
@pytest.mark.now('2020-03-20 10:00:00')
@pytest.mark.parametrize('campaign_id, status', [(2, 200), (4, 400)])
async def test_delete_draft(
        web_context, web_app_client, patch, campaign_id, status,
):

    response = await web_app_client.post(
        f'/v1/process/cancel?id={campaign_id}',
    )

    assert response.status == status

    if status == 200:
        db_campaign = storage.DbCampaign(web_context)
        draft_campaign = await db_campaign.fetch(campaign_id)

        assert draft_campaign.deleted_at
