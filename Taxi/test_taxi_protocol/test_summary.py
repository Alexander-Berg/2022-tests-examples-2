# pylint: disable=too-many-arguments
import pytest

from taxi import discovery

from test_taxi_protocol import plugins as conftest


@pytest.mark.parametrize(
    'headers, url, data, expected_code, expected_result, expected_owner,'
    'expected_owner_role, expected_platform',
    [
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88b'},
            '/4.0/support_chat/v1/regular/summary',
            {'id': '5ff4901c583745e089e55be4a8c7a88b'},
            401,
            None,
            None,
            None,
            None,
        ),
        (
            {'X-YaTaxi-UserId': '1ff4901c583745e089e55be4a8c7a88s'},
            '/4.0/support_chat/v1/regular/summary',
            {'id': '1ff4901c583745e089e55be4a8c7a88s'},
            401,
            None,
            None,
            None,
            None,
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/summary',
            {'id': '5ff4901c583745e089e55be4a8c7a88d'},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '000000000000000000000001',
            'client',
            'yandex',
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/summary/?service=grocery',
            {'id': '5ff4901c583745e089e55be4a8c7a88d'},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '000000000000000000000001',
            'client',
            'yandex',
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/summary',
            {},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '000000000000000000000001',
            'client',
            'yandex',
        ),
        (
            {
                'X-Yandex-UID': '123',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d',
            },
            '/4.0/support_chat/v1/realtime/summary',
            {},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '123',
            'eats_client',
            'yandex',
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/summary/?service=help_yandex_ru',
            {},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '123',
            'help_yandex_client',
            'help_yandex',
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/summary/'
            '?service=labs_admin_yandex_ru',
            {},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '123',
            'labs_admin_yandex_client',
            'labs_admin_yandex',
        ),
        (
            {'X-YaTaxi-User': 'eats_user_id=123,some_other=other_value'},
            '/eats/v1/support_chat/v1/realtime/summary/?service=eats_app',
            {},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '123',
            'eats_app_client',
            'eats_app',
        ),
        (
            {'X-Yandex-UID': '123'},
            '/eats/v1/support_chat/v1/realtime/summary/?service=eats_app',
            {},
            400,
            None,
            None,
            None,
            None,
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/regular/summary/?service=drive',
            {},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '123',
            'carsharing_client',
            'yandex',
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/summary/?service=scouts',
            {},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '123',
            'scouts_client',
            'scouts_app',
        ),
        (
            {'X-Taxi-Storage-Id': '123'},
            '/4.0/support_chat/v1/realtime/summary/?service=lavka_storages',
            {},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '123',
            'lavka_storages_client',
            'lavka_storages_app',
        ),
        (
            {'X-Eats-Session': 'test-session-header'},
            '/eats/v1/website_support_chat/v1/realtime/summary/'
            '?service=website',
            {},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '13c726a0440481a6d4208f6d834961400f7c8906',
            'website_client',
            'website',
        ),
        (
            {'X-YaEda-PartnerId': '12'},
            '/eats/v1/restapp_support_chat/v1/realtime/summary/'
            '?service=restapp',
            {},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '12',
            'restapp_client',
            'restapp',
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/summary/?service=market',
            {},
            200,
            {'archive': False, 'visible': False, 'new_messages_count': 0},
            '123',
            'market_client',
            'market_app',
        ),
    ],
)
async def test_summary(
        monkeypatch,
        patch_aiohttp_session,
        response_mock,
        protocol_client,
        protocol_app,
        mock_get_users,
        headers,
        url,
        data,
        expected_code,
        expected_result,
        expected_owner,
        expected_owner_role,
        expected_platform,
):
    service = discovery.find_service('support_chat')

    @patch_aiohttp_session(
        service.url + '/4.0/support_chat/v1/regular/summary', 'POST',
    )
    def _summary(*args, **kwargs):
        return response_mock(
            json={
                'archive': False,
                'open': False,
                'visible': False,
                'open_chat_new_messages_count': 0,
                'visible_chat_new_messages_count': 0,
            },
        )

    monkeypatch.setattr(
        protocol_app, 'passport', conftest.MockPassportClient(),
    )

    response = await protocol_client.post(url, headers=headers, json=data)
    assert response.status == expected_code
    if expected_result:
        assert await response.json() == expected_result

    if expected_code == 200:
        summary_call = _summary.calls[0]
        assert summary_call['kwargs']['json'] == {
            'owner': {
                'id': expected_owner,
                'platform': expected_platform,
                'role': expected_owner_role,
            },
        }
