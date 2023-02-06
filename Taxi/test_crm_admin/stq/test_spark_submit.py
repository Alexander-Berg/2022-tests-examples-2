# pylint: disable=unused-argument,unused-variable
import unittest.mock

import pytest

from crm_admin.utils.spark import spark_submit

CRM_ADMIN_TEST_SETTINGS = {
    'SparkSettings': {
        'discovery_path': 'discovery_path',
        'spark3_discovery_path': 'spark3_discovery_path',
    },
}


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
async def test_spark_submit_no_wait(stq3_context, patch):
    @patch('crm_admin.utils.spark.spark_submit.spyt.submit.java_gateway')
    def java_gateway():
        return unittest.mock.MagicMock()

    @patch('crm_admin.generated.stq3.yt_wrapper.plugin.AsyncYTClient.create')
    async def create(*args, **kwargs):
        pass

    @patch(
        'crm_admin.generated.stq3.yt_wrapper.plugin.AsyncYTClient.write_file',
    )
    async def write_file(path, *args, **kwargs):
        pass

    @patch('spyt.submit.SparkSubmissionClient.submit')
    def submit(*args, **kwargs):
        return 123

    job_config = {'campaign_id': 1}
    submission_id = await spark_submit.spark_submit_no_wait(
        stq3_context,
        'quicksegment.py',
        app_name='quicksegment',
        job_config=job_config,
    )

    assert submission_id == 123
    assert write_file.call['path'].endswith('quicksegment.py')
    assert write_file.call['path'].endswith('config.json')
    assert java_gateway.calls


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
async def test_spark_submit_error(stq3_context, patch):
    @patch('crm_admin.utils.spark.spark_submit.spyt.submit.java_gateway')
    def java_gateway():
        raise OSError('Argument list too long: \'java\'')

    @patch('crm_admin.generated.stq3.yt_wrapper.plugin.AsyncYTClient.create')
    async def create(*args, **kwargs):
        pass

    @patch(
        'crm_admin.generated.stq3.yt_wrapper.plugin.AsyncYTClient.write_file',
    )
    async def write_file(path, *args, **kwargs):
        pass

    @patch('spyt.submit.SparkSubmissionClient.submit')
    def submit(*args, **kwargs):
        return 123

    job_config = {'campaign_id': 1}
    submission_id = await spark_submit.spark_submit_no_wait(
        stq3_context,
        'quicksegment.py',
        app_name='quicksegment',
        job_config=job_config,
    )

    assert submission_id is None
    assert write_file.call['path'].endswith('quicksegment.py')
    assert write_file.call['path'].endswith('config.json')
    assert java_gateway.calls


@pytest.mark.parametrize(
    'response, status',
    [
        ({''}, 'POLLING_ERROR'),
        ({'success': False}, 'NOT_FOUND'),
        ({'success': True, 'driverState': 'RUNNING'}, 'RUNNING'),
    ],
)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
async def test_spark_poll(
        stq3_context,
        response,
        status,
        patch,
        patch_aiohttp_session,
        response_mock,
):
    @patch('crm_admin.generated.stq3.yt_wrapper.plugin.AsyncYTClient.list')
    async def yt_list(path, *args, **kwargs):
        return 'rest-api-endpoint'

    @patch_aiohttp_session(
        await spark_submit.get_rest_endpoint(stq3_context), 'GET',
    )
    def get_status(*args, **kwargs):
        return response_mock(json=response)

    assert await spark_submit.poll(stq3_context, 'submission_id') == status


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
async def test_spark_discovery_path(stq3_context, patch):
    assert (
        spark_submit.spark_discovery_path(stq3_context)
        == CRM_ADMIN_TEST_SETTINGS['SparkSettings']['spark3_discovery_path']
    )
