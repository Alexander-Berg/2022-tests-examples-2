# pylint: disable=redefined-outer-name,unused-variable

import pytest

from taxi.maintenance import run


@pytest.fixture(name='statistics', autouse=True)
async def _statictics(mock_statistics, statistics, cron_context):
    class Statistics:
        def __init__(self, context, mock_statistics):
            self._dumped = []
            self._context = context

            @mock_statistics('/v1/metrics/store')
            async def _handler(request):
                self._dumped.append(request.json)
                return {}

            self.handler = _handler

        async def dump(self):
            # pylint: disable=protected-access
            await self._context.clients.statistics._send()
            result = self._dumped
            self._dumped = []
            return result

    return Statistics(cron_context, mock_statistics)


@pytest.fixture(autouse=True)
async def vgw_api_tasks_mock_s3(mds_s3_client, patch):
    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _upload_content(key, body, *args, **kwargs):
        return await mds_s3_client.upload_content(key, body, *args, **kwargs)

    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _download_content(key, *args, **kwargs):
        return await mds_s3_client.download_content(key)


@pytest.fixture
def patch_task_id(patch):
    original_run_task = run.run_task

    def _patch_task_id(value):
        @patch('taxi.maintenance.run.run_task')
        async def run_task(task, *args, **kwargs):
            task.id = value
            # pylint: disable=missing-kwoa
            return await original_run_task(task, *args, **kwargs)

    return _patch_task_id
