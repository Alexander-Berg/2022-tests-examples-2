# pylint: disable=broad-except

import http
import json

import pytest


@pytest.mark.parametrize(
    'data, expected_status, expected_chats, expected_phone',
    [
        ({}, http.HTTPStatus.BAD_REQUEST, None, None),
        ({'user': {'id': 'non_existent_user'}}, http.HTTPStatus.OK, [], None),
        (
            {'user': {'phone': 'non_existent_phone'}},
            http.HTTPStatus.OK,
            [],
            None,
        ),
        (
            {'user': {'id': '5b4f5059779fb332fcc29999'}},
            http.HTTPStatus.OK,
            [
                ('539eb65be7e5b1f53980dfa8', None),
                ('539eb65be7e5b1f53980dfa9', None),
            ],
            None,
        ),
        (
            {'user': {'phone': '+79999999999'}, 'history_filter': {}},
            http.HTTPStatus.OK,
            [('5b436ece779fb3302cc784bb', 5), ('5b436ece779fb3302cc784bf', 5)],
            {
                'id': '5b4f5092779fb332fcc26153',
                'phone': '+79999999999',
                'type': 'yandex',
            },
        ),
        (
            {
                'user': {
                    'id': '5df1fc13779fb3085850a6cd',
                    'phone': '+79999999999',
                },
                'chat_types': ['driver'],
            },
            http.HTTPStatus.OK,
            [('5df1fd0b779fb3085850a6ce', None)],
            {
                'id': '5b4f5092779fb332fcc26153',
                'phone': '+79999999999',
                'type': 'yandex',
            },
        ),
        (
            {
                'user': {
                    'id': '5b4f5059779fb332fcc29999',
                    'phone': '+79999999999',
                },
                'date': {'older_than': '2018-07-05T10:59:50.035Z'},
            },
            http.HTTPStatus.OK,
            [
                ('539eb65be7e5b1f53980dfa9', None),
                ('5b436ece779fb3302cc784bb', None),
                ('5b436ece779fb3302cc784bf', None),
            ],
            {
                'id': '5b4f5092779fb332fcc26153',
                'phone': '+79999999999',
                'type': 'yandex',
            },
        ),
        (
            {
                'user': {'id': '5b4f5092779fb332fcc26154'},
                'history_filter': {'include_history': False},
                'offset': 1,
                'limit': 2,
            },
            http.HTTPStatus.OK,
            [
                ('5df208a0779fb3085850a6d0', None),
                ('closed_driver_chat_id', None),
            ],
            None,
        ),
        (
            {
                'user': {'id': 'yuid_yandex'},
                'history_filter': {'include_history': True},
                'date': {'newer_than': '2018-07-05T10:59:50.018Z'},
            },
            http.HTTPStatus.OK,
            [('5a436ca8779fb3302cc784ea', 2)],
            None,
        ),
        (
            {
                'user': {'id': 'yuid_yandex'},
                'chat_ids': ['5b56f0be8d64e6667db1440e'],
            },
            http.HTTPStatus.OK,
            [('5b56f0be8d64e6667db1440e', None)],
            None,
        ),
        (
            {
                'user': {'id': '5b4f5092779fb332fcc26153'},
                'chat_ids': ['5b436ece779fb3302cc784bf'],
                'history_filter': {
                    'date': {
                        'newer_than': '2018-07-04T05:06:50.000Z',
                        'older_than': '2018-07-19T20:21:50.000Z',
                    },
                },
            },
            http.HTTPStatus.OK,
            [('5b436ece779fb3302cc784bf', 3)],
            None,
        ),
    ],
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
@pytest.mark.filldb(user_chat_messages='search')
async def test_search_by_user(
        mock_get_user_phone,
        web_app_client,
        db,
        data,
        expected_status,
        expected_chats,
        expected_phone,
):
    response = await web_app_client.post(
        '/v1/chat/search_by_user/', data=json.dumps(data),
    )
    assert response.status == expected_status
    if expected_status != http.HTTPStatus.OK:
        return

    result = await response.json()
    if expected_chats is not None:
        assert len(result['chats']) == len(expected_chats)
        for chat, expected in zip(result['chats'], expected_chats):
            chat_id, messages = expected
            assert chat['id'] == chat_id
            if messages is not None:
                assert 'messages' in chat and len(chat['messages']) == messages
            else:
                assert 'messages' not in chat
    if expected_phone is not None:
        assert result.get('phone') == expected_phone
    else:
        assert 'phone' not in result
