# pylint: disable=too-many-arguments, unused-variable
import json

import pytest

from taxi import discovery

from test_taxi_protocol import plugins as conftest


@pytest.mark.parametrize(
    'headers,url,data,start_date,end_date,answer_data,expected_code,'
    'expected_result,expected_owner,expected_owner_role,expected_platform',
    [
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/supporthistory',
            {'user_id': '5ff4901c583745e089e55be4a8c7a88d'},
            '2017-08-09',
            None,
            {
                'chats': [
                    {
                        'id': 'id1',
                        'metadata': {
                            'created': '2017-12-11T' '18:08:56+0300',
                            'user_locale': 'en',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id1',
                        'chat_name': 'Appeal from 11.12.2017',
                        'created': '2017-12-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'taxi',
                    },
                ],
            },
            '000000000000000000000000',
            'client',
            'android',
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/supporthistory',
            {},
            '2017-08-09',
            None,
            {
                'chats': [
                    {
                        'id': 'id1',
                        'metadata': {
                            'created': '2017-12-11T' '18:08:56+0300',
                            'user_locale': 'en',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id1',
                        'chat_name': 'Appeal from 11.12.2017',
                        'created': '2017-12-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'taxi',
                    },
                ],
            },
            '000000000000000000000000',
            'client',
            'android',
        ),
        (
            {
                'X-Yandex-UID': '123',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d',
            },
            '/4.0/support_chat/v1/realtime/supporthistory',
            {},
            '2017-08-09',
            None,
            {
                'chats': [
                    {
                        'id': 'id1',
                        'metadata': {
                            'created': '2017-12-11T' '18:08:56+0300',
                            'user_locale': 'en',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id1',
                        'chat_name': 'Appeal from ' '11.12.2017',
                        'created': '2017-12-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'eats',
                    },
                ],
            },
            '123',
            'eats_client',
            'android',
        ),
        (
            {'X-YaTaxi-UserId': '1ff4901c583745e089e55be4a8c7a88v'},
            '/4.0/support_chat/v1/regular/supporthistory',
            {'user_id': '5ff4901c583745e089e55be4a8c7a88v'},
            '2017-08-09',
            None,
            None,
            401,
            None,
            None,
            'client',
            'android',
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/supporthistory',
            {'user_id': '5ff4901c583745e089e55be4a8c7a88d'},
            '2017-05-09',
            '2017-07-09',
            {
                'chats': [
                    {
                        'id': 'id2',
                        'metadata': {
                            'created': '2017-05-11T' '18:08:56+0300',
                            'user_locale': 'ru',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id2',
                        'chat_name': 'Обращение от' ' 11.05.2017',
                        'created': '2017-05-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'taxi',
                    },
                ],
            },
            '000000000000000000000000',
            'client',
            'android',
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/supporthistory',
            {},
            '2017-05-09',
            '2017-07-09',
            {
                'chats': [
                    {
                        'id': 'id2',
                        'metadata': {
                            'created': '2017-05-11T' '18:08:56+0300',
                            'user_locale': 'ru',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id2',
                        'chat_name': 'Обращение от' ' 11.05.2017',
                        'created': '2017-05-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'taxi',
                    },
                ],
            },
            '000000000000000000000000',
            'client',
            'android',
        ),
        (
            {
                'X-Yandex-UID': '123',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d',
            },
            '/4.0/support_chat/v1/realtime/supporthistory',
            {},
            '2017-05-09',
            '2017-07-09',
            {
                'chats': [
                    {
                        'id': 'id2',
                        'metadata': {
                            'created': '2017-05-11T' '18:08:56+0300',
                            'user_locale': 'ru',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id2',
                        'chat_name': 'Обращение от' ' 11.05.2017',
                        'created': '2017-05-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'eats',
                    },
                ],
            },
            '123',
            'eats_client',
            'android',
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/supporthistory'
            '/?service=help_yandex_ru',
            {},
            '2017-05-09',
            '2017-07-09',
            {
                'chats': [
                    {
                        'id': 'id2',
                        'metadata': {
                            'created': '2017-05-11T' '18:08:56+0300',
                            'user_locale': 'ru',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id2',
                        'chat_name': 'Обращение от' ' 11.05.2017',
                        'created': '2017-05-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'help_yandex_ru',
                    },
                ],
            },
            '123',
            'help_yandex_client',
            'help_yandex',
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/supporthistory'
            '/?service=labs_admin_yandex_ru',
            {},
            '2017-05-09',
            '2017-07-09',
            {
                'chats': [
                    {
                        'id': 'id2',
                        'metadata': {
                            'created': '2017-05-11T' '18:08:56+0300',
                            'user_locale': 'ru',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id2',
                        'chat_name': 'Обращение от' ' 11.05.2017',
                        'created': '2017-05-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'labs_admin_yandex_ru',
                    },
                ],
            },
            '123',
            'labs_admin_yandex_client',
            'labs_admin_yandex',
        ),
        (
            {'X-YaTaxi-User': 'eats_user_id=123'},
            '/eats/v1/support_chat/v1/realtime/supporthistory'
            '/?service=eats_app',
            {},
            '2017-05-09',
            '2017-07-09',
            {
                'chats': [
                    {
                        'id': 'id2',
                        'metadata': {
                            'created': '2017-05-11T' '18:08:56+0300',
                            'user_locale': 'ru',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id2',
                        'chat_name': 'Обращение от' ' 11.05.2017',
                        'created': '2017-05-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'eats_app',
                    },
                ],
            },
            '123',
            'eats_app_client',
            'eats_app',
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/regular/supporthistory/?service=drive',
            {},
            '2017-08-09',
            None,
            {
                'chats': [
                    {
                        'id': 'id1',
                        'metadata': {
                            'created': '2017-12-11T' '18:08:56+0300',
                            'user_locale': 'en',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id1',
                        'chat_name': 'Appeal from ' '11.12.2017',
                        'created': '2017-12-11T' '18:08:56+0300',
                        'handler_type': 'regular',
                        'service': 'drive',
                    },
                ],
            },
            '123',
            'carsharing_client',
            'android',
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/supporthistory/?service=scouts',
            {},
            '2017-08-09',
            None,
            {
                'chats': [
                    {
                        'id': 'id1',
                        'metadata': {
                            'created': '2017-12-11T' '18:08:56+0300',
                            'user_locale': 'en',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id1',
                        'chat_name': 'Appeal from ' '11.12.2017',
                        'created': '2017-12-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'scouts',
                    },
                ],
            },
            '123',
            'scouts_client',
            'scouts_app',
        ),
        (
            {'X-Taxi-Storage-Id': '123'},
            '/4.0/support_chat/v1/realtime/supporthistory'
            '/?service=lavka_storages',
            {},
            '2017-08-09',
            None,
            {
                'chats': [
                    {
                        'id': 'id1',
                        'metadata': {
                            'created': '2017-12-11T' '18:08:56+0300',
                            'user_locale': 'en',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id1',
                        'chat_name': 'Appeal from ' '11.12.2017',
                        'created': '2017-12-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'lavka_storages',
                    },
                ],
            },
            '123',
            'lavka_storages_client',
            'lavka_storages_app',
        ),
        (
            {'X-Eats-Session': 'test-session-header'},
            '/eats/v1/website_support_chat/v1/realtime/supporthistory/'
            '?service=website',
            {},
            '2017-05-09',
            '2017-07-09',
            {
                'chats': [
                    {
                        'id': 'id2',
                        'metadata': {
                            'created': '2017-05-11T' '18:08:56+0300',
                            'user_locale': 'ru',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id2',
                        'chat_name': 'Обращение от' ' 11.05.2017',
                        'created': '2017-05-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'website',
                    },
                ],
            },
            '13c726a0440481a6d4208f6d834961400f7c8906',
            'website_client',
            'website',
        ),
        (
            {'X-YaEda-PartnerId': '12'},
            '/eats/v1/restapp_support_chat/v1/realtime/supporthistory/'
            '?service=restapp',
            {},
            '2017-05-09',
            '2017-07-09',
            {
                'chats': [
                    {
                        'id': 'id2',
                        'metadata': {
                            'created': '2017-05-11T' '18:08:56+0300',
                            'user_locale': 'ru',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id2',
                        'chat_name': 'Обращение от' ' 11.05.2017',
                        'created': '2017-05-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'restapp',
                    },
                ],
            },
            '12',
            'restapp_client',
            'restapp',
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/supporthistory/?service=market',
            {},
            '2017-08-09',
            None,
            {
                'chats': [
                    {
                        'id': 'id1',
                        'metadata': {
                            'created': '2017-12-11T' '18:08:56+0300',
                            'user_locale': 'en',
                        },
                    },
                ],
            },
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id1',
                        'chat_name': 'Appeal from ' '11.12.2017',
                        'created': '2017-12-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'market',
                    },
                ],
            },
            '123',
            'market_client',
            'market_app',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'support_chat.header': {
            'ru': 'Обращение от %(date)s',
            'en': 'Appeal from %(date)s',
        },
    },
)
@pytest.mark.config(
    PROTOCOL_DEFAULT_HANDLER_TYPES={
        'eats': 'realtime',
        'eats_app': 'realtime',
        'taxi': 'realtime',
        'safety_center': 'realtime',
        'help_yandex_ru': 'realtime',
        'labs_admin_yandex_ru': 'realtime',
        'drive': 'regular',
        'scouts': 'realtime',
        'lavka_storages': 'realtime',
        'website': 'realtime',
        'restapp': 'realtime',
        'market': 'realtime',
    },
)
async def test_supporthistory(
        monkeypatch,
        protocol_client,
        protocol_app,
        mock_get_users,
        headers,
        url,
        data,
        start_date,
        end_date,
        answer_data,
        expected_code,
        expected_result,
        patch_aiohttp_session,
        response_mock,
        expected_owner,
        expected_owner_role,
        expected_platform,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def support_chat_search(*args, **kwargs):
        expected_data = {
            'owner': {
                'id': expected_owner,
                'role': expected_owner_role,
                'platform': expected_platform,
            },
            'date': {'newer_than': start_date},
            'type': 'archive',
        }
        if end_date:
            expected_data['date']['older_than'] = end_date
        assert kwargs['json'] == expected_data
        return response_mock(json=answer_data)

    monkeypatch.setattr(
        protocol_app, 'passport', conftest.MockPassportClient(),
    )
    data['start_date'] = start_date
    if end_date:
        data['end_date'] = end_date
    response = await protocol_client.post(
        url, headers=headers, data=json.dumps(data),
    )
    assert response.status == expected_code
    if expected_result:
        assert await response.json() == expected_result


@pytest.mark.parametrize(
    [
        'headers',
        'url',
        'data',
        'start_date',
        'end_date',
        'chat_response_mocks',
        'expected_code',
        'expected_result',
        'expected_requests',
    ],
    [
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/supporthistory',
            {'user_id': '5ff4901c583745e089e55be4a8c7a88d'},
            '2017-08-09',
            None,
            [
                {
                    'chats': [
                        {
                            'id': 'id1',
                            'metadata': {
                                'created': '2017-12-11T18:08:56+0300',
                                'user_locale': 'en',
                            },
                        },
                    ],
                },
                {
                    'chats': [
                        {
                            'id': 'id2',
                            'metadata': {
                                'created': '2017-12-12T18:08:56+0300',
                                'user_locale': 'en',
                            },
                        },
                    ],
                },
            ],
            200,
            {
                'chats': [
                    {
                        'chat_id': 'id2',
                        'chat_name': 'Emergency chat from 12.12.2017',
                        'created': '2017-12-12T18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'safety_center',
                    },
                    {
                        'chat_id': 'id1',
                        'chat_name': 'Appeal from 11.12.2017',
                        'created': '2017-12-11T' '18:08:56+0300',
                        'handler_type': 'realtime',
                        'service': 'taxi',
                    },
                ],
            },
            [
                {
                    'owner': {
                        'id': '000000000000000000000000',
                        'role': 'client',
                        'platform': 'android',
                    },
                    'date': {'newer_than': '2017-08-09'},
                    'type': 'archive',
                },
                {
                    'owner': {
                        'id': '123',
                        'role': 'safety_center_client',
                        'platform': 'android',
                    },
                    'date': {'newer_than': '2017-08-09'},
                    'type': 'archive',
                },
            ],
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'support_chat.header': {
            'ru': 'Обращение от %(date)s',
            'en': 'Appeal from %(date)s',
        },
        'support_chat.emergency_header': {
            'ru': 'Экстренное обращение от %(date)s',
            'en': 'Emergency chat from %(date)s',
        },
    },
)
@pytest.mark.config(
    PROTOCOL_ADJACENT_SERVICES={'taxi': ['safety_center']},
    PROTOCOL_DEFAULT_HANDLER_TYPES={
        'taxi': 'realtime',
        'safety_center': 'realtime',
    },
)
async def test_support_history_with_adjacent_services(
        monkeypatch,
        protocol_client,
        protocol_app,
        mock_get_users,
        headers,
        url,
        data,
        start_date,
        end_date,
        chat_response_mocks,
        expected_code,
        expected_result,
        patch_aiohttp_session,
        response_mock,
        expected_requests,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def support_chat_search(*args, **kwargs):
        expected_data = expected_requests.pop(0)
        if end_date:
            expected_data['date']['older_than'] = end_date
        assert kwargs['json'] == expected_data
        return response_mock(json=chat_response_mocks.pop(0))

    monkeypatch.setattr(
        protocol_app, 'passport', conftest.MockPassportClient(),
    )
    data['start_date'] = start_date
    if end_date:
        data['end_date'] = end_date
    response = await protocol_client.post(
        url, headers=headers, data=json.dumps(data),
    )
    assert response.status == expected_code
    if expected_result:
        assert await response.json() == expected_result
