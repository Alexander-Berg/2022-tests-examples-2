# pylint: disable=unused-variable

import pytest

from crm_admin import storage


@pytest.mark.parametrize(
    'campaign_id, has_extra_data, exists',
    [
        (1, True, True),
        (2, False, True),
        (3, False, True),
        (1, True, False),
        (2, False, False),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_get_extra_data_placeholders(
        web_context,
        web_app_client,
        patch,
        campaign_id,
        has_extra_data,
        exists,
):
    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def _get(path, *args, **kwargs):
        if 'extra' in path:
            columns = ['city', 'extra1']
        else:
            columns = ['key', 'city']
        return [{'name': col} for col in columns]

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def _exists(path, *args, **kwargs):
        return exists

    response = await web_app_client.get(
        '/v1/process/extra_data/placeholders', params={'id': campaign_id},
    )

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)

    if campaign.segment_id:
        assert response.status == 200

        columns = await response.json()
        if has_extra_data and exists:
            assert columns == ['key', 'city', 'extra1']
        elif exists:
            assert columns == ['key', 'city']
        else:
            assert columns == []
    else:
        assert response.status == 404
