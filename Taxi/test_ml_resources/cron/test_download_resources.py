# pylint: disable=redefined-outer-name
from aiohttp import web
import pytest

from ml_resources.generated.cron import run_cron


@pytest.mark.skip(reason='only for local debugging')
async def test_common_case(simple_secdist, load_json, mock_sandbox_py3):
    @mock_sandbox_py3('/api/v1.0/resource/1042955551')
    async def _resource_handler(request):
        return web.json_response(load_json('resource_1042955551.json'))

    @mock_sandbox_py3('/api/v1.0/resource')
    async def _snapshot_handler(request):
        return web.json_response(
            load_json('sandbox_resp.json'), headers={'X-Matched-Records': '1'},
        )

    await run_cron.main(
        ['ml_resources.crontasks.download_resources', '-t', '0'],
    )
