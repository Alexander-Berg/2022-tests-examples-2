import hashlib

import pytest

URI = '/v1/webhook/scooter-accumulator-bot/'
BOT_TOKEN_SHA256_HASH = hashlib.sha256(
    '123456:token'.encode('utf-8'),
).hexdigest()
WRONG_BOT_TOKEN_SHA256_HASH = hashlib.sha256(
    '123456:wrong_token'.encode('utf-8'),
).hexdigest()


JSON_REQUEST = {
    'update_id': 10000,
    'message': {
        'date': 1441645532,
        'chat': {
            'last_name': 'Test Lastname',
            'id': 11111,
            'type': 'private',
            'first_name': 'Test Firstname',
            'username': 'test_username',
        },
        'message_id': 1365,
        'from': {
            'is_bot': False,
            'last_name': 'Test Lastname',
            'id': 11111,
            'first_name': 'Test Firstname',
            'username': 'test_username',
        },
        'text': 'test',
    },
}


@pytest.mark.parametrize(
    'endpoint, code, message',
    [
        pytest.param(
            f'{URI}{BOT_TOKEN_SHA256_HASH}',
            400,
            'Webhook is disabled',
            id='bot is disabled in testsuite',
        ),
        pytest.param(
            f'{URI}{WRONG_BOT_TOKEN_SHA256_HASH}',
            404,
            'Not found',
            id='wrong URL',
        ),
    ],
)
async def test_ok(web_app_client, endpoint, code, message):
    json = JSON_REQUEST

    response = await web_app_client.post(endpoint, json=json)
    assert response.status == code
    assert await response.json() == {'code': str(code), 'message': message}
