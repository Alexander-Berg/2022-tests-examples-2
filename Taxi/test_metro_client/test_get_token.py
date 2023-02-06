import json


async def test_get_token(library_context, load_json, mockserver):
    base_token = 'base_token'

    request_param = library_context.secdist['settings_override'].get(
        'METRO_CREDENTIALS', {},
    )['stocks']

    @mockserver.handler('/test_get_token')
    def _get_test_path(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    login = await library_context.client_metro.get_login(request_param, 'test')
    assert login.token == base_token
