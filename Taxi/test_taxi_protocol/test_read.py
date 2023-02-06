import pytest

from taxi import discovery


@pytest.mark.parametrize(
    ['headers', 'read_url', 'params', 'data', 'chat_id', 'expected_json'],
    [
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/read/chat_id',
            {},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '000000000000000000000001',
                    'role': 'client',
                    'platform': 'yandex',
                },
            },
        ),
        (
            {
                'X-Yandex-UID': '123',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d',
            },
            '/4.0/support_chat/v1/realtime/read/chat_id',
            {},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '123',
                    'role': 'eats_client',
                    'platform': 'yandex',
                },
            },
        ),
        (
            {
                'X-Yandex-UID': '123',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d',
            },
            '/4.0/support_chat/v1/realtime/read/chat_id',
            {'service': 'safety_center'},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '123',
                    'role': 'safety_center_client',
                    'platform': 'yandex',
                },
            },
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/read/chat_id',
            {'service': 'help_yandex_ru'},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '123',
                    'role': 'help_yandex_client',
                    'platform': 'help_yandex',
                },
            },
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/lab/support_chat/v1/realtime/read/chat_id',
            {'service': 'labs_admin_yandex_ru'},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '123',
                    'role': 'labs_admin_yandex_client',
                    'platform': 'labs_admin_yandex',
                },
            },
        ),
        (
            {'X-YaTaxi-User': 'eats_user_id=12345'},
            '/eats/v1/support_chat/v1/realtime/read/chat_id',
            {'service': 'eats_app'},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '12345',
                    'role': 'eats_app_client',
                    'platform': 'eats_app',
                },
            },
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/regular/read/chat_id',
            {'service': 'drive'},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '123',
                    'role': 'carsharing_client',
                    'platform': 'yandex',
                },
            },
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/read/chat_id',
            {'service': 'scouts'},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '123',
                    'role': 'scouts_client',
                    'platform': 'scouts_app',
                },
            },
        ),
        (
            {'X-Taxi-Storage-Id': '123'},
            '/4.0/support_chat/v1/realtime/read/chat_id',
            {'service': 'lavka_storages'},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '123',
                    'role': 'lavka_storages_client',
                    'platform': 'lavka_storages_app',
                },
            },
        ),
        (
            {'X-Eats-Session': 'test-session-header'},
            '/eats/v1/website_support_chat/v1/realtime/read/chat_id',
            {'service': 'website'},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '13c726a0440481a6d4208f6d834961400f7c8906',
                    'role': 'website_client',
                    'platform': 'website',
                },
            },
        ),
        (
            {'X-YaEda-PartnerId': '12'},
            '/eats/v1/restapp_support_chat/v1/realtime/read/chat_id',
            {'service': 'restapp'},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '12',
                    'role': 'restapp_client',
                    'platform': 'restapp',
                },
            },
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/read/chat_id',
            {'service': 'market'},
            {},
            'chat_id',
            {
                'owner': {
                    'id': '123',
                    'role': 'market_client',
                    'platform': 'market_app',
                },
            },
        ),
    ],
)
@pytest.mark.usefixtures('mock_passport')
async def test_read(
        protocol_client,
        patch_aiohttp_session,
        response_mock,
        mock_get_users,
        headers,
        read_url,
        params,
        data,
        chat_id,
        expected_json,
):

    support_chat_url = discovery.find_service('support_chat').url

    @patch_aiohttp_session(support_chat_url, 'POST')
    def read(method, url, **kwargs):
        assert support_chat_url + '/v1/chat/' + chat_id + '/read' == url
        assert kwargs['json'] == expected_json
        return response_mock(json={})

    response = await protocol_client.post(
        read_url, headers=headers, params=params, json=data,
    )
    assert response.status == 200

    assert read.calls
