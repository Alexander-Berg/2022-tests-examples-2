import hashlib

import pytest

TG_ID_TO_PERSONAL_ID = {'1': 'pd1', '2': 'pd2'}
URI = '/v1/webhook/fleet-notifications-telegram-bot/'
BOT_TOKEN_SHA256_HASH = hashlib.sha256(
    '123456:test_token'.encode('utf-8'),
).hexdigest()
WRONG_BOT_TOKEN_SHA256_HASH = hashlib.sha256(
    '123456:wrong_token'.encode('utf-8'),
).hexdigest()


JSON_REQUEST = {
    'update_id': 10000,
    'message': {
        'date': 1441645532,
        'chat': {
            'last_name': 'test_Ivanov',
            'id': 1,
            'type': 'private',
            'first_name': 'test_Victor',
            'username': 'test_ivanov_victor_1970',
        },
        'message_id': 129,
        'from': {
            'is_bot': False,
            'last_name': 'test_Ivanov',
            'id': 11111,
            'first_name': 'test_Victor',
            'username': 'test_ivanov_victor_1970',
        },
        'text': 'test_text',
    },
}


@pytest.mark.parametrize(
    'endpoint, code',
    [
        pytest.param(f'{URI}{BOT_TOKEN_SHA256_HASH}', 200, id='ok'),
        pytest.param(
            f'{URI}{WRONG_BOT_TOKEN_SHA256_HASH}', 404, id='wrong URL',
        ),
    ],
)
async def test_webhook(web_app_client, stq, endpoint, personal, code):
    personal.set_tg_id_to_personal(TG_ID_TO_PERSONAL_ID)

    json = JSON_REQUEST

    response = await web_app_client.post(endpoint, json=json)
    assert response.status == code

    if code == 200:
        stq_args = (
            stq.fleet_notifications_telegram_bot_process_telegram_message.next_call()  # noqa E501 line too long
        )  # noqa
        assert (
            stq_args['queue']
            == 'fleet_notifications_telegram_bot_process_telegram_message'
        )
        assert stq_args['id'] == 'pd1_129'
        assert stq_args['args'][0] == 'pd1'
        assert stq_args['args'][1] == 'test_text'
