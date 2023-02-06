import pytest

import test_contractor_merch_payments_bot.mocks.telegram as telegram_mocks

CHAT_ID = 128918423094533274
PAYMENT = {
    'payment_id': 'test_payment_id',
    'status': 'payment_passed',
    'merchant_id': 'test_merchant_id',
    'price': '200',
    'created_at': '2021-11-12T12:00:00Z',
    'updated_at': '2021-11-12T12:00:00Z',
    'metadata': {
        'integrator': 'contractor-merch-payment-bot',
        'telegram_chat_id': CHAT_ID,
        'telegram_personal_id': 'test_telegram_personal_id',
    },
}


@pytest.mark.parametrize(
    ['status', 'telegram_message', 'response_status', 'tg_api_times_called'],
    [
        pytest.param(
            'payment_passed',
            'Платёж *test_payment_id* успешно выполнен! ✅',
            200,
            1,
            id='passed',
        ),
        pytest.param(
            'payment_failed',
            'Платёж *test_payment_id* не удался! ❌',
            200,
            1,
            id='failed',
        ),
        pytest.param(
            'payment_expired',
            'Срок действия платежа *test_payment_id* истёк! 🕒',
            200,
            1,
            id='expired',
        ),
        pytest.param(
            'contractor_declined',
            'Водитель отказался от оплаты платежа *test_payment_id*! ❌',
            200,
            1,
            id='contractor_declined',
        ),
    ],
)
async def test_ok(
        web_app_client,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        status,
        telegram_message,
        response_status,
        tg_api_times_called,
):
    update = {'payment': {**PAYMENT, 'status': status}}

    endpoint = '/internal/contractor-merch-payments-bot/v1/notify-on-payment-completion'  # noqa: E501 (line too long)
    response = await web_app_client.post(endpoint, json=update)

    assert response.status == response_status
    assert (
        mock_telegram_service.send_message.handler.times_called
        == tg_api_times_called
    )
    if tg_api_times_called > 0:
        request = mock_telegram_service.send_message.handler.next_call()[
            'request'
        ]
        assert request.json == {
            'chat_id': CHAT_ID,
            'text': telegram_message,
            'parse_mode': 'markdown',
            'reply_markup': {
                'keyboard': [[{'text': 'Справка 📚'}]],
                'resize_keyboard': True,
                'one_time_keyboard': False,
                'selective': False,
            },
        }
