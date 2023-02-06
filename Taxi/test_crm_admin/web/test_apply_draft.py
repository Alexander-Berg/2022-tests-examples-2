# pylint: disable=redefined-outer-name,unused-variable,too-many-lines
import pytest

from crm_admin import settings
from crm_admin import storage


@pytest.mark.parametrize('campaign_id, result', [(2, 200), (3, 400), (4, 400)])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_apply_draft(
        web_context, patch, web_app_client, campaign_id, result,
):
    @patch(
        'crm_admin.utils.validation.groupings.campaign_pre_start_validation',
    )
    async def validate(*args, **kwargs):
        return []

    response = await web_app_client.post(
        '/v1/campaigns/apply_draft',
        params={'campaign_id': campaign_id},
        headers={'X-Yandex-Login': 'trusienkodv'},
    )

    assert response.status == result

    if result == 200:
        db_campaign = storage.DbCampaign(web_context)
        db_draft_applying = storage.DbDraftApplying(web_context)

        draft_campaign = await db_campaign.fetch(campaign_id)

        assert draft_campaign
        assert draft_campaign.state == settings.APPLYING_DRAFT

        draft_applying = await db_draft_applying.fetch_by_draft_campaign_id(
            draft_campaign.campaign_id,
        )

        assert draft_applying
        assert draft_applying.draft_campaign_id == draft_campaign.campaign_id
        assert not draft_applying.is_applied
