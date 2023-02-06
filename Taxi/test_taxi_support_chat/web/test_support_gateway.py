# pylint: disable=no-member

import http
import json

import pytest

from taxi_support_chat.internal import const


@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.config(
    SUPPORT_CHAT_SERVICE_NOTIFY=True,
    SUPPORT_CHAT_SERVICE_NOTIFY_FILTERS={
        'support_gateway': {'type': ['safety_center_support']},
    },
)
@pytest.mark.parametrize(
    (
        'data',
        'expected_chats',
        'chat_id',
        'update_data',
        'expected_result',
        'expected_history',
    ),
    [
        (
            {'user': {'id': 'yuid_yandex'}},
            ['5a436ca8779fb3302cc784ea', '5b56f0be8d64e6667db1440e'],
            '5b56f0be8d64e6667db1440e',
            {
                'created_date': '2018-07-18T11:16:25.333000',
                'request_id': 'test_update_1',
                'message': {
                    'text': 'test_update_1',
                    'sender': {'id': 'yuid_yandex', 'role': 'client'},
                    'metadata': {'source': 'support_gateway'},
                },
                'update_metadata': {},
            },
            {'message_id': 'test_update_1'},
            {
                'id': '5b56f0be8d64e6667db1440e',
                'newest_message_id': 'test_update_1',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': None,
                        'nickname': '',
                    },
                    {
                        'id': 'yuid_yandex',
                        'is_owner': True,
                        'role': 'safety_center_client',
                        'platform': 'yandex',
                    },
                ],
                'metadata': {
                    'created': '2018-07-05T10:59:50+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'last_message_from_user': True,
                    'new_messages': 2,
                    'user_locale': 'ru',
                    'ticket_status': 'open',
                    'ask_csat': False,
                    'chatterbox_id': 'chatterbox_id_emergency',
                    'platform': 'yandex',
                },
                'status': {'is_open': True, 'is_visible': True},
                'type': 'safety_center_support',
                'actions': [],
                'view': {'show_message_input': True},
                'messages': [
                    {
                        'id': 'message_emergency_0',
                        'text': 'emergency_text',
                        'metadata': {'created': '2018-07-01T02:03:50+0000'},
                        'sender': {
                            'id': 'emergency_client',
                            'role': 'emergency_client',
                            'sender_type': '',
                        },
                    },
                    {
                        'id': 'support_to_emergency_1',
                        'text': 'emergency_text',
                        'metadata': {'created': '2018-07-01T02:03:50+0000'},
                        'sender': {
                            'id': 'support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                    {
                        'id': 'test_update_1',
                        'text': 'test_update_1',
                        'metadata': {
                            'source': 'support_gateway',
                            'created': '2018-07-18T11:16:25+0000',
                        },
                        'sender': {
                            'id': 'yuid_yandex',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.filldb(user_chat_messages='search')
async def test_update(
        mock_get_user_phone,
        web_app_client,
        stq,
        data,
        expected_chats,
        chat_id,
        update_data,
        expected_result,
        expected_history,
):
    response = await web_app_client.post(
        '/v1/chat/search_by_user/', data=json.dumps(data),
    )
    assert response.status == http.HTTPStatus.OK

    result = await response.json()
    assert expected_chats == [chat['id'] for chat in result['chats']]

    response = await web_app_client.post(
        '/v1/chat/%s/add_update' % chat_id, data=json.dumps(update_data),
    )
    assert response.status == http.HTTPStatus.CREATED
    assert await response.json() == expected_result

    call = stq.taxi_support_chat_support_gateway_notify.next_call()

    assert call['queue'] == 'taxi_support_chat_support_gateway_notify'
    assert call['args'] == [
        {'$oid': chat_id},
        update_data['request_id'],
        const.EVENT_NEW_MESSAGE,
    ]

    response = await web_app_client.get(
        '/v1/chat/%s' % chat_id, params={'include_history': 'true'},
    )
    assert response.status == http.HTTPStatus.OK
    assert await response.json() == expected_history
