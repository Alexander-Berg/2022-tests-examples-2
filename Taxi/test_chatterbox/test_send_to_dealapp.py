# pylint: disable=protected-access
import datetime
import json

import bson
import pytest

from taxi.clients import stq_agent
from taxi.stq import async_worker_ng

from chatterbox import stq_task
from chatterbox.internal import dealapp_tasks

NOW = datetime.datetime(2018, 5, 7, 12, 35)
TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a2')
TASK_ID_WITH_INNER_MESSAGES = bson.ObjectId('5b2cae5cb2682a976914c2a3')


@pytest.mark.config(
    CHATTERBOX_TO_DEALAPP_SETTINGS={
        'enabled': True,
        'max_attempts': 5,
        'retry_eta_multiplier': 10,
    },
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'user_phone': 'phones', 'user_email': 'emails'},
    },
)
@pytest.mark.parametrize(
    'task_id,expected',
    [
        (
            TASK_ID,
            {
                'operator_id': 'admin1',
                'communication_id': '5b2cae5cb2682a976914c2a2',
                'communication_type': 'chat',
                'custom_fields': {
                    'started_at': '2018-05-07T12:30:00+0000',
                    'dialog_line': 'first',
                    'client_phone_number': '+79123456789',
                },
                'client_id': 'user1_id',
                'direction': dealapp_tasks.DEALAPP_CHAT_DIRECTION_INCOMING,
                'communication_parts': [],
            },
        ),
        (
            TASK_ID_WITH_INNER_MESSAGES,
            {
                'operator_id': 'admin1',
                'communication_id': '5b2cae5cb2682a976914c2a3',
                'communication_type': 'chat',
                'custom_fields': {
                    'started_at': '2018-05-07T12:30:00+0000',
                    'dialog_line': 'first',
                    'client_mail': 'user2@test.com',
                },
                'client_id': 'user2_id',
                'direction': dealapp_tasks.DEALAPP_CHAT_DIRECTION_INCOMING,
                'communication_parts': [
                    {
                        'author': {'id': 'superuser', 'type': 'operator'},
                        'body': 'Task created',
                        'created_at': '2018-05-07T12:35:05+0000',
                        'communication_part_id': (
                            '5b2cae5cb2682a976914c2a3_internal_0'
                        ),
                    },
                    {
                        'author': {'id': 'support_vasya', 'type': 'operator'},
                        'body': 'Good request',
                        'created_at': '2018-05-07T12:35:10+0000',
                        'communication_part_id': (
                            '5b2cae5cb2682a976914c2a3_internal_1'
                        ),
                    },
                    {
                        'author': {'id': 'superuser', 'type': 'operator'},
                        'body': 'Task closed',
                        'created_at': '2018-05-07T12:38:10+0000',
                        'communication_part_id': (
                            '5b2cae5cb2682a976914c2a3_internal_2'
                        ),
                    },
                ],
            },
        ),
    ],
)
async def test_send_to_dealapp(
        cbox,
        mock,
        monkeypatch,
        mock_chat_get_history,
        mock_dealapp_send_chat,
        mock_personal,
        task_id,
        expected,
):
    mock_chat_get_history({'messages': []})
    mock_dealapp_send_chat = mock_dealapp_send_chat({'status': 'success'})

    @mock
    async def _dummy_put_task(*args, **kwargs):
        pass

    @mock
    async def _dummy_reschedule(*args, **kwargs):
        pass

    monkeypatch.setattr(stq_agent.StqAgentClient, 'put_task', _dummy_put_task)
    monkeypatch.setattr(
        stq_agent.StqAgentClient, 'reschedule', _dummy_reschedule,
    )

    task_info = async_worker_ng.TaskInfo(
        id=task_id,
        exec_tries=0,
        reschedule_counter=0,
        queue='chatterbox_send_to_dealapp_task',
    )
    await stq_task.send_to_dealapp(cbox.app, task_info)
    args = mock_dealapp_send_chat.calls
    assert args
    for arg in args:
        json.dumps(arg)
        assert arg['kwargs'].get('chat') == expected


@pytest.mark.parametrize(
    'task,messages,expected',
    [
        (
            {
                '_id': TASK_ID,
                'created': NOW - datetime.timedelta(minutes=30),
                'meta_info': {'user_uid': '123456'},
            },
            {},
            {
                'communication_parts': [],
                'communication_type': 'chat',
                'client_id': '123456',
                'communication_id': '5b2cae5cb2682a976914c2a2',
                'custom_fields': {'started_at': '2018-05-07T12:05:00+0000'},
                'direction': dealapp_tasks.DEALAPP_CHAT_DIRECTION_INCOMING,
            },
        ),
        (
            {
                '_id': TASK_ID,
                'created': NOW - datetime.timedelta(minutes=30),
                'full_resolve': 3600,
                'type': 'chat',
                'meta_info': {
                    'user_phone': '+79001234567890',
                    'user_email': 'user@test.ru',
                    'order_id': '12345',
                    'theme_name': 'Название тематики',
                    'user_id': '123456',
                },
                'line': 'first',
            },
            {
                'messages': [
                    {
                        '_id': bson.ObjectId('000000000000000000000000'),
                        'timestamp': NOW,
                        'message': 'Привет!',
                        'author_id': 'user007',
                        'author': 'user',
                    },
                    {
                        '_id': bson.ObjectId('000000000000000000000001'),
                        'timestamp': NOW,
                        'message': 'Здравствуй!',
                        'author_id': 'support_vasya',
                        'author': 'support',
                    },
                ],
                'metadata': {'csat_value': 'amazing'},
            },
            {
                'communication_parts': [
                    {
                        'author': {'id': 'user007', 'type': 'client'},
                        'body': 'Привет!',
                        'communication_part_id': '000000000000000000000000',
                        'created_at': '2018-05-07T12:35:00+0000',
                    },
                    {
                        'author': {'id': 'support_vasya', 'type': 'operator'},
                        'body': 'Здравствуй!',
                        'communication_part_id': '000000000000000000000001',
                        'created_at': '2018-05-07T12:35:00+0000',
                    },
                ],
                'client_id': '123456',
                'communication_type': 'chat',
                'communication_id': '5b2cae5cb2682a976914c2a2',
                'custom_fields': {
                    'started_at': '2018-05-07T12:05:00+0000',
                    'expire': '2018-05-07T13:05:00+0000',
                    'client_phone_number': '+79001234567890',
                    'client_mail': 'user@test.ru',
                    'order_number': '12345',
                    'reason': 'Название тематики',
                    'dialog_line': 'first',
                    'csat1': 5,
                },
                'direction': dealapp_tasks.DEALAPP_CHAT_DIRECTION_INCOMING,
            },
        ),
    ],
)
def test_prepare_payload(cbox, task, messages, expected):
    assert (
        dealapp_tasks._prepare_payload(task, messages, cbox.app.config)
        == expected
    )


@pytest.mark.config(
    CHATTERBOX_TO_DEALAPP_FIELD_MAP={
        'field1': 'field1',
        'field2': 'field3',
        'field4.inner': 'field4',
        'field5': 'field5.inner',
        'field6.inner.inner2': 'field6.inner3',
    },
)
@pytest.mark.parametrize(
    'task,expected',
    [
        ({}, {}),
        ({'invalid_field': 'value'}, {}),
        (
            {
                'field1': 'value1',
                'field2': 'value2',
                'field4': {'inner': 'value4'},
                'field5': 'value5',
                'field6': {'inner': {'inner2': 'value6'}},
                'invalid_field': 'value7',
            },
            {
                'field1': 'value1',
                'field3': 'value2',
                'field4': 'value4',
                'field5.inner': 'value5',
                'field6.inner3': 'value6',
            },
        ),
    ],
)
def test_map_to_dealapp(cbox, task, expected):
    assert (
        dealapp_tasks._map_to_dealapp(
            task, cbox.app.config.CHATTERBOX_TO_DEALAPP_FIELD_MAP,
        )
        == expected
    )


@pytest.mark.parametrize(
    'task,expire,chat_direction,communication_type',
    [
        (
            {'_id': bson.ObjectId('000000000000000000000000')},
            None,
            dealapp_tasks.DEALAPP_CHAT_DIRECTION_INCOMING,
            dealapp_tasks.DEALAPP_COMMUNICATION_TYPE_CHAT,
        ),
        (
            {'_id': TASK_ID, 'created': NOW - datetime.timedelta(minutes=10)},
            None,
            dealapp_tasks.DEALAPP_CHAT_DIRECTION_INCOMING,
            dealapp_tasks.DEALAPP_COMMUNICATION_TYPE_CHAT,
        ),
        (
            {
                '_id': TASK_ID,
                'created': NOW - datetime.timedelta(minutes=10),
                'full_resolve': 600,
            },
            NOW,
            dealapp_tasks.DEALAPP_CHAT_DIRECTION_INCOMING,
            dealapp_tasks.DEALAPP_COMMUNICATION_TYPE_CHAT,
        ),
        (
            {
                '_id': TASK_ID,
                'created': NOW - datetime.timedelta(minutes=10),
                'full_resolve': 600,
                'tags': ['support_init'],
            },
            NOW,
            dealapp_tasks.DEALAPP_CHAT_DIRECTION_OUTCOMING,
            dealapp_tasks.DEALAPP_COMMUNICATION_TYPE_CHAT,
        ),
        (
            {
                '_id': bson.ObjectId('000000000000000000000000'),
                'chat_type': 'startrack',
            },
            None,
            dealapp_tasks.DEALAPP_CHAT_DIRECTION_INCOMING,
            dealapp_tasks.DEALAPP_COMMUNICATION_TYPE_TICKET,
        ),
    ],
)
def test_get_extra_fields(task, expire, chat_direction, communication_type):
    result = dealapp_tasks._get_extra_fields(task)
    assert result.get(dealapp_tasks.DEALAPP_EXPIRE) == expire
    assert result.get(dealapp_tasks.DEALAPP_CHAT_DIRECTION) == chat_direction
    assert (
        result.get(dealapp_tasks.DEALAPP_COMMUNICATION_TYPE)
        == communication_type
    )


@pytest.mark.parametrize(
    'task_messages,task,client_id,expected',
    [
        ({}, {'_id': TASK_ID}, None, {'communication_parts': []}),
        (
            {'messages': []},
            {'_id': TASK_ID},
            None,
            {'communication_parts': []},
        ),
        (
            {
                'messages': [
                    {
                        '_id': bson.ObjectId('000000000000000000000000'),
                        'timestamp': NOW,
                        'message': 'Привет!',
                        'author_id': 'user007',
                        'author': 'user',
                    },
                    {
                        '_id': bson.ObjectId('000000000000000000000001'),
                        'timestamp': NOW + datetime.timedelta(seconds=1),
                        'message': 'Здравствуй!',
                        'author_id': 'support_vasya',
                        'author': 'support',
                    },
                ],
            },
            {'_id': TASK_ID},
            None,
            {
                'communication_parts': [
                    {
                        'communication_part_id': '000000000000000000000000',
                        'created_at': '2018-05-07T12:35:00+0000',
                        'body': 'Привет!',
                        'author': {'id': 'user007', 'type': 'client'},
                    },
                    {
                        'communication_part_id': '000000000000000000000001',
                        'created_at': '2018-05-07T12:35:01+0000',
                        'body': 'Здравствуй!',
                        'author': {'id': 'support_vasya', 'type': 'operator'},
                    },
                ],
            },
        ),
        (
            {
                'messages': [
                    {
                        '_id': bson.ObjectId('000000000000000000000000'),
                        'timestamp': datetime.datetime(2018, 5, 7, 12, 35, 5),
                        'message': 'Привет!',
                        'author_id': 'user007',
                        'author': 'user',
                    },
                    {
                        '_id': bson.ObjectId('000000000000000000000001'),
                        'timestamp': datetime.datetime(2018, 5, 7, 12, 35, 15),
                        'message': 'Здравствуй!',
                        'author_id': 'support_vasya',
                        'author': 'support',
                    },
                ],
            },
            {
                '_id': TASK_ID,
                'inner_comments': [
                    {
                        'login': 'superuser',
                        'comment': 'Task created',
                        'created': datetime.datetime(2018, 5, 7, 12, 35, 6),
                    },
                    {
                        'login': 'support_vasya',
                        'comment': 'Good request',
                        'created': datetime.datetime(2018, 5, 7, 12, 35, 10),
                    },
                ],
            },
            None,
            {
                'communication_parts': [
                    {
                        'communication_part_id': '000000000000000000000000',
                        'created_at': '2018-05-07T12:35:05+0000',
                        'body': 'Привет!',
                        'author': {'id': 'user007', 'type': 'client'},
                    },
                    {
                        'communication_part_id': (
                            '5b2cae5cb2682a976914c2a2_internal_0'
                        ),
                        'created_at': '2018-05-07T12:35:06+0000',
                        'body': 'Task created',
                        'author': {'id': 'superuser', 'type': 'operator'},
                    },
                    {
                        'communication_part_id': (
                            '5b2cae5cb2682a976914c2a2_internal_1'
                        ),
                        'created_at': '2018-05-07T12:35:10+0000',
                        'body': 'Good request',
                        'author': {'id': 'support_vasya', 'type': 'operator'},
                    },
                    {
                        'communication_part_id': '000000000000000000000001',
                        'created_at': '2018-05-07T12:35:15+0000',
                        'body': 'Здравствуй!',
                        'author': {'id': 'support_vasya', 'type': 'operator'},
                    },
                ],
            },
        ),
        (
            {
                'messages': [
                    {
                        'id': '0',
                        'sender': {'id': '1130000029893851', 'role': 'client'},
                        'text': 'test startrack',
                        'metadata': {
                            'created': '2018-05-07T12:36:10.123+0000',
                            'updated': '2018-05-07T12:36:11.456+0000',
                            'ticket_subject': 'еда_тест 9',
                        },
                    },
                    {
                        'id': '691706162',
                        'sender': {'id': 'superuser', 'role': 'support'},
                        'text': 'test',
                        'metadata': {'created': '2018-05-07T12:36:15.12+0000'},
                    },
                ],
            },
            {
                '_id': TASK_ID,
                'inner_comments': [
                    {
                        'login': 'superuser',
                        'comment': 'Task created',
                        'created': datetime.datetime(2018, 5, 7, 12, 35, 6),
                    },
                    {
                        'login': 'support_vasya',
                        'comment': 'Good request',
                        'created': datetime.datetime(2018, 5, 7, 12, 35, 10),
                    },
                ],
                'chat_type': 'startrack',
            },
            None,
            {
                'communication_parts': [
                    {
                        'author': {'id': 'superuser', 'type': 'operator'},
                        'body': 'Task created',
                        'communication_part_id': (
                            '5b2cae5cb2682a976914c2a2_internal_0'
                        ),
                        'created_at': '2018-05-07T12:35:06+0000',
                    },
                    {
                        'author': {'id': 'support_vasya', 'type': 'operator'},
                        'body': 'Good request',
                        'communication_part_id': (
                            '5b2cae5cb2682a976914c2a2_internal_1'
                        ),
                        'created_at': '2018-05-07T12:35:10+0000',
                    },
                    {
                        'author': {'id': '1130000029893851', 'type': 'client'},
                        'body': 'test startrack',
                        'communication_part_id': '0',
                        'created_at': '2018-05-07T12:36:10.123+0000',
                        'updated_at': '2018-05-07T12:36:11.456+0000',
                    },
                    {
                        'author': {'id': 'superuser', 'type': 'operator'},
                        'body': 'test',
                        'communication_part_id': '691706162',
                        'created_at': '2018-05-07T12:36:15.12+0000',
                    },
                ],
            },
        ),
        (
            {
                'messages': [
                    {
                        '_id': bson.ObjectId('000000000000000000000000'),
                        'timestamp': NOW,
                        'message': 'Привет!',
                        'author_id': 'user008',
                    },
                    {
                        '_id': bson.ObjectId('000000000000000000000001'),
                        'timestamp': NOW + datetime.timedelta(seconds=1),
                        'message': 'Здравствуй!',
                        'author_id': 'support_vasya',
                        'author': 'support',
                    },
                ],
            },
            {'_id': TASK_ID},
            'user008',
            {
                'communication_parts': [
                    {
                        'communication_part_id': '000000000000000000000000',
                        'created_at': '2018-05-07T12:35:00+0000',
                        'body': 'Привет!',
                        'author': {'id': 'user008', 'type': 'client'},
                    },
                    {
                        'communication_part_id': '000000000000000000000001',
                        'created_at': '2018-05-07T12:35:01+0000',
                        'body': 'Здравствуй!',
                        'author': {'id': 'support_vasya', 'type': 'operator'},
                    },
                ],
            },
        ),
        (
            {
                'messages': [
                    {
                        '_id': bson.ObjectId('000000000000000000000000'),
                        'timestamp': NOW,
                        'message': 'Привет!',
                        'author_id': 'user008',
                    },
                    {
                        '_id': bson.ObjectId('000000000000000000000001'),
                        'timestamp': NOW + datetime.timedelta(seconds=1),
                        'message': 'Здравствуй!',
                        'author_id': 'support_vasya',
                        'author': 'support',
                    },
                ],
                'user_id': 'user008',
            },
            {'_id': TASK_ID},
            None,
            {
                'communication_parts': [
                    {
                        'communication_part_id': '000000000000000000000000',
                        'created_at': '2018-05-07T12:35:00+0000',
                        'body': 'Привет!',
                        'author': {'id': 'user008', 'type': 'client'},
                    },
                    {
                        'communication_part_id': '000000000000000000000001',
                        'created_at': '2018-05-07T12:35:01+0000',
                        'body': 'Здравствуй!',
                        'author': {'id': 'support_vasya', 'type': 'operator'},
                    },
                ],
            },
        ),
        (
            {
                'messages': [
                    {
                        '_id': bson.ObjectId('000000000000000000000000'),
                        'timestamp': NOW,
                        'message': 'Здравствуйте! В пакете с едой было это:',
                        'author_id': 'user009',
                        'author': 'user',
                        'metadata': {
                            'attachments': [
                                {
                                    'name': 'image_1.png',
                                    'link': 'link_to_image_1',
                                    'link_preview': 'link_to_preview_image_1',
                                },
                                {
                                    'name': 'image_2.png',
                                    'link': 'link_to_image_2',
                                },
                            ],
                        },
                    },
                    {
                        '_id': bson.ObjectId('000000000000000000000001'),
                        'timestamp': NOW + datetime.timedelta(seconds=1),
                        'message': (
                            'Здравствуйте! А Вы точно это не заказывали?'
                        ),
                        'author_id': 'support_vasya',
                        'author': 'support',
                    },
                    {
                        '_id': bson.ObjectId('000000000000000000000002'),
                        'timestamp': NOW + datetime.timedelta(seconds=2),
                        'author_id': 'user009',
                        'author': 'user',
                        'metadata': {
                            'attachments': [
                                {
                                    'name': 'are_you_kidding_me.gif',
                                    'link': 'link_to_gif',
                                    'link_preview': 'link_to_preview_gif',
                                },
                            ],
                        },
                    },
                ],
            },
            {'_id': TASK_ID},
            None,
            {
                'communication_parts': [
                    {
                        'communication_part_id': '000000000000000000000000',
                        'created_at': '2018-05-07T12:35:00+0000',
                        'body': (
                            'Здравствуйте! В пакете с едой было это:\n'
                            '<a href="link_to_image_1" target="_blank">'
                            '<img src="link_to_preview_image_1" '
                            'alt="image_1.png"></a>\n'
                            '<a href="link_to_image_2" target="_blank">'
                            'image_2.png</a>'
                        ),
                        'content_type': 'text/html',
                        'author': {'id': 'user009', 'type': 'client'},
                    },
                    {
                        'communication_part_id': '000000000000000000000001',
                        'created_at': '2018-05-07T12:35:01+0000',
                        'body': 'Здравствуйте! А Вы точно это не заказывали?',
                        'author': {'id': 'support_vasya', 'type': 'operator'},
                    },
                    {
                        'communication_part_id': '000000000000000000000002',
                        'created_at': '2018-05-07T12:35:02+0000',
                        'body': (
                            '<a href="link_to_gif" target="_blank">'
                            '<img src="link_to_preview_gif" '
                            'alt="are_you_kidding_me.gif"></a>'
                        ),
                        'content_type': 'text/html',
                        'author': {'id': 'user009', 'type': 'client'},
                    },
                ],
            },
        ),
    ],
)
def test_prepare_message(task_messages, task, client_id, expected):
    assert (
        dealapp_tasks._prepare_message(
            task_messages, task, client_id=client_id,
        )
        == expected
    )


@pytest.mark.parametrize(
    'task,expected',
    [
        ({}, {}),
        ({'metadata': {'csat_value': 'good'}}, {'custom_fields.csat1': 4}),
        (
            {
                'metadata': {
                    'csat_values': {
                        'questions': [
                            {
                                'id': 'support_quality',
                                'value': {
                                    'id': 'horrible',
                                    'comment': 'test1',
                                },
                            },
                            {'dummy_field': 'dummy_value'},
                            {
                                'id': 'response_quality',
                                'value': {'id': 'horrible'},
                            },
                            {
                                'id': 'leave_note',
                                'value': {'comment': 'test2'},
                            },
                        ],
                    },
                },
            },
            {
                'custom_fields.csat1': 1,
                'custom_fields.comment_client_csat1': 'test1',
                'custom_fields.csat2': 1,
                'custom_fields.comment_client_csat3': 'test2',
            },
        ),
    ],
)
def test_prepare_csat(task, expected):
    csat_mapper = {'horrible': 1, 'good': 4, 'amazing': 5}
    assert dealapp_tasks._prepare_csat(task, csat_mapper) == expected
