from aiohttp import web
import pytest

from clownductor.generated.cron import run_cron


@pytest.mark.pgsql('clownductor', files=['add_test_data.sql'])
async def test_create_remote_jobs(mock_task_processor):
    @mock_task_processor('/v1/jobs/start/')
    # pylint: disable=W0612
    async def handler(request):  # pylint: disable=unused-argument
        return web.json_response({'job_id': 1})

    await run_cron.main(
        ['clownductor.crontasks.create_remote_jobs', '-t', '0'],
    )

    assert handler.times_called == 2
