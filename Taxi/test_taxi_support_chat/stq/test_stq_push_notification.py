# pylint: disable=redefined-outer-name,unused-variable
import json

import bson
import pytest

from testsuite.utils import callinfo

from taxi_support_chat.stq import stq_task


TRANSLATIONS = {
    'user_support_chat.support_name.yandex_support': {'ru': 'Саппорт яндекс'},
}


@pytest.mark.now('2020-01-09T12:00:00')
@pytest.mark.config(
    USER_CHAT_PUSH_NOTIFICATIONS={
        'lavka_support': {
            'new_message': {
                'msg': {
                    'keyset': 'client_messages',
                    'key': 'backend.push_notifications.lavka_msg',
                },
                'extra_chat_fields': ['new_messages'],
                'default_locale': 'ru',
            },
            'read_message': {
                'extra_chat_fields': ['new_messages'],
                'default_locale': 'ru',
            },
            'delay': 5,
        },
    },
)
@pytest.mark.parametrize(
    ('request_name', 'expected_stq'),
    [
        ('create_lavka_chat', 'new_message'),
        ('create_other_chat', 'no_calls'),
        ('add_message_lavka_chat', 'new_message'),
        ('add_message_other_chat', 'no_calls'),
        ('read_lavka_chat', 'read_message'),
        ('read_other_chat', 'no_calls'),
    ],
)
@pytest.mark.translations(client_messages=TRANSLATIONS)
async def test_is_stq_task_queued(
        request_name, expected_stq, load_json, stq, web_app_client,
):
    request = load_json('requests.json')[request_name]
    await web_app_client.post(
        request['handle'], data=json.dumps(request['data']),
    )

    try:
        stq_call = stq.taxi_support_chat_push_notifications.next_call()
    except callinfo.CallQueueEmptyError:
        stq_call = None

    expected_calls = load_json('expected_stq_calls.json')[expected_stq]
    assert stq_call == expected_calls
    assert stq.is_empty


@pytest.mark.config(
    USER_CHAT_PUSH_NOTIFICATIONS={
        'lavka_support': {
            'new_message': {
                'msg': {
                    'keyset': 'client_messages',
                    'key': 'backend.push_notifications.lavka_msg',
                },
                'extra_chat_fields': ['new_messages'],
                'default_locale': 'ru',
            },
            'read_message': {
                'extra_chat_fields': ['new_messages'],
                'default_locale': 'ru',
            },
        },
        'datetime_support': {
            'new_message': {
                'msg': {
                    'keyset': 'client_messages',
                    'key': 'backend.push_notifications.timestamp_msg',
                },
                'extra_chat_fields': [
                    'new_messages',
                    'test_timestamp',
                    'test_list',
                    'test_dict',
                ],
                'default_locale': 'ru',
            },
            'read_message': {
                'extra_chat_fields': ['new_messages', 'test_timestamp'],
                'default_locale': 'ru',
            },
        },
    },
)
@pytest.mark.parametrize(
    ('chat_id', 'event', 'should_send', 'expected_call'),
    [
        (
            bson.ObjectId('5e285103779fb3831c8b4ad8'),
            'new_message',
            True,
            'new_message_1',
        ),
        (
            bson.ObjectId('5e285103779fb3831c8b4ad8'),
            'read_message',
            True,
            'read_message_1',
        ),
        (
            bson.ObjectId('5e285103779fb3831c8b4ad9'),
            'new_message',
            False,
            None,
        ),
        (
            bson.ObjectId('5e285103779fb3831c8b4ad9'),
            'read_message',
            False,
            None,
        ),
        (
            bson.ObjectId('5e285103779fb3831c8b4ada'),
            'new_message',
            False,
            None,
        ),
        (
            bson.ObjectId('5e285103779fb3831c8b4ada'),
            'read_message',
            False,
            None,
        ),
        (
            bson.ObjectId('5e285103779fb3831c8b4adb'),
            'new_message',
            True,
            'new_message_2',
        ),
        (
            bson.ObjectId('5e285103779fb3831c8b4adb'),
            'read_message',
            True,
            'read_message_2',
        ),
        (
            bson.ObjectId('5e285103779fb3831c8b4aa2'),
            'new_message',
            True,
            'new_message_3',
        ),
    ],
)
async def test_send_push_notification(
        chat_id,
        event,
        should_send,
        expected_call,
        load_json,
        mock_ucommunications,
        stq3_context,
        stq,
):
    await stq_task.push_notification_task(stq3_context, chat_id, event)

    assert mock_ucommunications.has_calls == should_send
    if should_send:
        assert mock_ucommunications.times_called == 1

        expected_data = load_json('expected_ucommunications_calls.json')[
            expected_call
        ]
        request = mock_ucommunications.next_call()['request']
        assert request.json == expected_data
