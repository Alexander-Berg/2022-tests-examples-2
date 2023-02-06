import pytest

from crm_admin import settings
from crm_admin import storage
from crm_admin.utils.spark import spark_submit

CRM_ADMIN_TEST_SETTINGS = {
    'SparkSettings': {
        'discovery_path': 'discovery_path',
        'spark3_discovery_path': 'spark3_discovery_path',
    },
}


async def get_campaign_state(context, campaign_id):
    db_campaign = storage.DbCampaign(context)
    campaign = await db_campaign.fetch(campaign_id=campaign_id)
    return campaign.state


# ********************************************************************************
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_bad_campaing_id(web_app_client):
    campaign_id = -1
    response = await web_app_client.post(
        '/v1/terminate/segmenting', params={'id': campaign_id},
    )
    assert response.status == 404
    data = await response.json()
    assert data == {'message': 'Campaign -1 was not found'}


# ********************************************************************************
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_bad_campaing_state(web_app_client):
    campaign_id = 6
    response = await web_app_client.post(
        '/v1/terminate/segmenting', params={'id': campaign_id},
    )
    assert response.status == 404
    data = await response.json()
    assert 'Campaign state \'OTHER_STATE\' is not' in data['message']


# ********************************************************************************
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_operations_not_started(web_app_client, web_context):
    campaign_id = 7
    response = await web_app_client.post(
        '/v1/terminate/segmenting', params={'id': campaign_id},
    )
    assert response.status == 200

    # Change state only
    state = await get_campaign_state(web_context, campaign_id)
    assert state == settings.SEGMENT_CANCELLING


# ********************************************************************************
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_operations_empty(web_app_client, web_context):
    campaign_id = 2
    response = await web_app_client.post(
        '/v1/terminate/segmenting', params={'id': campaign_id},
    )
    assert response.status == 404

    data = await response.json()
    assert data == {'message': 'No operations for the campaign 2.'}


# ****************************************************************************
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_no_active_calcs(web_app_client, web_context):
    campaign_id = 3
    response = await web_app_client.post(
        '/v1/terminate/segmenting', params={'id': campaign_id},
    )
    assert response.status == 200


# ****************************************************************************
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_kill_spark(
        web_app_client,
        web_context,
        patch,
        patch_aiohttp_session,
        response_mock,
):
    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.list')
    async def _yt_list(path, *args, **kwargs):
        return 'rest-api-endpoint'

    @patch_aiohttp_session(
        await spark_submit.get_rest_endpoint(web_context), 'POST',
    )
    def _kill_query(*args, **kwargs):
        return response_mock(json={'success': True})

    campaign_id = 1
    response = await web_app_client.post(
        '/v1/terminate/segmenting', params={'id': campaign_id},
    )

    assert response.status == 200
    assert len(_kill_query.calls) == 1  # only last operation killed

    state = await get_campaign_state(web_context, campaign_id)
    assert state == settings.SEGMENT_CANCELLING


# ****************************************************************************
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_kill_yql(web_app_client, web_context, patch):
    @patch('yql.client.operation.YqlAbortOperationRequest')
    def _yql_operation_abort_request(operation_id):
        class YQLRequest:
            json = {}
            is_success = False
            status = 'ABORTED'

            def run(self):
                pass

        return YQLRequest()

    campaign_id = 4
    response = await web_app_client.post(
        '/v1/terminate/segmenting', params={'id': campaign_id},
    )

    assert response.status == 200
    # only last operation killed
    assert len(_yql_operation_abort_request.calls) == 1

    state = await get_campaign_state(web_context, campaign_id)
    assert state == settings.SEGMENT_CANCELLING


# ****************************************************************************
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_kill_yql_error(web_app_client, web_context, patch):
    @patch('yql.client.operation.YqlAbortOperationRequest')
    def _yql_operation_abort_request(operation_id):
        class YQLRequest:
            json = {}
            is_success = False
            status = 'ERROR'

            def run(self):
                pass

        return YQLRequest()

    campaign_id = 4
    response = await web_app_client.post(
        '/v1/terminate/segmenting', params={'id': campaign_id},
    )

    assert response.status == 200


# ****************************************************************************
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_kill_spark_error(
        web_app_client,
        web_context,
        patch,
        patch_aiohttp_session,
        response_mock,
):
    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.list')
    async def _yt_list(path, *args, **kwargs):
        return 'rest-api-endpoint'

    @patch_aiohttp_session(
        await spark_submit.get_rest_endpoint(web_context), 'POST',
    )
    def _kill_query(*args, **kwargs):
        return response_mock(json={'success': False, 'message': 'err_msg'})

    campaign_id = 1
    response = await web_app_client.post(
        '/v1/terminate/segmenting', params={'id': campaign_id},
    )

    assert response.status == 200
