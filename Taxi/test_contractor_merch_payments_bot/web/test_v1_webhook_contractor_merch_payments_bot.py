import hashlib
from typing import Any, Dict  # noqa: IS001

import pytest

URI = '/v1/webhook/contractor-merch-payments-bot/'
BOT_TOKEN_HASH = hashlib.pbkdf2_hmac(
    'sha512',
    '123456:test_token'.encode('utf-8'),
    'test_token_salt'.encode('utf-8'),
    1000000,
).hex()
WRONG_BOT_TOKEN_HASH = hashlib.pbkdf2_hmac(
    'sha512',
    '123456:wrong_test_token'.encode('utf-8'),
    'test_token_salt'.encode('utf-8'),
    1000000,
).hex()

REQUEST_MESSAGE = {
    'update_id': 10000,
    'message': {
        'date': 1441645532,
        'chat': {
            'last_name': 'test_Ivanov',
            'id': 11111,
            'type': 'private',
            'first_name': 'test_Victor',
            'username': 'test_ivanov_victor_1970',
        },
        'message_id': 1365,
        'from': {
            'is_bot': False,
            'last_name': 'test_Ivanov',
            'id': 11111,
            'first_name': 'test_Victor',
            'username': 'test_ivanov_victor_1970',
        },
        'text': 'test',
    },
}
CHAT_USERNAME = 'test_ivanov_victor_1970'
USER_ID = 419406554
CHAT_ID = 419406554
CALLBACK_QUERY_SKELETON = {
    'id': '1800907935403429203',
    'from': {
        'id': USER_ID,
        'is_bot': False,
        'first_name': 'test_Victor',
        'username': 'test_ivanov_victor_1970',
        'last_name': 'test_Ivanov',
        'language_code': 'en',
    },
    'chat_instance': '-1892487184517850311',
    'data': '100.50,DJJ83JDJ20S9QA,a',
}

MESSAGE_CALLBACK_QUERY = {
    'message_id': 79,
    'from': {
        'id': USER_ID,
        'is_bot': True,
        'first_name': 'contractor-merch-payments-bot-k911mipt',
        'username': 'yandex_k911mipt_cmp_bot',
    },
    'chat': {
        'id': CHAT_ID,
        'type': 'private',
        'first_name': 'test_Victor',
        'last_name': 'test_Ivanov',
        'username': CHAT_USERNAME,
    },
    'date': 1634696245,
    'text': 'You are about to write off 100.50 from payment_id=DJJ83JDJ20S9QA',
    'reply_markup': {
        'inline_keyboard': [
            [
                {'callback_data': '100.50,DJJ83JDJ20S9QA,a', 'text': 'OK'},
                {
                    'callback_data': '100.50,DJJ83JDJ20S9QA,r',
                    'text': 'Enter another price',
                },
            ],
        ],
    },
}
REQUEST_CALLBACK_QUERY = {
    'update_id': 864419797,
    'callback_query': {
        **CALLBACK_QUERY_SKELETON,  # type: ignore
        'message': MESSAGE_CALLBACK_QUERY,
    },
}


@pytest.mark.parametrize(
    ['update', 'task_id'],
    [
        pytest.param(REQUEST_MESSAGE, '11111_11111_1365', id='common message'),
        pytest.param(
            REQUEST_CALLBACK_QUERY,
            '419406554_419406554_79_1800907935403429203',
            id='callback_query',
        ),
    ],
)
async def test_ok(web_app_client, stq, update, task_id):
    endpoint = f'{URI}{BOT_TOKEN_HASH}'
    response = await web_app_client.post(endpoint, json=update)
    assert response.status == 200
    assert stq.contractor_merch_payments_bot_process_telegram_message.has_calls
    stq_args = (
        stq.contractor_merch_payments_bot_process_telegram_message.next_call()
    )
    assert (
        stq_args['queue']
        == 'contractor_merch_payments_bot_process_telegram_message'
    )
    assert stq_args['id'] == task_id
    assert stq_args['kwargs']['update'] == update


async def test_wrong_hook(web_app_client):
    update = REQUEST_MESSAGE
    endpoint = f'{URI}{WRONG_BOT_TOKEN_HASH}'
    response = await web_app_client.post(endpoint, json=update)
    assert response.status == 404
    assert await response.json() == {'code': '404', 'message': 'Not found'}


UPDATE_SKELETON: Dict[str, Any] = {'update_id': 10000}
MESSAGE_SKELETON: Dict[str, Any] = {
    'date': 1441645532,
    'message_id': 1365,
    'text': 'test',
}
CHAT_SKELETON: Dict[str, Any] = {
    'last_name': 'Test Lastname',
    'id': 11111,
    'type': 'private',
    'first_name': 'Test Firstname',
    'username': 'test_username',
}
FROM_SKELETON: Dict[str, Any] = {
    'is_bot': False,
    'last_name': 'Test Lastname',
    'id': 11111,
    'first_name': 'Test Firstname',
    'username': 'test_username',
}


@pytest.mark.parametrize(
    'update',
    [
        pytest.param(UPDATE_SKELETON, id='Empty message'),
        pytest.param(
            {
                **UPDATE_SKELETON,
                'message': {**MESSAGE_SKELETON, 'from': FROM_SKELETON},
            },
            id='Empty message.chat',
        ),
        pytest.param(
            {
                **UPDATE_SKELETON,
                'message': {**MESSAGE_SKELETON, 'chat': CHAT_SKELETON},
            },
            id='Empty message.from',
        ),
        pytest.param(
            {
                'update_id': 864419797,
                'callback_query': {**CALLBACK_QUERY_SKELETON},
            },
            id='Empty message in callback query',
        ),
    ],
)
async def test_invalid_update(web_app_client, stq, update):
    endpoint = f'{URI}{BOT_TOKEN_HASH}'
    response = await web_app_client.post(endpoint, json=update)
    assert response.status == 200
    assert (
        not stq.contractor_merch_payments_bot_process_telegram_message.has_calls  # noqa: E501 (line too long)
    )
