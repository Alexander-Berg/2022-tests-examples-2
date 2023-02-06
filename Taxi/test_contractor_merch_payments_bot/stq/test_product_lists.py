import pytest

from contractor_merch_payments_bot.generated.stq3 import (
    pytest_plugin as stq_plugin,
)
from test_contractor_merch_payments_bot.mocks import (
    authorization as authorization_mocks,
)
from test_contractor_merch_payments_bot.mocks import telegram as telegram_mocks


CHAT_ID = 419406554
PRODUCT_LISTS = [
    [{'price': '259', 'name': 'Биг Тейсти'}],
    [{'price': '99', 'hide_price': True, 'name': 'Картофель фри'}],
    [{'price': '199', 'hide_price': True}],
    [{'price': '69'}],
]

INLINE_KEYBOARD = [
    [
        {
            'text': 'Биг Тейсти – 259 ₽',
            'callback_data': (
                'pl#0#0#YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8'
            ),
        },
    ],
    [
        {
            'text': 'Картофель фри',
            'callback_data': (
                'pl#1#0#YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8'
            ),
        },
    ],
    [
        {
            'text': '199 ₽',
            'callback_data': (
                'pl#2#0#YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8'
            ),
        },
    ],
    [
        {
            'text': '69 ₽',
            'callback_data': (
                'pl#3#0#YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8'
            ),
        },
    ],
    [
        {
            'text': 'Указать другую сумму',
            'callback_data': (
                'pl#-1#-1#YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8'
            ),
        },
    ],
]


@pytest.mark.config(
    MERCHANT_PROFILES_MERCHANTS={
        'merchant_id-mcdonalds': {
            'merchant_name': 'McDonalds',
            'products': PRODUCT_LISTS,
        },
    },
)
async def test_product_list_starting(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        load_json,
):
    update = load_json('request_with_photo.json')
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    send_message_handler = mock_telegram_service.send_message.handler

    assert send_message_handler.times_called == 1
    assert send_message_handler.next_call()['request'].json == {
        'chat_id': CHAT_ID,
        'text': (
            'Идентификатор данного платежа '
            '*YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8*\n\n'
            'Пожалуйста, выберите нужный товар!'
        ),
        'parse_mode': 'markdown',
        'reply_markup': {'inline_keyboard': INLINE_KEYBOARD},
    }


@pytest.mark.config(
    MERCHANT_PROFILES_MERCHANTS={
        'merchant_id-mcdonalds': {
            'merchant_name': 'McDonalds',
            'products': PRODUCT_LISTS,
        },
    },
)
@pytest.mark.parametrize(
    ['update', 'price', 'row', 'column', 'expected_text'],
    [
        pytest.param(
            'request_with_product.json',
            '259',
            0,
            0,
            (
                'Вы выбрали «Биг Тейсти» (*259* руб.). Верно?\n'
                '\n'
                'Платёж: *YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8*'
            ),
            id='product with name and price',
        ),
        pytest.param(
            'request_with_product_without_price.json',
            '99',
            1,
            0,
            (
                'Вы выбрали «Картофель фри». Верно?\n'
                '\n'
                'Платёж: *YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8*'
            ),
            id='product with only name',
        ),
        pytest.param(
            'request_with_product_without_name.json',
            '69',
            3,
            0,
            (
                'Установлена цена *69* руб. Верно?\n'
                '\n'
                'Платёж: *YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8*'
            ),
            id='product with only price',
        ),
    ],
)
async def test_product_list_buttons(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        load_json,
        update,
        price,
        row,
        column,
        expected_text,
):
    update = load_json(update)
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    send_message_handler = mock_telegram_service.send_message.handler

    assert send_message_handler.times_called == 1
    assert send_message_handler.next_call()['request'].json == {
        'chat_id': CHAT_ID,
        'text': expected_text,
        'parse_mode': 'markdown',
        'reply_markup': {
            'inline_keyboard': [
                [
                    {
                        'callback_data': (
                            f'c#prd#c#{price}#'
                            'YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8#'
                            f'{row}#{column}'
                        ),
                        'text': 'Верно ✅',
                    },
                    {
                        'callback_data': (
                            f'c#prd#r#{price}#'
                            'YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8'
                            f'#{row}#{column}'
                        ),
                        'text': 'Изменить 🔄',
                    },
                ],
            ],
        },
    }

    answer_callback_query_handler = (
        mock_telegram_service.answer_callback_query.handler
    )

    assert answer_callback_query_handler.times_called == 1
    assert answer_callback_query_handler.next_call()['request'].json == {
        'callback_query_id': '3936498112798969358',
        'text': 'Подтвердите выбор!',
    }


async def test_manual_price(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        load_json,
):
    update = load_json('request_with_manual_price.json')
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    send_message_handler = mock_telegram_service.send_message.handler

    assert send_message_handler.times_called == 1
    assert send_message_handler.next_call()['request'].json == {
        'chat_id': 419406554,
        'text': (
            'Пожалуйста, введите цену, которую вы хотите списать!'
            '\n\n'
            'Платёж: *YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8*'
        ),
        'parse_mode': 'markdown',
        'reply_markup': {'force_reply': True, 'selective': False},
    }

    answer_callback_query_handler = (
        mock_telegram_service.answer_callback_query.handler
    )

    assert answer_callback_query_handler.times_called == 1
    assert answer_callback_query_handler.next_call()['request'].json == {
        'callback_query_id': '3936498112798969358',
        'text': 'Укажите новую цену!',
    }


@pytest.mark.config(
    MERCHANT_PROFILES_MERCHANTS={
        'merchant_id-mcdonalds': {
            'merchant_name': 'McDonalds',
            'products': PRODUCT_LISTS,
        },
    },
)
async def test_select_product_retry(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        load_json,
):
    update = load_json('request_with_retry.json')
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    send_message_handler = mock_telegram_service.send_message.handler

    assert send_message_handler.times_called == 1
    assert send_message_handler.next_call()['request'].json == {
        'chat_id': CHAT_ID,
        'text': (
            'Пожалуйста, выберите нужный товар!\n'
            '\n'
            'Платёж: *YANDEXPRO-b40d7ecff8244fb8b38bf368507051f8*'
        ),
        'parse_mode': 'markdown',
        'reply_markup': {'inline_keyboard': INLINE_KEYBOARD},
    }

    answer_callback_query_handler = (
        mock_telegram_service.answer_callback_query.handler
    )

    assert answer_callback_query_handler.times_called == 1
    assert answer_callback_query_handler.next_call()['request'].json == {
        'callback_query_id': '799592010872444591',
        'text': 'Выберите нужную опцию!',
    }


@pytest.mark.config(
    MERCHANT_PROFILES_MERCHANTS={
        'merchant_id-mcdonalds': {
            'merchant_name': 'McDonalds',
            'products': PRODUCT_LISTS,
        },
    },
)
async def test_select_product_confirmation(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        load_json,
):
    update = load_json('request_with_confirmation.json')
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    send_message_handler = mock_telegram_service.send_message.handler

    assert send_message_handler.times_called == 1
    assert send_message_handler.next_call()['request'].json == {
        'chat_id': CHAT_ID,
        'text': (
            'Цена была успешно выставлена! '
            'Ожидаем подтверждения от водителя.. 🕒'
        ),
        'parse_mode': 'markdown',
    }

    price_put_handler = (
        mock_contractor_merch_payments.payment_price_put.handler
    )

    assert price_put_handler.times_called == 1
    assert price_put_handler.next_call()['request'].json == {
        'price': '259',
        'currency': 'RUB',
        'merchant_id': 'merchant_id-mcdonalds',
        'integrator': 'payments-bot',
        'metadata': {
            'telegram_chat_id': 419406554,
            'telegram_personal_id': 'sonsdnc9929dn202010e4cnn191nx49c',
            'product_name': 'Биг Тейсти',
        },
    }
