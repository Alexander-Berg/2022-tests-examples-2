import json

import pytest

from eats_integration_shooter.components import worker


async def test_authorization_to_partner(web_context, mockserver, load_json):
    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')),
            200,
            headers={'Content-type': 'application/json'},
        )

    request_param = {
        'vendor_host': '$mockserver',
        'client_id': 'yandex',
        'client_secret': 'client_secret',
        'grant_type': 'grant_type',
        'scope': 'scope',
    }
    token = await web_context.retail_worker.get_authorization_info(
        request_param,
    )

    assert token == 'base_token'
    assert get_test_get_token.has_calls


async def test_authorization_to_partner_error(
        web_context, mockserver, load_json,
):
    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(b'error', 500)

    request_param = {
        'vendor_host': '$mockserver',
        'client_id': 'yandex',
        'client_secret': 'client_secret',
        'grant_type': 'grant_type',
        'scope': 'scope',
    }
    with pytest.raises(worker.RetailDataError):
        await web_context.retail_worker.get_authorization_info(request_param)

    assert get_test_get_token.has_calls
