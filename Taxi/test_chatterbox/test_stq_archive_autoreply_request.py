# pylint: disable=too-many-arguments,redefined-outer-name
import bson
import pytest

from taxi import discovery
from taxi.clients import messenger_chat_mirror
from taxi.clients import support_chat

from chatterbox import stq_task


@pytest.mark.now('2018-06-15T12:34:00')
@pytest.mark.parametrize(
    ('task_id', 'expected_autoreply_call'),
    [
        (
            bson.ObjectId('5b2cae5cb2682a976914caa1'),
            {
                'chat_id': '5b2cae5cb2682a976914caa1',
                'dialog': {
                    'messages': [
                        {
                            'author': 'user',
                            'created': '2018-05-05T15:34:56Z',
                            'id': 1,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'text',
                        },
                    ],
                },
                'features': [
                    {'key': 'city', 'value': 'Moscow'},
                    {'key': 'country', 'value': 'rus'},
                    {'key': 'macro_id', 'value': 'some_macro_id'},
                    {'key': 'service', 'value': 'eats'},
                    {'key': 'user_phone', 'value': 'some_user_phone'},
                    {'key': 'zendesk_profile', 'value': 'yataxi'},
                    {'key': 'request_repeated', 'value': True},
                    {'key': 'chat_type', 'value': 'client'},
                    {'key': 'line', 'value': 'first'},
                    {'key': 'screen_attach', 'value': False},
                    {'key': 'is_reopen', 'value': False},
                    {'key': 'number_of_reopens', 'value': 0},
                    {'key': 'all_tags', 'value': []},
                    {'key': 'last_message_tags', 'value': []},
                    {'key': 'comment_lowercased', 'value': 'text'},
                    {'key': 'number_of_orders', 'value': 0},
                    {'key': 'minutes_from_order_creation', 'value': 59039},
                    {'key': 'last_support_action', 'value': 'hidden_comment'},
                ],
                'feedback': True,
            },
        ),
        (
            bson.ObjectId('5c2cae5cb2682a976914caa1'),
            {
                'chat_id': '5c2cae5cb2682a976914caa1',
                'dialog': {
                    'messages': [
                        {
                            'author': 'user',
                            'created': '2018-05-05T15:34:56Z',
                            'id': 1,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'text',
                        },
                    ],
                },
                'features': [
                    {'key': 'city', 'value': 'Moscow'},
                    {'key': 'country', 'value': 'rus'},
                    {'key': 'macro_id', 'value': 'some_macro_id'},
                    {'key': 'service', 'value': 'eats'},
                    {'key': 'user_phone', 'value': 'some_user_phone'},
                    {'key': 'zendesk_profile', 'value': 'yataxi'},
                    {'key': 'request_repeated', 'value': True},
                    {'key': 'chat_type', 'value': 'messenger'},
                    {'key': 'line', 'value': 'first'},
                    {'key': 'screen_attach', 'value': False},
                    {'key': 'is_reopen', 'value': False},
                    {'key': 'number_of_reopens', 'value': 0},
                    {'key': 'all_tags', 'value': []},
                    {'key': 'last_message_tags', 'value': []},
                    {'key': 'comment_lowercased', 'value': 'text'},
                    {'key': 'number_of_orders', 'value': 0},
                    {'key': 'minutes_from_order_creation', 'value': 59039},
                    {'key': 'last_support_action', 'value': 'empty'},
                ],
                'feedback': True,
            },
        ),
        (
            bson.ObjectId('5b2cae5cb2682a976914caa2'),
            {
                'chat_id': '5b2cae5cb2682a976914caa2',
                'dialog': {
                    'messages': [
                        {
                            'author': 'user',
                            'created': '2018-05-05T15:34:56Z',
                            'id': 1,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'text',
                        },
                    ],
                },
                'features': [
                    {'key': 'driver_license', 'value': 'AAAAA'},
                    {'key': 'zendesk_profile', 'value': 'yataxi'},
                    {'key': 'request_repeated', 'value': True},
                    {'key': 'chat_type', 'value': 'driver'},
                    {'key': 'line', 'value': 'first'},
                    {'key': 'screen_attach', 'value': False},
                    {'key': 'is_reopen', 'value': False},
                    {'key': 'number_of_reopens', 'value': 0},
                    {'key': 'all_tags', 'value': []},
                    {'key': 'last_message_tags', 'value': []},
                    {'key': 'comment_lowercased', 'value': 'text'},
                    {'key': 'number_of_orders', 'value': 0},
                    {'key': 'minutes_from_order_creation', 'value': 59039},
                    {'key': 'last_support_action', 'value': 'empty'},
                ],
                'feedback': True,
            },
        ),
    ],
)
@pytest.mark.config(
    CHATTERBOX_AUTOREPLY={
        'test': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {
                'chat_type': {'#in': ['client', 'driver', 'messenger']},
            },
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'test',
            'event_type': 'test',
            'need_driver_meta': True,
        },
    },
)
async def test_archive_autoreply_request(
        cbox,
        mock,
        patch,
        mock_chat_get_history,
        mock_translate,
        patch_aiohttp_session,
        mock_personal,
        response_mock,
        monkeypatch,
        load_json,
        task_id,
        expected_autoreply_call,
):
    async def _dummy_get_history(self, chat_id, *args, **kwargs):
        return {
            'messages': [
                {
                    'id': 1,
                    'sender': {'id': 'user_id', 'role': 'client'},
                    'text': 'text',
                    'metadata': {
                        'created': '2018-05-05T15:34:56',
                        'attachments': [{'id': 'some_attachment_id'}],
                    },
                },
            ],
        }

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_history', _dummy_get_history,
    )
    monkeypatch.setattr(
        messenger_chat_mirror.MessengerChatMirrorApiClient,
        'get_history',
        _dummy_get_history,
    )

    mock_translate('ru')

    supportai_api_service = discovery.find_service('supportai-api')

    @patch_aiohttp_session(supportai_api_service.url, 'POST')
    def _dummy_autoreply_ai(method, url, **kwargs):
        assert method == 'post'
        assert (
            url
            == supportai_api_service.url + '/supportai-api/v1/support_internal'
        )
        return response_mock(json={})

    await stq_task.chatterbox_archive_autoreply(cbox.app, task_id)

    autoreply_calls_ai = [
        call['kwargs']['json'] for call in _dummy_autoreply_ai.calls
    ]
    assert autoreply_calls_ai[0] == expected_autoreply_call
