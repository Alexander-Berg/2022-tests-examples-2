# pylint: disable=unused-variable
from aiohttp import web
import pytest

from infra_events.common import bot


@pytest.mark.config(INFRA_EVENTS_FEATURES={'notify_bot': False})
@pytest.mark.config(INFRA_EVENTS_VIEWS={'taxi': {}})
async def test_bot_send_message_feature(mock_infra_bot_api, cron_context):
    @mock_infra_bot_api('/api/queue')
    def handler(request):
        raise AssertionError('Feature disabled, but handle was called')

    await bot.send_message(
        context=cron_context, view='taxi', message='test message',
    )


@pytest.mark.config(INFRA_EVENTS_FEATURES={'notify_bot': True})
@pytest.mark.config(INFRA_EVENTS_VIEWS={'taxi': {}})
async def test_bot_send_message_ignore_error(mock_infra_bot_api, cron_context):
    @mock_infra_bot_api('/api/queue')
    def handler(request):
        return web.json_response({}, status=500)

    await bot.send_message(
        context=cron_context, view='taxi', message='test message',
    )


@pytest.mark.config(INFRA_EVENTS_FEATURES={'notify_bot': True})
@pytest.mark.config(INFRA_EVENTS_VIEWS={'taxi': {}})
async def test_bot_send_message_check_view(cron_context):
    raised = False
    try:
        await bot.send_message(
            context=cron_context, view='some_view', message='test message',
        )
    except ValueError:
        raised = True
    assert raised
