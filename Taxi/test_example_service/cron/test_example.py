# pylint: disable=redefined-outer-name
from aiohttp import web

from example_service.generated.cron import run_cron


async def test_example(mock_yet_another_service):
    @mock_yet_another_service('/ping')
    def ping_handler(request):
        return web.json_response()

    await run_cron.main(['example_service.crontasks.example', '-t', '0'])
    assert ping_handler.times_called == 1
