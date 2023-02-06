# pylint: disable=no-member
from taxi_support_chat.generated.cron import run_cron


async def test_send_driver_chat_push(cron_context, loop, stq):
    await run_cron.main(
        ['taxi_support_chat.crontasks.send_driver_chat_push', '-t', '0'],
    )

    db = cron_context.mongo
    chats = await db.user_chat_messages.find(
        {'open': True, 'visible': True, 'send_push': True}, ['_id'],
    ).to_list(None)

    assert chats == [{'_id': 'client_chat_message'}]

    calls = []
    while not stq.is_empty:
        calls.append(stq.driver_support_push.next_call())

    assert len(calls) == 2

    call_args = calls[0]
    call_args.pop('kwargs')
    assert call_args['queue'] == 'driver_support_push'
    assert call_args['args'][0] == 'visible_open_driver_chat_message_send_push'

    call_args = calls[1]
    call_args.pop('kwargs')
    assert call_args['queue'] == 'driver_support_push'
    assert (
        call_args['args'][0] == 'visible_open_driver_chat_message_send_push_2'
    )
