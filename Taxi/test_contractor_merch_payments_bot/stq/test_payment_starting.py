import pytest

from contractor_merch_payments_bot.generated.stq3 import (
    pytest_plugin as stq_plugin,
)
from test_contractor_merch_payments_bot.mocks import (
    authorization as authorization_mocks,
)
from test_contractor_merch_payments_bot.mocks import telegram as telegram_mocks


USER_ID = 419406554
CHAT_ID = 419406554
CHAT_USERNAME = 'test_ivanov_victor_1970'
START_PAYMENT_REQUEST = 'request_with_photo.json'

PAYMENT_ID = 'YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8'
MESSAGE_ENTER_PRICE = {
    'chat_id': CHAT_ID,
    'text': (
        f'Идентификатор данного платежа *{PAYMENT_ID}*\n'
        '\n'
        'Пожалуйста, введите цену, которую вы хотите списать!'
    ),
    'reply_markup': {'force_reply': True, 'selective': False},
    'parse_mode': 'markdown',
}

MESSAGE_NOT_PARSED = {
    'chat_id': 419406554,
    'text': (
        'Простите, не могу понять Вас!\n'
        '\n'
        'Введите /start для начала работы!'
    ),
    'parse_mode': 'markdown',
}

QR_CODE_NOT_PARSED = {
    'chat_id': 419406554,
    'text': 'Не удалось распознать QR-код. Попробуйте ещё раз!',
    'parse_mode': 'markdown',
}


@pytest.mark.parametrize(
    ['image', 'payment_status', 'expected_response'],
    [
        pytest.param('short_payment_id.png', 200, MESSAGE_ENTER_PRICE),
        pytest.param('long_payment_id.png', 200, MESSAGE_ENTER_PRICE),
        pytest.param('utka.png', 200, QR_CODE_NOT_PARSED),
    ],
)
async def test_start_with_qr_code(
        stq_runner: stq_plugin.Stq3Runner,
        mockserver,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        load_binary,
        load_json,
        image,
        payment_status,
        expected_response,
):
    mock_telegram_service.download_file.image = image
    mock_contractor_merch_payments.payment_status_get.status = payment_status

    update = load_json('request_with_photo.json')
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    send_message_request = (
        mock_telegram_service.send_message.handler.next_call()['request']
    )
    assert send_message_request.json == expected_response


@pytest.mark.parametrize(
    ['payment_status_response', 'expected_message'],
    [
        pytest.param(
            {
                'status': 'pending_merchant_approve',
                'merchant': {
                    'merchant_id': 'merchant-id-wrong',
                    'merchant_name': 'Bloodseeker',
                },
                'price': '100',
            },
            'Данный QR-код уже использован для покупки у другого продавца!',
            id='wrong merchant_id',
        ),
        pytest.param(
            {
                'status': 'payment_expired',
                'merchant': {
                    'merchant_id': 'merchant_id-mcdonalds',
                    'merchant_name': 'Bloodseeker',
                },
                'price': '100',
            },
            'Срок действия данного QR-кода истёк!',
            id='payment expired',
        ),
        pytest.param(
            {
                'status': 'merchant_approved',
                'merchant': {
                    'merchant_id': 'merchant_id-mcdonalds',
                    'merchant_name': 'Bloodseeker',
                },
                'price': '99.99',
            },
            'Вы уже указали цену *99.99* руб. '
            'Ожидаем подтверждения водителя! 🕒',
            id='merchant approved',
        ),
        pytest.param(
            {
                'status': 'pending_payment_execution',
                'merchant': {
                    'merchant_id': 'merchant_id-mcdonalds',
                    'merchant_name': 'Bloodseeker',
                },
                'price': '99.50',
            },
            'Вы уже указали цену *99.50* руб. Платёж обрабатывается! 🕒',
            id='pending payment execution',
        ),
        pytest.param(
            {
                'status': 'payment_passed',
                'merchant': {
                    'merchant_id': 'merchant_id-mcdonalds',
                    'merchant_name': 'Bloodseeker',
                },
                'price': '99.3',
            },
            'Вы уже указали цену *99.3* руб. Платёж успешно выполнен! ✅',
            id='payment passed',
        ),
        pytest.param(
            {
                'status': 'payment_failed',
                'merchant': {
                    'merchant_id': 'merchant_id-mcdonalds',
                    'merchant_name': 'Bloodseeker',
                },
                'price': '99',
            },
            'Платёж не удался! ❌',
            id='payment failed',
        ),
        pytest.param(
            {
                'status': 'contractor_declined',
                'merchant': {
                    'merchant_id': 'merchant_id-mcdonalds',
                    'merchant_name': 'Bloodseeker',
                },
                'price': '99',
            },
            'Водитель отказался от оплаты! ❌',
            id='contractor declined',
        ),
    ],
)
async def test_start_with_validation(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        load_json,
        payment_status_response,
        expected_message,
):
    mock_contractor_merch_payments.payment_status_get.body = (
        payment_status_response
    )

    update = load_json(START_PAYMENT_REQUEST)
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    assert (
        mock_contractor_merch_payments.payment_status_get.handler.times_called
        == 1
    )
    assert (
        mock_contractor_merch_payments.payment_status_get.handler.next_call()[
            'request'
        ].query
        == {'payment_id': 'YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8'}
    )

    send_message_request = (
        mock_telegram_service.send_message.handler.next_call()['request']
    )
    assert send_message_request.json == {
        'chat_id': 419406554,
        'text': expected_message,
        'parse_mode': 'markdown',
    }


async def test_start_with_deep_link(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        load_json,
):
    update = load_json('request_with_deep_link.json')
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    send_message_request = (
        mock_telegram_service.send_message.handler.next_call()['request']
    )
    assert send_message_request.json == MESSAGE_ENTER_PRICE


@pytest.mark.parametrize(
    ['username', 'merchant_times_called'],
    [
        pytest.param('test_not_registered_merchant_username', 1),
        pytest.param('test_not_registered_personal_username', 0),
        pytest.param(None, 0),
    ],
)
async def test_start_not_recognized_merchant(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        load_json,
        username,
        merchant_times_called,
):
    request = load_json('not_authorized_request.json')
    request['message']['from']['username'] = username
    request['message']['chat']['username'] = username

    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=request),
        )
    )

    telegram_logins_find = (
        mock_authorization_services.personal_telegram_logins_find
    )
    assert (
        telegram_logins_find.handler.times_called == 0
        if username is None
        else 1
    )

    id_by_personal_id = (
        mock_authorization_services.merchant_profiles_id_by_personal_id
    )
    assert id_by_personal_id.handler.times_called == merchant_times_called

    assert mock_telegram_service.send_message.handler.times_called == 1
    send_message_request = (
        mock_telegram_service.send_message.handler.next_call()['request']
    )

    if username is not None:
        expected_text = (
            'Не можем найти продавца, где вы зарегистрированы как кассир. '
            'Обратитесь, пожалуйста, в поддержку, '
            'чтобы вас зарегистрировали!\n'
            f'Ваш телеграмный логин: `{username}`'
        )
    else:
        expected_text = (
            'Не можем найти продавца, где вы зарегистрированы как кассир. '
            'Укажите, пожалуйста, свой логин в профиле и обратитесь '
            'в поддержку, чтобы вас зарегистрировали!'
        )

    assert send_message_request.json == {
        'chat_id': CHAT_ID,
        'text': expected_text,
        'parse_mode': 'markdown',
    }
