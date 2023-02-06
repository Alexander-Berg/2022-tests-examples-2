import pytest

from taxi.stq import async_worker_ng

from test_workforce_management_bot import data
from workforce_management_bot.stq import send


START_REQUEST_MESSAGE = {
    'message': {
        'chat': {'id': 1},
        'from': {'username': 'roma'},
        'text': '/start',
    },
}


@pytest.mark.translations(wfm_backend_tg_bot=data.DEFAULT_TRANSLATION)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_BOT_EMOJIES={
        'emoji_heart': 'heavy black heart',
        'emoji_calendar': 'calendar',
        'emoji_coffee': 'hot beverage',
        'emoji_lunch': 'fork and knife',
    },
)
async def test_stq_message_sending(
        stq3_context, mock_wfm, web_app_client, mock_bot_class,
):
    mock_wfm()

    await web_app_client.post('/v1/webhook', json=START_REQUEST_MESSAGE)
    assert (
        mock_bot_class.calls['send_message'][0]['kwargs']['text']
        == 'Регистрация прошла успешно, показываю меню ❤!'
    )

    await send.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=1, exec_tries=1, reschedule_counter=1, queue='',
        ),
        messages={
            '123': [{'message_key': 'new_shifts'}],
            'fake': [{'message_key': 'custom_message'}],
        },
    )

    assert (
        mock_bot_class.calls['send_message'][1]['kwargs']['text']
        == 'У тебя изменились смены: 📅 '
        'Смена 01 апреля (чт) 06:00 - 12:30 Обрати '
        'внимание, на смену запланировано: '
        'Химиотерапия 03 апреля (сб) 23:00 - '
        '04 апреля (вс) 00:00'
    )

    assert len(mock_bot_class.calls['send_message']) == 2


@pytest.mark.translations(wfm_backend_tg_bot=data.DEFAULT_TRANSLATION)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_BOT_EMOJIES={
        'emoji_heart': 'heavy black heart',
        'emoji_calendar': 'calendar',
    },
)
async def test_shift_offer_message_sending(
        stq3_context, mock_wfm, web_app_client, mock_bot_class,
):
    mock_wfm()

    await web_app_client.post('/v1/webhook', json=START_REQUEST_MESSAGE)

    await send.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=1, exec_tries=1, reschedule_counter=1, queue='',
        ),
        messages={
            '123': [
                {
                    'message_key': 'additional_shift_offer',
                    'message_kwargs': {
                        'job_data': {
                            'job_id': 1,
                            'datetime_from': (
                                '2021-08-02T02:00:00.000000 +0300'
                            ),
                            'datetime_to': '2021-08-02T12:00:00.000000 +0300',
                        },
                    },
                },
            ],
        },
    )

    assert (
        mock_bot_class.calls['send_message'][1]['kwargs']['text']
        == 'Тебе предложена дополнительная смена: 📅 '
        '02 августа (пн) 02:00 - 12:00'
    )
    calls = mock_bot_class.calls['send_message']
    assert len(calls) == 2
