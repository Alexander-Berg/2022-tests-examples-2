from aiohttp import web
import pytest


async def test_example_task(cron_runner, mock_yet_another_service):
    @mock_yet_another_service('/ping')
    def ping_handler(request):
        return web.json_response()

    await cron_runner.example()
    assert ping_handler.times_called == 1


async def test_always_failed_task(cron_runner):
    with pytest.raises(RuntimeError, match='Task \'always_failed\' failed'):
        await cron_runner.always_failed()


@pytest.mark.now('2000-01-01T03:00:00+03:00')
async def test_check_now_task(cron_runner):
    await cron_runner.check_now()
