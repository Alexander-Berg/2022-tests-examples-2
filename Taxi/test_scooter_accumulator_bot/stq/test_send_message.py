from scooter_accumulator_bot import utils

CHAT_ID = 'chat_id'
MESSAGE = 'message'
MESSAGE_FORMAT = 'html'


async def test_send_message(stq_runner, testpoint):
    @testpoint('bot_send_message')
    async def _testpoint_send_message(data):
        return data

    await stq_runner.scooter_accumulator_bot_send_message.call(
        task_id='task_id', args=(CHAT_ID, MESSAGE, MESSAGE_FORMAT),
    )

    sent_message = await _testpoint_send_message.wait_call()
    assert sent_message['data']['chat_id'] == CHAT_ID
    assert sent_message['data']['text'] == MESSAGE
    assert sent_message['data']['parse_mode'] == utils.get_parse_mode(
        MESSAGE_FORMAT,
    )
