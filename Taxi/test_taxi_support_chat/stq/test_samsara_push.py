# pylint: disable=protected-access
import datetime

import bson
import pytest

from taxi import discovery

from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.internal import const
from taxi_support_chat.internal import support_chats
from taxi_support_chat.stq import stq_task


NOW = datetime.datetime(2018, 6, 15, 12, 34)


@pytest.mark.config(CHATTERBOX_SAMSARA_PUSH_MESSAGE_DELAY=10)
@pytest.mark.parametrize(
    ('task_id', 'chat_id', 'kwargs', 'expected_request', 'second_queue_call'),
    (
        (
            bson.ObjectId('5b436ca8779fb3302cc784ba'),
            '5b436ca8779fb3302cc784ba',
            {'meta': {'yandex_uid': 'test_uid', 'field': 'value'}},
            {
                'messages': [
                    {
                        'id': 'message_11',
                        'line_id': 'samsara',
                        'origin': 'client',
                        'origin_meaning_id': '5b4f5059779fb332fcc26152',
                        'task_id': '5b436ca8779fb3302cc784ba',
                        'task_meta_info': {
                            'field': 'value',
                            'yandex_uid': 'test_uid',
                        },
                        'text': 'text_1',
                        'timestamp_iso': '2018-07-01T02:03:50.000000Z',
                        'attachment_ids': [],
                    },
                    {
                        'id': 'message_12',
                        'line_id': 'samsara',
                        'origin': 'support',
                        'origin_meaning_id': '5b4f5059779fb332fcc26152',
                        'task_id': '5b436ca8779fb3302cc784ba',
                        'task_meta_info': {
                            'field': 'value',
                            'yandex_uid': 'test_uid',
                        },
                        'text': 'text_2',
                        'timestamp_iso': '2018-07-04T05:06:50.000000Z',
                        'attachment_ids': [],
                    },
                ],
            },
            False,
        ),
        (
            bson.ObjectId('5b436ca8779fb3302cc784ba'),
            '5b436ece779fb3302cc784bb',
            {
                'meta': {'yandex_uid': 'test_uid'},
                'hidden_comment': 'test_comment',
            },
            {
                'messages': [
                    {
                        'id': 'message_21',
                        'line_id': 'samsara',
                        'origin': 'client',
                        'origin_meaning_id': '5b4f5092779fb332fcc26153',
                        'task_id': '5b436ca8779fb3302cc784ba',
                        'task_meta_info': {'yandex_uid': 'test_uid'},
                        'text': 'text_1',
                        'timestamp_iso': '2018-07-04T05:06:50.000000Z',
                        'attachment_ids': [],
                    },
                    {
                        'id': 'message_22',
                        'line_id': 'samsara',
                        'origin': 'support',
                        'origin_meaning_id': 'some_support',
                        'task_id': '5b436ca8779fb3302cc784ba',
                        'task_meta_info': {'yandex_uid': 'test_uid'},
                        'text': 'text_2',
                        'timestamp_iso': '2018-07-10T11:12:50.000000Z',
                        'attachment_ids': [],
                    },
                    {
                        'id': 'message_23',
                        'line_id': 'samsara',
                        'origin': 'client',
                        'origin_meaning_id': '5b4f5092779fb332fcc26153',
                        'task_id': '5b436ca8779fb3302cc784ba',
                        'task_meta_info': {'yandex_uid': 'test_uid'},
                        'text': 'text_3',
                        'timestamp_iso': '2018-07-13T14:15:50.000000Z',
                        'attachment_ids': ['attach_1', 'attach_2'],
                    },
                    {
                        'id': 'message_24',
                        'line_id': 'samsara',
                        'origin': 'support',
                        'origin_meaning_id': 'another_support',
                        'task_id': '5b436ca8779fb3302cc784ba',
                        'task_meta_info': {'yandex_uid': 'test_uid'},
                        'text': 'text_4',
                        'timestamp_iso': '2018-07-16T17:18:50.000000Z',
                        'attachment_ids': [],
                    },
                    {
                        'id': 'message_25',
                        'line_id': 'samsara',
                        'origin': 'client',
                        'origin_meaning_id': '5b4f5092779fb332fcc26153',
                        'task_id': '5b436ca8779fb3302cc784ba',
                        'task_meta_info': {'yandex_uid': 'test_uid'},
                        'text': 'text_5',
                        'timestamp_iso': '2018-07-19T20:21:50.000000Z',
                        'attachment_ids': [],
                    },
                ],
            },
            False,
        ),
        (
            bson.ObjectId('5b436ca8779fb3302cc784bf'),
            '5b436ca8779fb3302cc784bf',
            {'meta': {'yandex_uid': 'test_uid', 'field': 'value'}},
            {
                'messages': [
                    {
                        'id': 'message_31',
                        'line_id': 'samsara',
                        'origin': 'client',
                        'origin_meaning_id': '5b4f5059779fb332fcc26152',
                        'task_id': '5b436ca8779fb3302cc784bf',
                        'task_meta_info': {
                            'field': 'value',
                            'yandex_uid': 'test_uid',
                        },
                        'text': 'text_1',
                        'timestamp_iso': '2018-07-01T02:03:50.000000Z',
                        'attachment_ids': [],
                    },
                    {
                        'id': 'message_32',
                        'line_id': 'samsara',
                        'origin': 'support',
                        'origin_meaning_id': '5b4f5059779fb332fcc26152',
                        'task_id': '5b436ca8779fb3302cc784bf',
                        'task_meta_info': {
                            'field': 'value',
                            'yandex_uid': 'test_uid',
                        },
                        'text': 'text_2',
                        'timestamp_iso': '2018-07-04T05:06:50.000000Z',
                        'attachment_ids': [],
                    },
                ],
            },
            False,
        ),
        (
            bson.ObjectId('5b436ca8779fb3302cc784bf'),
            '5b436ca8779fb3302cc784bf',
            {
                'meta': {'yandex_uid': 'test_uid', 'field': 'value'},
                'required_msg_id': 'dont_seek_me',
            },
            {
                'messages': [
                    {
                        'id': 'message_31',
                        'line_id': 'samsara',
                        'origin': 'client',
                        'origin_meaning_id': '5b4f5059779fb332fcc26152',
                        'task_id': '5b436ca8779fb3302cc784bf',
                        'task_meta_info': {
                            'field': 'value',
                            'yandex_uid': 'test_uid',
                        },
                        'text': 'text_1',
                        'timestamp_iso': '2018-07-01T02:03:50.000000Z',
                        'attachment_ids': [],
                    },
                    {
                        'id': 'message_32',
                        'line_id': 'samsara',
                        'origin': 'support',
                        'origin_meaning_id': '5b4f5059779fb332fcc26152',
                        'task_id': '5b436ca8779fb3302cc784bf',
                        'task_meta_info': {
                            'field': 'value',
                            'yandex_uid': 'test_uid',
                        },
                        'text': 'text_2',
                        'timestamp_iso': '2018-07-04T05:06:50.000000Z',
                        'attachment_ids': [],
                    },
                ],
            },
            True,
        ),
        (
            bson.ObjectId('5b436ca8779fb3302cc784bf'),
            '5b436ca8779fb3302cc784bf',
            {
                'meta': {'yandex_uid': 'test_uid', 'field': 'value'},
                'required_msg_id': 'message_31',
            },
            {
                'messages': [
                    {
                        'id': 'message_31',
                        'line_id': 'samsara',
                        'origin': 'client',
                        'origin_meaning_id': '5b4f5059779fb332fcc26152',
                        'task_id': '5b436ca8779fb3302cc784bf',
                        'task_meta_info': {
                            'field': 'value',
                            'yandex_uid': 'test_uid',
                        },
                        'text': 'text_1',
                        'timestamp_iso': '2018-07-01T02:03:50.000000Z',
                        'attachment_ids': [],
                    },
                    {
                        'id': 'message_32',
                        'line_id': 'samsara',
                        'origin': 'support',
                        'origin_meaning_id': '5b4f5059779fb332fcc26152',
                        'task_id': '5b436ca8779fb3302cc784bf',
                        'task_meta_info': {
                            'field': 'value',
                            'yandex_uid': 'test_uid',
                        },
                        'text': 'text_2',
                        'timestamp_iso': '2018-07-04T05:06:50.000000Z',
                        'attachment_ids': [],
                    },
                ],
            },
            False,
        ),
    ),
)
@pytest.mark.now(NOW.isoformat())
async def test_send_messages_to_samsara(
        stq3_context: stq_context.Context,
        patch,
        stq,
        task_id,
        chat_id,
        kwargs,
        expected_request,
        second_queue_call,
        response_mock,
        mockserver,
        patch_aiohttp_session,
):
    @mockserver.json_handler(
        f'/samsara/api/integration/chatterbox/v1/task/{task_id}/message',
    )
    def _mock_samsara(request):
        assert request.json == expected_request
        return {}

    chatterbox_service = discovery.find_service('chatterbox')

    # pylint: disable=unused-variable
    @patch_aiohttp_session(chatterbox_service.url, 'GET')
    def patch_request(method, url, **kwargs):
        assert method == 'get'
        assert url.split('/')[-1] == str(task_id)
        assert url == '%s/v1/tasks/%s' % (chatterbox_service.url, task_id)
        return response_mock(json={'line': 'samsara'}, status=200)

    await stq_task.send_messages_to_samsara(
        stq3_context, task_id, chat_id, **kwargs,
    )
    if second_queue_call:
        stq_call = stq.support_chat_send_messages_to_samsara.next_call()
        assert stq_call['queue'] == 'support_chat_send_messages_to_samsara'
        assert stq_call['eta'] == NOW + datetime.timedelta(seconds=10)
        assert stq_call['args'] == [{'$oid': str(task_id)}, chat_id]
        stq_call['kwargs'].pop('log_extra')
        assert stq_call['kwargs'] == {
            'meta': kwargs.get('meta'),
            'hidden_comment': kwargs.get('hidden_comment'),
            'required_msg_id': kwargs.get('required_msg_id'),
        }
    else:
        chat = await stq3_context.mongo.user_chat_messages.find_one(
            {'_id': bson.ObjectId(chat_id)},
        )
        for message in chat['messages']:
            if (
                    support_chats.get_api_role(message['author'])
                    != const.SUPPORT_ROLE
            ):
                assert message['metadata']['sent_to_samsara']
