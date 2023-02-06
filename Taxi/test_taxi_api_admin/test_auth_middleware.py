import json

import pytest


@pytest.mark.parametrize(
    ['url', 'params', 'login'],
    [
        pytest.param(
            '/me', {}, 'some_test_login', id='test_tariff_editor_auth',
        ),
        pytest.param(
            '/me',
            {'tplatform_namespace': 'market'},
            'login_not_from_staff',
            id='test_platform_auth',
        ),
    ],
)
@pytest.mark.config(API_ADMIN_USE_PASSPORT_CLIENT_PROBABILITY=1)
async def test_passport_session_auth(
        taxi_api_admin_client,
        patch_aiohttp_session,
        response_mock,
        url,
        params,
        login,
):
    @patch_aiohttp_session('http://blackbox.yandex-team.ru/blackbox/')
    def _blackbox_request(*args, **kwargs):
        response_patch = {
            'status': {'value': 'VALID'},
            'uid': {'value': '11111111'},
            'login': login,
        }
        response_str = json.dumps(response_patch)
        return response_mock(text=response_str)

    taxi_api_admin_client.app.settings.BLACKBOX_AUTH = True
    taxi_api_admin_client.app.secdist['settings_override'][
        'TAXI_ADMIN_CSRF_TOKEN'
    ] = 'temp'
    response = await taxi_api_admin_client.request(
        'GET',
        url,
        params=params,
        cookies={
            'Session_id': 'test_session_id',
            'yandexuid': 'some_yandexuid',
        },
        headers={'X-Real-IP': '127.0.0.1'},
    )
    response_body = await response.json()
    assert response.status == 200, response_body
    assert (
        response_body['csrf_token'] and len(response_body) == 1
    ), response_body
