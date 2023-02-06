# pylint: disable=no-member
import datetime

import pytest

from taxi import discovery

from taxi_support_chat.generated.cron import run_cron


@pytest.mark.now('2018-01-01T00:00:00')
async def test_close_disabled(cron_context, loop):
    db = cron_context.mongo
    query = {'open': False, 'visible': False, 'close_ticket': True}
    close_count_before = await db.user_chat_messages.count(query)
    await run_cron.main(
        ['taxi_support_chat.crontasks.close_chatterbox_tasks', '-t', '0'],
    )
    close_count_after = await db.user_chat_messages.count(query)
    assert close_count_after == close_count_before


async def _check_chats(cron_context, stq, call_counter):
    assert call_counter == 2
    assert stq.taxi_support_chat_opteum_notify.times_called == 1
    call_args = stq.taxi_support_chat_opteum_notify.next_call()
    call_args['kwargs'].pop('log_extra')
    assert call_args == {
        'queue': 'taxi_support_chat_opteum_notify',
        'args': ['opteum_closed_chat', ''],
        'kwargs': {'update_type': 'update'},
        'id': 'opteum_closed_chat',
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
    }


@pytest.mark.config(ENABLE_CLOSE_CHATTERBOX_CHAT_PY2=False)
@pytest.mark.now('2018-01-01T00:00:00')
async def test_close_tasks(
        cron_context, loop, response_mock, patch_aiohttp_session, stq,
):
    chatterbox_service = discovery.find_service('chatterbox')

    call_counter = 0
    # pylint: disable=unused-variable
    @patch_aiohttp_session(chatterbox_service.url, 'POST')
    def patch_request(method, url, **kwargs):
        nonlocal call_counter
        assert method == 'post'
        assert url == '%s/v1/tasks' % chatterbox_service.url
        assert kwargs['json']['type'] == 'chat'
        assert kwargs['json']['external_id'] in [
            'closed_chat',
            'opteum_closed_chat',
        ]
        call_counter += 1
        return response_mock()

    await run_cron.main(
        ['taxi_support_chat.crontasks.close_chatterbox_tasks', '-t', '0'],
    )
    await _check_chats(cron_context, stq, call_counter)


@pytest.mark.config(ENABLE_CLOSE_CHATTERBOX_CHAT_PY2=False)
@pytest.mark.now('2018-01-01T00:00:00')
async def test_close_tasks_gone(
        cron_context, loop, response_mock, patch_aiohttp_session, stq,
):
    chatterbox_service = discovery.find_service('chatterbox')

    call_counter = 0
    # pylint: disable=unused-variable
    @patch_aiohttp_session(chatterbox_service.url, 'POST')
    def patch_request(method, url, **kwargs):
        nonlocal call_counter
        assert method == 'post'
        assert url == '%s/v1/tasks' % chatterbox_service.url
        assert kwargs['json']['type'] == 'chat'
        assert kwargs['json']['external_id'] in [
            'closed_chat',
            'opteum_closed_chat',
        ]
        call_counter += 1
        return response_mock(status=410)

    await run_cron.main(
        ['taxi_support_chat.crontasks.close_chatterbox_tasks', '-t', '0'],
    )
    await _check_chats(cron_context, stq, call_counter)
