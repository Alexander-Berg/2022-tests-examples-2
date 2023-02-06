import json

import pytest


@pytest.mark.parametrize(
    'token_file, errors_list',
    [
        ['test_token.json', []],
        [
            'test_token_error.json',
            [
                'Отсутствует обязательное поле "access_token" в теле ответа на запрос POST $mockserver/security/oauth/token',  # noqa: F401,E501
            ],
        ],
    ],
)
async def test_stocks(
        web_context, mockserver, load_json, token_file, errors_list,
):
    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json(token_file)),
            200,
            headers={'Content-type': 'application/json'},
        )

    request_param = {
        'vendor_host': '$mockserver',
        'client_id': 'yandex',
        'client_secret': 'client_secret',
        'grant_type': 'grant_type',
        'scope': 'scope',
        'origin_id': '123',
    }
    response = await web_context.retail_worker.validate_token(request_param)
    assert errors_list == response
    assert get_test_get_token.has_calls
