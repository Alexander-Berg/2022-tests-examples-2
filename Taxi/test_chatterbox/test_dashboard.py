# pylint: disable=no-self-use, too-many-lines, unused-variable

import pytest

from taxi import discovery


CHATS = {
    'offered_chat_id': {
        'new_message_count': 1,
        'messages': [
            {
                'id': 'message_0',
                'text': 'text_0',
                'metadata': {'created': '2018-05-06T10:00:00'},
                'sender': {'id': 'toert', 'role': 'support'},
            },
        ],
    },
    'in_progress_chat_id': {
        'new_message_count': 4,
        'messages': [
            {
                'id': 'message_0',
                'text': 'text_0',
                'metadata': {
                    'created': '2018-05-06T10:00:00',
                    'attachments': [{'id': 1}],
                },
                'sender': {'id': 'toert', 'role': 'client'},
            },
            {
                'id': 'message_1',
                'text': 'text_1',
                'metadata': {'created': '2018-05-06T10:00:00'},
                'sender': {'id': 'toert', 'role': 'support'},
            },
            {
                'id': 'message_2',
                'text': 'text_2',
                'metadata': {
                    'created': '2018-05-06T10:00:00',
                    'attachments': [{'id': 1}],
                    'encrypt_key': '123',
                },
                'sender': {'id': 'toert', 'role': 'client'},
            },
            {
                'id': 'message_3',
                'text': 'text_1',
                'metadata': {'created': '2018-05-06T10:00:00'},
                'sender': {'id': 'toert', 'role': 'system_scenarios'},
            },
        ],
    },
    'accepted_chat_id_1': {
        'new_message_count': 3,
        'messages': [
            {
                'id': 'message_2',
                'text': 'text_2',
                'metadata': {'created': '2018-05-06T10:00:00'},
                'sender': {'id': 'toert', 'role': 'support'},
            },
        ],
    },
    'accepted_chat_id_2': {
        'new_message_count': 4,
        'messages': [
            {
                'id': 'message_1',
                'text': 'text_3',
                'metadata': {
                    'created': '2018-05-06T10:00:00',
                    'encrypt_key': '123',
                },
                'sender': {'id': 'system', 'role': 'system_scenarios'},
            },
        ],
    },
    'accepted_chat_id_3': {
        'new_message_count': 5,
        'messages': [
            {
                'id': 'message',
                'text': 'text',
                'metadata': {'created': '2018-05-05T10:00:00'},
                'sender': {'id': 'toert', 'role': 'client'},
            },
            {
                'id': 'message_5',
                'text': 'text_4',
                'metadata': {
                    'created': '2018-05-05T10:00:00',
                    'attachments': [{'id': 1}],
                },
                'sender': {'id': 'toert', 'role': 'support'},
            },
        ],
    },
    'empty_message_task_id_1': {'new_message_count': 0, 'messages': []},
    'empty_message_task_id_2': {'new_message_count': 0, 'messages': []},
}


@pytest.mark.config(
    CHATTERBOX_LINES_OFFER_TIMEOUT={'first': 3600, '__default__': 600},
)
@pytest.mark.parametrize(
    'expected_code, expected_data',
    [
        (
            200,
            {
                'next_request_timeout': 5,
                'tasks': [
                    {
                        'id': 'accepted_task_id_2',
                        'last_message': {
                            'created': '2018-05-06T10:00:00',
                            'text': 'text_3',
                            'is_file': False,
                            'encrypt_key': '123',
                        },
                        'status': 'waiting_support_answer',
                        'unread_messages_count': 1,
                        'offer_time': '2018-05-05T12:33:56+0000',
                        'reject_time': '2018-05-05T13:33:56+0000',
                    },
                    {
                        'id': 'accepted_task_id_1',
                        'last_message': {
                            'created': '2018-05-06T10:00:00',
                            'text': 'text_2',
                            'is_file': False,
                        },
                        'offer_time': '2018-05-05T12:34:56+0000',
                        'reject_time': '2018-05-05T13:34:56+0000',
                        'status': 'waiting_user_answer',
                        'unread_messages_count': 0,
                    },
                    {
                        'id': 'accepted_task_id_3',
                        'last_message': {
                            'created': '2018-05-05T10:00:00',
                            'text': 'text_4',
                            'is_file': True,
                        },
                        'status': 'waiting_user_answer',
                        'unread_messages_count': 0,
                        'offer_time': '2018-05-05T12:34:57+0000',
                        'reject_time': '2018-05-05T13:34:57+0000',
                    },
                    {
                        'id': 'accepted_task_id_4',
                        'last_message': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'text': 'some description',
                            'is_file': False,
                        },
                        'first_of_last_messages': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'text': 'some description',
                            'is_file': False,
                        },
                        'status': 'waiting_support_answer',
                        'unread_messages_count': 1,
                        'offer_time': '2018-05-05T12:34:58+0000',
                        'reject_time': '2018-05-05T13:34:58+0000',
                    },
                    {
                        'id': 'accepted_task_id_5',
                        'last_message': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'text': 'some description',
                            'is_file': False,
                        },
                        'first_of_last_messages': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'text': 'some description',
                            'is_file': False,
                        },
                        'status': 'waiting_support_answer',
                        'unread_messages_count': 1,
                        'offer_time': '2018-05-05T12:34:58+0000',
                        'reject_time': '2018-05-05T13:34:58+0000',
                    },
                    {
                        'id': 'empty_accepted_task_id',
                        'last_message': {},
                        'status': 'waiting_support_answer',
                        'unread_messages_count': 0,
                        'offer_time': '2018-05-05T12:34:58+0000',
                        'reject_time': '2018-05-05T13:34:58+0000',
                    },
                    {
                        'id': 'empty_in_progress_task_id',
                        'last_message': {},
                        'status': 'in_progress',
                        'unread_messages_count': 0,
                        'offer_time': '2018-05-05T12:34:58+0000',
                        'reject_time': '2018-05-05T13:34:58+0000',
                    },
                    {
                        'id': 'offered_task_id',
                        'last_message': {
                            'created': '2018-05-06T10:00:00',
                            'text': 'text_0',
                            'is_file': False,
                        },
                        'status': 'offered',
                        'unread_messages_count': 0,
                        'offer_time': '2018-05-05T12:34:58+0000',
                        'reject_time': '2018-05-05T13:34:58+0000',
                    },
                    {
                        'id': 'in_progress_task_id',
                        'last_message': {
                            'created': '2018-05-06T10:00:00',
                            'text': 'text_1',
                            'is_file': False,
                        },
                        'first_of_last_messages': {
                            'created': '2018-05-06T10:00:00',
                            'text': 'text_2',
                            'is_file': True,
                            'encrypt_key': '123',
                        },
                        'status': 'in_progress',
                        'unread_messages_count': 2,
                        'offer_time': '2018-05-05T12:34:59+0000',
                        'reject_time': '2018-05-05T12:44:59+0000',
                    },
                ],
            },
        ),
    ],
)
async def test_dashboard(
        cbox,
        patch_aiohttp_session,
        expected_code,
        expected_data,
        response_mock,
        mock_st_get_comments,
        mock_st_get_ticket,
        mock_st_get_all_attachments,
):
    mock_st_get_comments([])
    mock_st_get_all_attachments(empty=True)

    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def patch_request(method, url, headers, **kwargs):
        chat_id = str(url).split('/')[5]
        return response_mock(json=CHATS[chat_id])

    await cbox.query('/v1/tasks/dashboard/', headers={'Accept-Language': 'en'})
    assert cbox.status == expected_code
    assert cbox.body_data == expected_data
