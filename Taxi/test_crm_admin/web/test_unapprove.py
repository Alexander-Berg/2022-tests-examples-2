import pytest


from crm_admin import settings
from crm_admin import storage


@pytest.mark.parametrize('campaign_id, result', [(1, 200), (2, 424), (3, 404)])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_unapprove(
        web_context,
        web_app_client,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        campaign_id,
        result,
):
    ticket = 'CRMTEST-1'
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']
    url = st_settings['robot-crm-admin']['url'] + f'issues/{ticket}/comments'

    @patch_aiohttp_session(url, 'POST')
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['text'] == 'Отмена согласования'
        return response_mock(json={})

    response = await web_app_client.post(
        '/v1/campaigns/unapprove', params={'id': campaign_id},
    )

    campaign_response = await response.json()

    assert response.status == result

    if result == 200:
        assert campaign_response['state'] == settings.GROUPS_RESULT_STATE
        assert patch_issue.calls

        db_campaign = storage.DbCampaign(web_context)
        campaign = await db_campaign.fetch(campaign_id)

        assert campaign.state == settings.GROUPS_RESULT_STATE
    elif result == 424:
        assert not patch_issue.calls

        db_campaign = storage.DbCampaign(web_context)
        campaign = await db_campaign.fetch(campaign_id)

        assert campaign.state == settings.VERIFY_RESULT_STATE
