# pylint: disable=redefined-outer-name,no-member

import bson
import pytest

from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.stq import stq_task


@pytest.mark.parametrize(
    'chat_id, message_id, expected_kwargs',
    [
        (
            bson.ObjectId('5a436ca8779fb3302cc222ea'),
            'support_to_eats_2',
            {
                'chat_id': {'$oid': '5a436ca8779fb3302cc222ea'},
                'log_extra': None,
                'locale': 'en',
                'message_key': 'user_chat.new_message',
                'deeplink': 'ubermlbv://chat/eats',
                'new_message_count': 1,
                'timestamp': {'$date': 1530410637000},
                'yandex_uid': 'yuid_uber',
            },
        ),
        (
            bson.ObjectId('5a436ca8779fb3302cc784ea'),
            'support_to_eats_1',
            {
                'chat_id': {'$oid': '5a436ca8779fb3302cc784ea'},
                'locale': 'ru',
                'log_extra': None,
                'message_key': 'user_chat.new_message',
                'deeplink': 'yandextaxi://chat/eats',
                'new_message_count': 2,
                'timestamp': {'$date': 1530410630000},
                'yandex_uid': 'yuid_yandex',
            },
        ),
        (
            bson.ObjectId('539eb65be7e5b1f53980dfa8'),
            'message_88',
            {
                'chat_id': {'$oid': '539eb65be7e5b1f53980dfa8'},
                'locale': 'en',
                'log_extra': None,
                'message_key': 'user_chat.new_message',
                'deeplink': 'ubermlbv://chat/eats',
                'new_message_count': 1,
                'timestamp': {'$date': 1530410637000},
                'yandex_uid': 'yuid_uber',
            },
        ),
        (
            bson.ObjectId('5ff4901c583745e089e55be4'),
            'message_88',
            {
                'chat_id': {'$oid': '5ff4901c583745e089e55be4'},
                'locale': 'en',
                'log_extra': None,
                'message_key': 'user_chat.new_message',
                'deeplink': 'ubermlbv://chat/safety_center',
                'new_message_count': 1,
                'timestamp': {'$date': 1530410637000},
                'yandex_uid': 'yuid_uber',
            },
        ),
    ],
)
@pytest.mark.config(
    SUPPORT_CHAT_USE_PLATFORM_TO_SEND_NOTIFICATIONS=True,
    USER_CHAT_PUSH_BY_TYPES={
        'client_support': {
            'deeplink': {
                'uber': 'ubermlbv://chat',
                'yandex': 'yandextaxi://chat',
                'yango': 'yandexyango://chat',
            },
            'tanker_key': 'user_chat.new_message',
        },
        'eats_support': {
            'deeplink': {
                'uber': 'ubermlbv://chat/eats',
                'yandex': 'yandextaxi://chat/eats',
                'yango': 'yandexyango://chat/eats',
            },
            'tanker_key': 'user_chat.new_message',
        },
        'safety_center_support': {
            'deeplink': {
                'uber': 'ubermlbv://chat/safety_center',
                'yandex': 'yandextaxi://chat/safety_center',
                'yango': 'yandexyango://chat/safety_center',
            },
            'tanker_key': 'user_chat.new_message',
        },
    },
)
@pytest.mark.now('2019-07-10T11:20:00')
async def test_task(
        stq3_context: stq_context.Context,
        stq,
        chat_id,
        message_id,
        expected_kwargs,
):
    await stq_task.client_notify_task(
        stq3_context, chat_id=chat_id, message_id=message_id,
    )
    call_args = stq.send_user_chat_push.next_call()
    assert stq.is_empty
    assert call_args['queue'] == 'send_user_chat_push'
    assert call_args['kwargs'] == expected_kwargs
