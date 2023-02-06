import base64

import pytest

from eats_tips_payments.api import approve_domain_apple


@pytest.mark.parametrize(
    'token', ('apple_token', 'another_apple_token', 'multi\nstring\ntoken'),
)
async def test_register_payment(web_app_client, simple_secdist, token):
    simple_secdist['settings_override'][
        approve_domain_apple.APPLE_APPROVE_TOKEN_NAME
    ] = base64.b64encode(token.encode())
    response = await web_app_client.get(
        '/.well-known/apple-developer-merchantid-domain-association.txt',
        headers={'Host': 'tips.yandex.ru'},
    )
    assert response.status == 200
    assert await response.text() == token
