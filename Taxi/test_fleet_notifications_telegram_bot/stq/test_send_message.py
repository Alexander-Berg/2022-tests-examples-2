import pytest


TELEGRAM_PD_ID = 'pd1'
MESSAGE = 'MessageBlaBlaBlaBla'

PERSONAL_ID_TO_TG_ID = {'pd1': '123'}


@pytest.mark.config(
    FLEET_NOTIFICATIONS_TELEGRAM_BOT_MESSAGE_SETTINGS_V2={
        'max_message_to_send_len': 20,
        'stq_amount_in_one_builder': 1,
    },
)
@pytest.mark.parametrize('parse_mode', ('html', None))
async def test_send_message(
        stq_runner, testpoint, personal, parse_mode, telegram,
):
    @testpoint('bot_send_message')
    async def _testpoint_send_message(data):
        return data

    personal.set_personal_to_tg_id(PERSONAL_ID_TO_TG_ID)

    await stq_runner.fleet_notifications_telegram_bot_send_message.call(
        task_id='task_id', args=(TELEGRAM_PD_ID, MESSAGE, parse_mode),
    )

    sent_message = await _testpoint_send_message.wait_call()
    assert sent_message['data']['chat_id'] == int(PERSONAL_ID_TO_TG_ID['pd1'])
    assert sent_message['data']['text'] == MESSAGE
    assert sent_message['data']['markup_language'] == parse_mode
