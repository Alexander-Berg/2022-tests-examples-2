# pylint: disable=no-member
import pytest

from taxi_support_chat.generated.cron import run_cron

EXPECTED_MESSAGE_IDS = {'some_good_message_id_1', 'some_good_message_id_3'}


@pytest.mark.now('2018-10-07T11:31:00+0')
@pytest.mark.config(FORCE_CREATE_CHATTERBOX_TICKET_STUFF=True)
async def test_force_create_tasks(stq):
    await run_cron.main(
        ['taxi_support_chat.crontasks.force_create_tasks', '-t', '0'],
    )

    create_message_calls = []
    while not stq.is_empty:
        call = stq.user_support_chat_message.next_call()
        if call['queue'] == 'user_support_chat_message':
            create_message_calls.append(call)

    assert EXPECTED_MESSAGE_IDS == set(
        map(lambda call: call['args'][1], create_message_calls),
    )
