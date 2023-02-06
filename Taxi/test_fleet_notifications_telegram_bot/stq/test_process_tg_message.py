import pytest


PERSONAL_ID_TO_TG_ID = {'pd1': '1', 'pd2': '2'}
SUCCESS = 'Регистрация успешна! Уведомления будут приходить сюда'
UNSUCCESS = 'Регистрация не удалась. Запросите новую ссылку'


def get_telegram_pd_id_with_token(pgsql, token):
    db = pgsql['fleet_notifications_telegram_bot'].cursor()
    db.execute(
        'SELECT telegram_pd_id '
        'FROM fleet_notifications_telegram_bot.tg_users_info '
        f'WHERE registered_with_token = \'{token}\'',
    )
    result = list(db)
    return result[0][0] if result else None


@pytest.mark.pgsql(
    'fleet_notifications_telegram_bot',
    files=['pg_fleet_notifications_telegram_bot.sql'],
)
@pytest.mark.parametrize(
    'telegram_pd_id, message, answer',
    [
        pytest.param('pd1', '/start token2', SUCCESS, id='Register user'),
        pytest.param(
            'pd2', '/start token1', UNSUCCESS, id='Token already registered',
        ),
        pytest.param('pd2', '/start no_tok', UNSUCCESS, id='No token'),
        pytest.param('pd2', '/start token3', UNSUCCESS, id='Old token'),
    ],
)
async def test_process_tg_message(
        stq_runner,
        testpoint,
        telegram_pd_id,
        message,
        answer,
        personal,
        telegram,
        pgsql,
):
    @testpoint('bot_send_message')
    async def _testpoint_send_message(data):
        return data

    personal.set_personal_to_tg_id(PERSONAL_ID_TO_TG_ID)

    await stq_runner.fleet_notifications_telegram_bot_process_telegram_message.call(  # noqa: E501 (line too long)
        task_id='task_id', args=[telegram_pd_id, message],
    )

    sent_message = await _testpoint_send_message.wait_call()
    assert sent_message['data']['chat_id'] == int(
        PERSONAL_ID_TO_TG_ID[telegram_pd_id],
    )
    assert sent_message['data']['text'] == answer

    registered_telegram_pd_id = get_telegram_pd_id_with_token(
        pgsql, message.split()[-1],
    )

    if answer == SUCCESS:
        assert telegram_pd_id == registered_telegram_pd_id
    else:
        assert (
            not registered_telegram_pd_id
            or telegram_pd_id != registered_telegram_pd_id
        )
