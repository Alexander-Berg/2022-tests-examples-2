# pylint: disable=protected-access
import bson
import pytest

from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.internal import const
from taxi_support_chat.internal import support_chats
from taxi_support_chat.stq import stq_task


@pytest.mark.parametrize(
    ('task_id', 'chat_id', 'kwargs', 'expected_request', 'expected_uid'),
    (
        (
            bson.ObjectId('5b436ca8779fb3302cc784ba'),
            '5b436ca8779fb3302cc784ba',
            {'meta': {'yandex_uid': 'test_uid', 'field': 'value'}},
            {
                'provider': 'taxi',
                'provider_chat_id': '5b436ca8779fb3302cc784ba',
                'provider_meta': {
                    'yandex_uid': 'test_uid',
                    'field': 'value',
                    'owner_id': '5b4f5059779fb332fcc26152',
                },
                'messages': [
                    {
                        'id': 'message_11',
                        'type': 0,
                        'text': 'text_1',
                        'timestamp': 1530421430,
                    },
                ],
            },
            '5b4f5059779fb332fcc26152',
        ),
        (
            bson.ObjectId('5b436ca8779fb3302cc784ba'),
            '5b436ece779fb3302cc784bb',
            {
                'meta': {'yandex_uid': 'test_uid'},
                'hidden_comment': 'test_comment',
            },
            {
                'provider': 'taxi',
                'provider_chat_id': '5b436ca8779fb3302cc784ba',
                'provider_meta': {
                    'yandex_uid': 'test_uid',
                    'owner_id': '5b4f5092779fb332fcc26153',
                },
                'messages': [
                    {
                        'id': 'message_23',
                        'type': 0,
                        'text': 'text_3',
                        'timestamp': 1531502150,
                        'attachments_id': ['attach_1', 'attach_2'],
                    },
                    {
                        'id': 'message_25',
                        'type': 0,
                        'text': 'text_5',
                        'timestamp': 1532042510,
                    },
                    {
                        'id': '5b436ca8779fb3302cc784ba_1530895490',
                        'type': 1,
                        'text': 'test_comment',
                        'timestamp': 1530895490,
                    },
                ],
            },
            '5b4f5092779fb332fcc26153',
        ),
        (
            bson.ObjectId('5b436ca8779fb3302cc784bf'),
            '5b436ca8779fb3302cc784bf',
            {'meta': {'yandex_uid': 'test_uid', 'field': 'value'}},
            {},
            '',
        ),
    ),
)
async def test_send_messages_to_carsharing(
        stq3_context: stq_context.Context,
        task_id,
        chat_id,
        kwargs,
        expected_request,
        expected_uid,
        response_mock,
        mockserver,
):
    @mockserver.json_handler('/drive/api/taxi_chat/messages/add')
    def _mock_drive(request):
        assert request.json == expected_request
        assert request.headers['X-Uid'] == expected_uid
        return {}

    await stq_task.send_events_to_carsharing(
        stq3_context, task_id, chat_id, **kwargs,
    )

    chat = await stq3_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    for message in chat['messages']:
        if support_chats.get_api_role(message['author']) != const.SUPPORT_ROLE:
            assert message['metadata']['sent_to_carsharing']
