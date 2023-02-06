import pytest


@pytest.mark.parametrize(
    'campaign_id, feed_id, result, result_feed_id',
    [
        (1, None, 200, 'feed_id_1'),
        (1, 'feed_id_1', 200, 'feed_id_2'),
        (2, None, 404, None),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_internal_import_export_bundle(
        web_context,
        web_app_client,
        campaign_id,
        feed_id,
        result,
        result_feed_id,
        patch,
        mockserver,
):
    @mockserver.json_handler('feeds-admin/v1/driver-wall/create')
    async def _(request):
        return {'id': 'feed_id_1'}

    @patch('crm_admin.utils.feed.copy_feed')
    async def _(*args, **kwargs):
        return 'feed_id_2'

    if feed_id:
        response = await web_app_client.post(
            '/v2/process/wall_draft',
            params={'campaign_id': campaign_id, 'feed_id': feed_id},
        )
    else:
        response = await web_app_client.post(
            '/v2/process/wall_draft', params={'campaign_id': campaign_id},
        )

    assert result == response.status

    if result == 200:
        assert (await response.json())['data'] == result_feed_id
