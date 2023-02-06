import pytest

from contractor_merch_payments_bot.generated.stq3 import (
    pytest_plugin as stq_plugin,
)
from test_contractor_merch_payments_bot.mocks import (
    authorization as authorization_mocks,
)
from test_contractor_merch_payments_bot.mocks import telegram as telegram_mocks

CHAT_ID = 419406554

IMAGES = {
    'instructions': {
        'help': (
            'https://taxi-mvp.s3.yandex.net/pro-marketplace/telegram/help.png'
        ),
        'scanning': (
            'https://taxi-mvp.s3.yandex.net/'
            'pro-marketplace/telegram/scanning.png'
        ),
        'setting_price': (
            'https://taxi-mvp.s3.yandex.net/'
            'pro-marketplace/telegram/setting_price.png'
        ),
        'price_confirmation': (
            'https://taxi-mvp.s3.yandex.net/'
            'pro-marketplace/telegram/price_confirmation.png'
        ),
        'completion': (
            'https://taxi-mvp.s3.yandex.net/'
            'pro-marketplace/telegram/completion.png'
        ),
    },
}


@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_BOT_IMAGES=IMAGES)
async def test_introduction(
        stq_runner: stq_plugin.Stq3Runner,
        mockserver,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        load_json,
):
    update = load_json('request_with_start.json')
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    send_message_request = (
        mock_telegram_service.send_message.handler.next_call()['request']
    )
    assert send_message_request.json == {
        'chat_id': 419406554,
        'text': (
            'Здравствуйте, `test_Victor`! 👋\n'
            'Чтобы начать платёж сфотографируйте, пожалуйста, QR-код!\n'
            '\n'
            'Для более детальной инструкции введите /help'
        ),
        'parse_mode': 'markdown',
        'reply_markup': {
            'keyboard': [[{'text': 'Справка 📚'}]],
            'resize_keyboard': True,
            'one_time_keyboard': False,
            'selective': False,
        },
    }


@pytest.mark.parametrize(
    ['request_json'],
    [
        pytest.param('request_with_help.json', id='instructions_with_help'),
        pytest.param(
            'request_with_help_key.json', id='instructions_with_help_key',
        ),
    ],
)
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_BOT_IMAGES=IMAGES)
async def test_instructions_with_command(
        stq_runner: stq_plugin.Stq3Runner,
        mockserver,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        load_json,
        request_json,
):
    update = load_json(request_json)
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    send_photo_request = mock_telegram_service.send_photo.handler.next_call()[
        'request'
    ]
    assert send_photo_request.json == {
        'caption': (
            'Привет 👋\n'
            '\n'
            'В этой инструкции я покажу, как принять оплату от '
            'водителей по QR-коду!'
        ),
        'chat_id': CHAT_ID,
        'parse_mode': 'markdown',
        'photo': (
            'https://taxi-mvp.s3.yandex.net/pro-marketplace/telegram/help.png'
        ),
        'reply_markup': {
            'inline_keyboard': [
                [{'callback_data': 'is#n#0', 'text': 'Начать! ✨'}],
            ],
        },
    }


@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_BOT_IMAGES=IMAGES)
async def test_instructions_scroll_next(
        stq_runner: stq_plugin.Stq3Runner,
        mockserver,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        load_json,
):
    update = load_json('request_with_next_button.json')
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    edit_message_media_request = (
        mock_telegram_service.edit_message_media.handler.next_call()['request']
    )
    assert edit_message_media_request.json == {
        'chat_id': 419406554,
        'media': {
            'caption': (
                '*Этап №1. Сканирование*\n'
                '\n'
                'Сначала нужно отсканировать QR-код у водителя. Для этого '
                'откройте камеру на вашем телефоне и отсканируйте QR-код.\n'
                '\n'
                'Или же нажмите на значок «скрепки» (📎) слева от клавиатуры. '
                'Далее выберите первую вкладку (📷), чтобы сделать '
                'фотографию QR-кода. После того, как фотография будет '
                'сделана, нажмите отправить (⬆).'
            ),
            'media': (
                'https://taxi-mvp.s3.yandex.net/pro-marketplace/'
                'telegram/scanning.png'
            ),
            'parse_mode': 'markdown',
            'type': 'photo',
        },
        'message_id': 10,
        'reply_markup': {
            'inline_keyboard': [
                [
                    {'callback_data': 'is#p#1', 'text': '⏮ Предыдущий шаг'},
                    {'callback_data': 'is#n#1', 'text': 'Следующий шаг ⏭'},
                ],
            ],
        },
    }

    assert (
        mock_telegram_service.answer_callback_query.handler.times_called == 1
    )

    answer_callback_query_request = (
        mock_telegram_service.answer_callback_query.handler.next_call()[
            'request'
        ]
    )
    assert answer_callback_query_request.json == {
        'callback_query_id': '3936498112798969358',
    }


@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_BOT_IMAGES=IMAGES)
async def test_instructions_scroll_previous(
        stq_runner: stq_plugin.Stq3Runner,
        mockserver,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        load_json,
):
    update = load_json('request_with_previous_button.json')
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    edit_message_media_request = (
        mock_telegram_service.edit_message_media.handler.next_call()['request']
    )
    assert edit_message_media_request.json == {
        'chat_id': 419406554,
        'message_id': 10,
        'media': {
            'type': 'photo',
            'media': (
                'https://taxi-mvp.s3.yandex.net/pro-marketplace/'
                'telegram/price_confirmation.png'
            ),
            'caption': (
                '*Этап №3. Подтверждение цены*\n\nТеперь нужно просто '
                'подтвердить, что была введена верная сумма.'
            ),
            'parse_mode': 'markdown',
        },
        'reply_markup': {
            'inline_keyboard': [
                [
                    {'text': '⏮ Предыдущий шаг', 'callback_data': 'is#p#3'},
                    {'text': 'Следующий шаг ⏭', 'callback_data': 'is#n#3'},
                ],
            ],
        },
    }

    assert (
        mock_telegram_service.answer_callback_query.handler.times_called == 1
    )

    answer_callback_query_request = (
        mock_telegram_service.answer_callback_query.handler.next_call()[
            'request'
        ]
    )
    assert answer_callback_query_request.json == {
        'callback_query_id': '3936498112798969358',
    }
