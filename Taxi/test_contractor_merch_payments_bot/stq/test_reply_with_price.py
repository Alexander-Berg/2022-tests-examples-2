import aiohttp.web
import pytest

import contractor_merch_payments_bot.generated.stq3.pytest_plugin as stq_plugin
from test_contractor_merch_payments_bot.mocks import (
    authorization as authorization_mocks,
)
import test_contractor_merch_payments_bot.mocks.telegram as telegram_mocks

CHAT_ID = 419406554


@pytest.mark.parametrize(
    ['telegram_update', 'expected_telegram_message'],
    [
        pytest.param(
            'valid_request.json',
            'valid_confirmation_request.json',
            id='Ask merchant first time',
        ),
        pytest.param(
            'valid_request_retry.json',
            'valid_confirmation_request.json',
            id='Ask merchant on retry',
        ),
        pytest.param(
            'invalid_request.json',
            'invalid_confirmation_request.json',
            id='Callback data is more than 64 bytes',
        ),
    ],
)
async def test_ok_and_internal_error(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        mockserver,
        load_json,
        telegram_update,
        expected_telegram_message,
):
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id',
            args=[],
            kwargs=dict(update=load_json(telegram_update)),
        )
    )

    mock_authorization_services.assert_services_called_once()

    assert mock_telegram_service.send_message.handler.times_called == 1
    assert mock_telegram_service.send_message.handler.next_call()[
        'request'
    ].json == load_json(expected_telegram_message)


@pytest.mark.parametrize(
    ['price', 'expected_telegram_message'],
    [
        pytest.param(
            'qwerty',
            'Некорректный ввод: укажите, пожалуйста, число,'
            ' например: 300 или 99.99\n'
            '\n'
            'Платёж: *DJJ83JDJ20S9QA*',
            id='Not parsable price',
        ),
        pytest.param(
            '-10',
            'Некорректный ввод: цена должна быть больше нуля!\n'
            '\n'
            'Платёж: *DJJ83JDJ20S9QA*',
            id='Price below zero',
        ),
        pytest.param(
            '0',
            'Некорректный ввод: цена должна быть больше нуля!\n'
            '\n'
            'Платёж: *DJJ83JDJ20S9QA*',
            id='Price equals to zero',
        ),
        pytest.param(
            '23.456',
            'Некорректный ввод: укажите, пожалуйста, цену'
            ' с точностью не больше чем до одной копейки\n'
            '\n'
            'Платёж: *DJJ83JDJ20S9QA*',
            id='Decimal places exceeded',
        ),
    ],
)
async def test_send_wrong_price_reply(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        mockserver,
        load_json,
        price,
        expected_telegram_message,
):
    request = load_json('valid_request.json')
    request['message']['text'] = price
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=request),
        )
    )
    mock_authorization_services.assert_services_called_once()
    assert mock_telegram_service.send_message.handler.times_called == 1
    send_message_request = (
        mock_telegram_service.send_message.handler.next_call()['request']
    )
    assert send_message_request.json == {
        'chat_id': CHAT_ID,
        'text': expected_telegram_message,
        'reply_markup': '{"force_reply": true, "selective": false}',
        'parse_mode': 'markdown',
    }


PRICE_SET_TELEGRAM_REQUEST = {
    'chat_id': CHAT_ID,
    'text': (
        'Цена была успешно выставлена! '
        'Ожидаем подтверждения от водителя.. 🕒'
    ),
    'parse_mode': 'markdown',
}

RETRY_TELEGRAM_REQUEST = {
    'chat_id': CHAT_ID,
    'text': (
        'Пожалуйста, введите цену, которую вы хотите списать!\n'
        '\n'
        'Платёж: *DJJ83JDJ20S9QA*'
    ),
    'parse_mode': 'markdown',
    'reply_markup': {'force_reply': True, 'selective': False},
}

SOME_ERROR_OCCURRED_TELEGRAM_REQUEST = {
    'chat_id': CHAT_ID,
    'text': 'Что-то пошло не так... Попробуйте ещё раз!',
    'parse_mode': 'markdown',
}


@pytest.mark.parametrize(
    [
        'telegram_update',
        'expected_telegram_message',
        'price_put_is_called',
        'answer_callback_query_is_called',
        'callback_text',
    ],
    [
        pytest.param(
            'valid_request_with_confirm_button.json',
            PRICE_SET_TELEGRAM_REQUEST,
            True,
            True,
            'Цена установлена!',
            id='Merchant replied OK',
        ),
        pytest.param(
            'valid_request_with_retry_button.json',
            RETRY_TELEGRAM_REQUEST,
            False,
            True,
            'Укажите новую цену!',
            id='Merchant asked reply',
        ),
        pytest.param(
            'invalid_request_with_buttons_format.json',
            SOME_ERROR_OCCURRED_TELEGRAM_REQUEST,
            False,
            False,
            None,
            id='Button callback data incorrect',
        ),
        pytest.param(
            'invalid_request_with_buttons_name.json',
            SOME_ERROR_OCCURRED_TELEGRAM_REQUEST,
            False,
            False,
            None,
            id='Button callback data button incorrect',
        ),
    ],
)
async def test_price_put_after_confirmation_ok(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        mockserver,
        load_json,
        telegram_update,
        expected_telegram_message,
        price_put_is_called,
        answer_callback_query_is_called,
        callback_text,
):
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id',
            args=[],
            kwargs=dict(update=load_json(telegram_update)),
        )
    )

    mock_authorization_services.assert_services_called_once()

    assert mock_telegram_service.send_message.handler.times_called == 1
    assert (
        mock_telegram_service.send_message.handler.next_call()['request'].json
        == expected_telegram_message
    )
    if price_put_is_called:
        payment_price_put = mock_contractor_merch_payments.payment_price_put
        request = payment_price_put.handler.next_call()['request']
        assert request.query['payment_id'] == 'DJJ83JDJ20S9QA'
        assert request.json == {
            'merchant_id': 'merchant_id-mcdonalds',
            'price': '100.50',
            'currency': 'RUB',
            'integrator': 'payments-bot',
            'metadata': {
                'telegram_chat_id': CHAT_ID,
                'telegram_personal_id': 'sonsdnc9929dn202010e4cnn191nx49c',
            },
        }

    if answer_callback_query_is_called:
        assert (
            mock_telegram_service.answer_callback_query.handler.times_called
            == 1
        )

        assert (
            mock_telegram_service.answer_callback_query.handler.next_call()[
                'request'
            ].json
            == {
                'callback_query_id': '799592010872444591',
                'text': callback_text,
            }
        )


@pytest.mark.parametrize(
    ['expected_telegram_message', 'cmp_v1_payment_price_put_response'],
    [
        pytest.param(
            'Платёж не найден! ❌',
            aiohttp.web.json_response(
                {'code': 'payment_not_found', 'message': 'Payment not found'},
                status=404,
            ),
            id='payment_not_found',
        ),
        pytest.param(
            'Цена уже выставлена!',
            aiohttp.web.json_response(
                {'code': 'price_already_set', 'message': 'Price already set'},
                status=409,
            ),
            id='price_already_set',
        ),
        pytest.param(
            'Срок действия платежа истёк! 🕒',
            aiohttp.web.json_response(
                {'code': 'payment_expired', 'message': 'Payment expired'},
                status=410,
            ),
            id='payment_expired',
        ),
        # TODO: удалить тест после полной выкатки `price_limit_exceeded`
        pytest.param(
            'Превышен допустимый лимит цены!',
            aiohttp.web.json_response(
                {
                    'code': 'price_limit_excceded',
                    'message': 'Price limit excceded.',
                },
                status=400,
            ),
            id='price_limit_excceded',
        ),
        pytest.param(
            'Превышен допустимый лимит цены!',
            aiohttp.web.json_response(
                {
                    'code': 'price_limit_exceeded',
                    'message': 'Price limit exceeded.',
                },
                status=400,
            ),
            id='price_limit_exceeded',
        ),
    ],
)
async def test_set_price_handler_replies(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        mockserver,
        load_json,
        expected_telegram_message,
        cmp_v1_payment_price_put_response,
):
    mock_contractor_merch_payments.payment_price_put.body = (
        cmp_v1_payment_price_put_response
    )
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id',
            args=[],
            kwargs=dict(
                update=load_json('valid_request_with_confirm_button.json'),
            ),
        )
    )
    mock_authorization_services.assert_services_called_once()
    assert mock_telegram_service.send_message.handler.times_called == 1
    send_message_request = (
        mock_telegram_service.send_message.handler.next_call()['request']
    )
    assert send_message_request.json == {
        'chat_id': CHAT_ID,
        'text': expected_telegram_message,
        'parse_mode': 'markdown',
    }
