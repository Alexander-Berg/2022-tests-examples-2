import pytest

from crm_admin import settings
from crm_admin import storage


@pytest.mark.parametrize(
    'campaign_id, result', [(2, 200), (3, 400), (6, 424), (7, 400)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_apply_draft(web_context, web_app_client, campaign_id, result):
    response = await web_app_client.post(
        '/v1/campaigns/cancel_draft', params={'campaign_id': campaign_id},
    )

    assert response.status == result

    if result == 200:
        db_campaign = storage.DbCampaign(web_context)
        db_draft_applying = storage.DbDraftApplying(web_context)

        draft_campaign = await db_campaign.fetch(campaign_id)

        assert draft_campaign
        assert draft_campaign.state == settings.APPROVED_STATE

        draft_applying = await db_draft_applying.fetch_by_draft_campaign_id(
            draft_campaign.campaign_id,
        )

        assert not draft_applying
