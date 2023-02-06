import pytest

from crm_admin.generated.cron import run_cron
from crm_admin.storage import campaign_results as db_storage

CRM_ADMIN_SETTINGS = {
    'CampaignResultsSettings': {'yt_path': '//home/yt_camaign_results'},
}


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.yt(static_table_data=['yt_campaign_results.yaml'])
async def test_success(yt_apply, yt_client, web_context):

    await run_cron.main(['crm_admin.crontasks.campaign_results', '-t', '0'])

    obj = db_storage.DbCampaignResults(web_context)
    ret = await obj.fetch_campaign(51)
    assert len(ret) == 3
    ret = await obj.fetch_campaign(52)
    assert len(ret) == 1
    ret = await obj.fetch_campaign(53)
    assert not ret
