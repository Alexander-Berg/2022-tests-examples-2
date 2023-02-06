# pylint: disable=no-member
import pytest

from taxi_support_chat.generated.cron import run_cron


@pytest.mark.now('2019-10-31T12:00:00+0')
async def test_retry_csat_request(cron_context, stq):
    expected_results = [
        {
            'id': 'visible_open_driver_support_read',
            'message_key': 'user_chat.retry_csat_with_read_messages',
        },
        {
            'id': 'visible_open_driver_support_read_none',
            'message_key': 'user_chat.retry_csat_with_read_messages',
        },
        {
            'id': 'visible_open_driver_support_unread',
            'message_key': 'user_chat.retry_csat_with_unread_messages',
        },
    ]
    expected_ids = {
        'visible_open_driver_support_read',
        'visible_open_driver_support_read_none',
        'visible_open_driver_support_unread',
    }

    db = cron_context.mongo
    old_chats = await db.user_chat_messages.find().sort('id', 1).to_list(None)
    await run_cron.main(
        ['taxi_support_chat.crontasks.retry_csat_request', '-t', '0'],
    )
    chats = await db.user_chat_messages.find().sort('id', 1).to_list(None)
    for i, chat in enumerate(chats):
        if chat['_id'] in expected_ids:
            assert not chat['retry_csat_request']
            assert chat['updated']
            chat.pop('updated')
            chat['retry_csat_request'] = True
        assert chat == old_chats[i]
    calls = []
    while not stq.is_empty:
        calls.append(stq.driver_support_push.next_call())

    assert len(calls) == 3
    calls = sorted(calls, key=lambda item: item['args'][0])
    for i, call in enumerate(calls):
        assert call['queue'] == 'driver_support_push'
        assert call['args'][0] == expected_results[i]['id']
        assert (
            call['kwargs']['message_key'] == expected_results[i]['message_key']
        )
