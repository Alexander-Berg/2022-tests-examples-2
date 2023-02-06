# pylint: disable=too-many-lines
import datetime

import pytest
import pytz


async def _check_chatterbox_events(db, expected_result):
    result = await db.primary_fetch(
        'SELECT * FROM events.chatterbox_events ORDER BY id ASC',
    )
    assert len(result) == len(expected_result)
    for i, record in enumerate(result):
        assert record['id'] == expected_result[i]['id']
        assert record['type'] == expected_result[i]['type']
        assert record.get('task_id') == expected_result[i].get('task_id')
        assert record['created_ts'] == expected_result[i]['created_ts']
        assert record['login'] == expected_result[i]['login']
        assert record['action_type'] == expected_result[i]['action_type']
        assert record['line'] == expected_result[i]['line']
        assert record['new_line'] == expected_result[i]['new_line']
        assert record['in_addition'] == expected_result[i]['in_addition']
        if 'start_timestamp' in expected_result[i]:
            assert record['start_timestamp'] == (
                expected_result[i]['start_timestamp']
            )


async def _check_supporter_events(db, expected_result):
    result = await db.primary_fetch(
        'SELECT * FROM events.supporter_events ORDER BY id ASC',
    )
    assert len(result) == len(expected_result)
    for i, record in enumerate(result):
        assert record['id'] == expected_result[i]['id']
        assert record['type'] == expected_result[i]['type']
        assert record['created_ts'] == expected_result[i]['created_ts']
        assert record['login'] == expected_result[i]['login']
        assert record['in_addition'] == expected_result[i]['in_addition']
        assert record['status'] == expected_result[i]['status']
        assert record['finish_timestamp'] == (
            expected_result[i]['finish_timestamp']
        )
        assert record['start_timestamp'] == (
            expected_result[i]['start_timestamp']
        )
        assert record['lines'] == expected_result[i]['lines']
        assert record['projects'] == expected_result[i]['projects']


async def _check_chatterbox_lines_backlog(db, expected_result):
    result = await db.primary_fetch(
        'SELECT * FROM events.chatterbox_lines_backlog_events ORDER BY id ASC',
    )
    assert len(result) == len(expected_result)
    for i, record in enumerate(result):
        assert record['id'] == expected_result[i]['id']
        assert record['created_ts'] == expected_result[i]['created_ts']
        assert record['line'] == expected_result[i]['line']
        assert record['status'] == expected_result[i]['status']
        assert record['count'] == expected_result[i]['count']


async def _check_chatterbox_offered_tasks(db, expected_result):
    result = await db.primary_fetch(
        'SELECT * FROM chatterbox_tasks.offered_tasks ORDER BY id ASC',
    )
    assert len(result) == len(expected_result)
    for i, record in enumerate(result):
        assert record['id'] == expected_result[i]['id']
        assert record['login'] == expected_result[i]['login']
        assert record['line'] == expected_result[i]['line']
        assert record['offered_ts'] == expected_result[i]['offered_ts']
        assert record['updated_ts'] == expected_result[i]['updated_ts']


async def _check_ivr_calls_events(db, expected_result):
    result = await db.primary_fetch(
        'SELECT * FROM events.chatterbox_ivr_calls_events ORDER BY id ASC',
    )
    assert len(result) == len(expected_result)
    for i, record in enumerate(result):
        assert record['id'] == expected_result[i]['id']
        assert record['created_ts'] == expected_result[i]['created_ts']
        assert record['line'] == expected_result[i]['line']
        assert record['action_type'] == expected_result[i]['action_type']
        assert (
            record['start_timestamp'] == expected_result[i]['start_timestamp']
        )
        assert (
            record['answered_timestamp']
            == expected_result[i]['answered_timestamp']
        )
        assert (
            record['completed_timestamp']
            == expected_result[i]['completed_timestamp']
        )


@pytest.mark.now('2019-02-04T12:20:00.0')
@pytest.mark.parametrize(
    'data, expected_code, expected_result',
    [
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'chatterbox_action',
                    'created': '2019-02-04T12:20:00.0+0000',
                    'payload': {
                        'task_id': 'test_id',
                        'login': 'superuser',
                        'action': 'create',
                        'line': 'first',
                        'in_addition': False,
                    },
                },
            },
            200,
            [
                {
                    'id': 'test_id',
                    'type': 'chatterbox_action',
                    'task_id': 'test_id',
                    'created_ts': datetime.datetime(
                        2019, 2, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'login': 'superuser',
                    'action_type': 'create',
                    'line': 'first',
                    'new_line': '',
                    'in_addition': False,
                },
            ],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'chatterbox_action',
                    'created': '2019-02-04T12:20:00.0+0000',
                    'payload': {
                        'task_id': 'test_id',
                        'login': 'superuser',
                        'action': 'online_chat_processing',
                        'line': 'first',
                        'in_addition': False,
                        'start_timestamp': '2019-02-04T11:20:00.0+0000',
                    },
                },
            },
            200,
            [
                {
                    'id': 'test_id',
                    'type': 'chatterbox_action',
                    'task_id': 'test_id',
                    'created_ts': datetime.datetime(
                        2019, 2, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'login': 'superuser',
                    'action_type': 'online_chat_processing',
                    'line': 'first',
                    'new_line': '',
                    'in_addition': False,
                    'start_timestamp': datetime.datetime(
                        2019, 2, 4, 11, 20, tzinfo=pytz.utc,
                    ),
                },
            ],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'chatterbox_action',
                    'created': '2019-02-04T12:20:00.0+0000',
                    'payload': {
                        'task_id': 'test_id',
                        'login': 'superuser',
                        'action': 'forward',
                        'line': 'first',
                        'new_line': 'second',
                        'in_addition': True,
                    },
                },
            },
            200,
            [
                {
                    'id': 'test_id',
                    'type': 'chatterbox_action',
                    'task_id': 'test_id',
                    'created_ts': datetime.datetime(
                        2019, 2, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'login': 'superuser',
                    'action_type': 'forward',
                    'line': 'first',
                    'new_line': 'second',
                    'in_addition': True,
                },
            ],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'sip_call',
                    'created': '2019-02-04T12:20:00.0+0000',
                    'payload': {
                        'login': 'superuser',
                        'action': 'success_call',
                        'line': 'first',
                        'start_timestamp': '2019-02-04T11:20:00.0+0000',
                    },
                },
            },
            200,
            [
                {
                    'id': 'test_id',
                    'type': 'sip_call',
                    'created_ts': datetime.datetime(
                        2019, 2, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'login': 'superuser',
                    'action_type': 'success_call',
                    'line': 'first',
                    'new_line': '',
                    'in_addition': False,
                    'start_timestamp': datetime.datetime(
                        2019, 2, 4, 11, 20, tzinfo=pytz.utc,
                    ),
                },
            ],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'supporter_status',
                    'created': '2019-02-04T12:20:00.0+0000',
                    'payload': {
                        'login': 'superuser',
                        'status': 'online',
                        'in_addition': True,
                        'start_timestamp': '2019-02-04T12:20:00.0+0000',
                        'finish_timestamp': '2019-02-04T12:30:00.0+0000',
                        'lines': ['first', 'second'],
                        'projects': ['eats', 'taxi'],
                    },
                },
            },
            200,
            [
                {
                    'id': 'test_id',
                    'type': 'supporter_status',
                    'created_ts': datetime.datetime(
                        2019, 2, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'login': 'superuser',
                    'status': 'online',
                    'in_addition': True,
                    'start_timestamp': datetime.datetime(
                        2019, 2, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'finish_timestamp': datetime.datetime(
                        2019, 2, 4, 12, 30, tzinfo=pytz.utc,
                    ),
                    'lines': ['first', 'second'],
                    'projects': ['eats', 'taxi'],
                },
            ],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'chatterbox_action',
                    'created': '2019-02-04T12:20:00.0+00',
                    'payload': {
                        'task_id': 'test_id',
                        'login': 'superuser',
                        'line': 'first',
                        'in_addition': False,
                    },
                },
            },
            400,
            [],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'chatterbox_action',
                    'created': '2019-02-04T12:20:00.0+00',
                    'payload': {
                        'task_id': 'test_id',
                        'login': 'superuser',
                        'line': 'first',
                        'action': 'close',
                    },
                },
            },
            400,
            [],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'chatterbox_action',
                    'created': '2019-02-04T12:20:00.0+00',
                    'payload': {
                        'task_id': 'test_id',
                        'login': 'superuser',
                        'in_addition': False,
                        'action': 'close',
                    },
                },
            },
            400,
            [],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'chatterbox_action',
                    'created': '2019-02-04T12:20:00.0+00',
                    'payload': {
                        'task_id': 'test_id',
                        'line': 'first',
                        'in_addition': False,
                        'action': 'close',
                    },
                },
            },
            400,
            [],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'chatterbox_action',
                    'created': '2019-02-04T12:20:00.0+00',
                    'payload': {'login': 'superuser', 'line': 'first'},
                },
            },
            400,
            [],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'change_line',
                    'created': '2019-02-04T12:20:00.0+00',
                },
            },
            400,
            [],
        ),
        (
            {'event': {'id': 'test_id', 'type': 'change_line', 'payload': {}}},
            400,
            [],
        ),
        (
            {
                'event': {
                    'type': 'change_line',
                    'created': '2019-02-04T12:20:00.0+00',
                    'payload': {},
                },
            },
            400,
            [],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'change_line',
                    'payload': {},
                    'created': '2019-02-04T12:20:00.0+00',
                },
                'option': 'value',
            },
            400,
            [],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'supporter_status',
                    'created': '2019-02-04T12:20:00.0+0000',
                    'payload': {
                        'login': 'superuser',
                        'status': 'online',
                        'in_addition': True,
                        'start_timestamp': '2019-02-04T12:20:00.0+0000',
                    },
                },
            },
            400,
            [],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'supporter_status',
                    'created': '2019-02-04T12:20:00.0+0000',
                    'payload': {
                        'login': 'superuser',
                        'status': 'online',
                        'in_addition': True,
                        'finish_timestamp': '2019-02-04T12:20:00.0+0000',
                    },
                },
            },
            400,
            [],
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'supporter_status',
                    'created': '2019-02-04T12:20:00.0+0000',
                    'payload': {
                        'login': 'superuser',
                        'in_addition': True,
                        'start_timestamp': '2019-02-04T12:20:00.0+0000',
                        'finish_timestamp': '2019-02-04T12:20:00.0+0000',
                    },
                },
            },
            400,
            [],
        ),
    ],
)
async def test_event(
        web_app_client, web_context, data, expected_code, expected_result,
):
    response = await web_app_client.post('/v1/process_event', json=data)
    assert response.status == expected_code
    if expected_code == 200:
        content = await response.json()
        assert content == {}
        db = web_context.postgresql.support_metrics[0]
        if data['event']['type'] == 'chatterbox_action':
            await _check_chatterbox_events(db, expected_result)
        elif data['event']['type'] == 'supporter_status':
            await _check_supporter_events(db, expected_result)


@pytest.mark.now('2019-02-04T12:20:00.0')
@pytest.mark.parametrize(
    'data, expected_code, expected_result',
    [
        (
            {
                'events': [
                    {
                        'id': 'test_id',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'forward',
                            'line': 'first',
                            'new_line': 'second',
                            'in_addition': True,
                        },
                    },
                    {
                        'id': 'test_id_1',
                        'type': 'new_task',
                        'created': '2019-06-04T13:20:00.0+00',
                        'payload': {'old_line': 'first', 'new_line': 'second'},
                    },
                    {
                        'id': 'test_id_supporter',
                        'type': 'supporter_status',
                        'created': '2019-02-04T12:10:00.0+0000',
                        'payload': {
                            'login': 'superuser',
                            'status': 'online',
                            'in_addition': False,
                            'start_timestamp': '2019-02-04T12:15:00.0+0000',
                            'finish_timestamp': '2019-02-04T12:25:00.0+0000',
                            'lines': ['first'],
                            'projects': ['taxi'],
                        },
                    },
                    {
                        'id': 'test_id_supporter',
                        'type': 'supporter_status',
                        'created': '2019-02-04T12:20:00.0+0000',
                        'payload': {
                            'login': 'superuser',
                            'status': 'online',
                            'in_addition': True,
                            'start_timestamp': '2019-02-04T12:20:00.0+0000',
                            'finish_timestamp': '2019-02-04T12:30:00.0+0000',
                            'lines': ['second'],
                            'projects': ['eats'],
                        },
                    },
                    {
                        'id': 'test_id_2',
                        'type': 'chatterbox_action',
                        'created': '2019-06-04T14:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'login',
                            'action': 'create',
                            'line': 'corp',
                            'in_addition': False,
                        },
                    },
                ],
            },
            200,
            {
                'chatterbox_events': [
                    {
                        'id': 'test_id',
                        'type': 'chatterbox_action',
                        'task_id': 'test_id',
                        'created_ts': datetime.datetime(
                            2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                        ),
                        'login': 'superuser',
                        'action_type': 'forward',
                        'line': 'first',
                        'new_line': 'second',
                        'in_addition': True,
                    },
                    {
                        'id': 'test_id_2',
                        'task_id': 'test_id',
                        'type': 'chatterbox_action',
                        'created_ts': datetime.datetime(
                            2019, 6, 4, 14, 20, tzinfo=pytz.utc,
                        ),
                        'login': 'login',
                        'action_type': 'create',
                        'line': 'corp',
                        'in_addition': False,
                        'new_line': '',
                    },
                ],
                'supporter_events': [
                    {
                        'id': 'test_id_supporter',
                        'type': 'supporter_status',
                        'created_ts': datetime.datetime(
                            2019, 2, 4, 12, 20, tzinfo=pytz.utc,
                        ),
                        'login': 'superuser',
                        'status': 'online',
                        'in_addition': True,
                        'start_timestamp': datetime.datetime(
                            2019, 2, 4, 12, 20, tzinfo=pytz.utc,
                        ),
                        'finish_timestamp': datetime.datetime(
                            2019, 2, 4, 12, 30, tzinfo=pytz.utc,
                        ),
                        'lines': ['second'],
                        'projects': ['eats'],
                    },
                ],
            },
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_id',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'forward',
                            'line': 'first',
                            'new_line': 'second',
                            'in_addition': True,
                        },
                    },
                    {
                        'id': 'test_id',
                        'type': 'chatterbox_action',
                        'created': '2019-06-04T13:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'forward',
                            'line': 'second',
                            'new_line': 'corp',
                            'in_addition': True,
                        },
                    },
                ],
            },
            200,
            {
                'chatterbox_events': [
                    {
                        'id': 'test_id',
                        'type': 'chatterbox_action',
                        'task_id': 'test_id',
                        'created_ts': datetime.datetime(
                            2019, 6, 4, 13, 20, tzinfo=pytz.utc,
                        ),
                        'login': 'superuser',
                        'action_type': 'forward',
                        'line': 'second',
                        'new_line': 'corp',
                        'in_addition': True,
                    },
                ],
                'supporter_events': [],
            },
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_id',
                        'type': 'sip_call',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'login': 'superuser',
                            'action': 'success_call',
                            'line': 'first',
                            'start_timestamp': '2019-05-04T12:19:00.0+00',
                        },
                    },
                    {
                        'id': 'next_test_id',
                        'type': 'sip_call',
                        'created': '2019-06-04T13:20:00.0+00',
                        'payload': {
                            'login': 'superuser',
                            'action': 'failed_call',
                            'line': 'first',
                            'start_timestamp': '2019-06-04T13:20:00.0+00',
                        },
                    },
                ],
            },
            200,
            {
                'chatterbox_events': [
                    {
                        'id': 'next_test_id',
                        'type': 'sip_call',
                        'created_ts': datetime.datetime(
                            2019, 6, 4, 13, 20, tzinfo=pytz.utc,
                        ),
                        'login': 'superuser',
                        'action_type': 'failed_call',
                        'line': 'first',
                        'new_line': '',
                        'in_addition': False,
                        'start_timestamp': datetime.datetime(
                            2019, 6, 4, 13, 20, tzinfo=pytz.utc,
                        ),
                    },
                    {
                        'id': 'test_id',
                        'type': 'sip_call',
                        'created_ts': datetime.datetime(
                            2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                        ),
                        'login': 'superuser',
                        'action_type': 'success_call',
                        'line': 'first',
                        'new_line': '',
                        'in_addition': False,
                        'start_timestamp': datetime.datetime(
                            2019, 5, 4, 12, 19, tzinfo=pytz.utc,
                        ),
                    },
                ],
                'supporter_events': [],
            },
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_id',
                        'type': 'sip_call',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'login': 'superuser',
                            'action': 'incoming_call',
                            'line': 'first',
                            'start_timestamp': '2019-05-04T12:19:00.0+00',
                        },
                    },
                    {
                        'id': 'next_test_id',
                        'type': 'sip_call',
                        'created': '2019-06-04T13:20:00.0+00',
                        'payload': {
                            'login': 'superuser',
                            'action': 'failed_call',
                            'line': 'first',
                            'start_timestamp': '2019-06-04T13:20:00.0+00',
                        },
                    },
                ],
            },
            200,
            {
                'chatterbox_events': [
                    {
                        'id': 'next_test_id',
                        'type': 'sip_call',
                        'created_ts': datetime.datetime(
                            2019, 6, 4, 13, 20, tzinfo=pytz.utc,
                        ),
                        'login': 'superuser',
                        'action_type': 'failed_call',
                        'line': 'first',
                        'new_line': '',
                        'in_addition': False,
                        'start_timestamp': datetime.datetime(
                            2019, 6, 4, 13, 20, tzinfo=pytz.utc,
                        ),
                    },
                    {
                        'id': 'test_id',
                        'type': 'sip_call',
                        'created_ts': datetime.datetime(
                            2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                        ),
                        'login': 'superuser',
                        'action_type': 'incoming_call',
                        'line': 'first',
                        'new_line': '',
                        'in_addition': False,
                        'start_timestamp': datetime.datetime(
                            2019, 5, 4, 12, 19, tzinfo=pytz.utc,
                        ),
                    },
                ],
                'supporter_events': [],
            },
        ),
        (
            {
                'event': {
                    'id': 'test_id',
                    'type': 'change_line',
                    'created': '2019-02-04T12:20:00.0+00',
                },
            },
            400,
            None,
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_id',
                        'payload': {},
                        'created': '2019-02-04T12:20:00.0+00',
                    },
                ],
            },
            400,
            None,
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_id',
                        'type': 'change_line',
                        'payload': {},
                        'created': '2019-02-04T12:20:00.0+00',
                    },
                ],
                'option': 'value',
            },
            400,
            None,
        ),
        (
            {
                'events': [
                    {
                        'id': 'first_new_2019-11-13T15:00:00+0300',
                        'type': 'chatterbox_line_backlog',
                        'payload': {},
                        'created': '2019-11-13T12:00:00+00',
                    },
                ],
            },
            400,
            None,
        ),
        (
            {
                'events': [
                    {
                        'id': 'first_new_2019-11-13T15:00:00+0300',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T12:00:00+00',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'new',
                            'count': 10,
                        },
                    },
                ],
            },
            200,
            {
                'chatterbox_events': [],
                'supporter_events': [],
                'chatterbox_lines_backlog_events': [
                    {
                        'id': 'first_new_2019-11-13T15:00:00+0300',
                        'created_ts': datetime.datetime(
                            2019, 11, 13, 12, 00, tzinfo=pytz.utc,
                        ),
                        'line': 'first',
                        'projects': ['taxi'],
                        'status': 'new',
                        'count': 10,
                    },
                ],
            },
        ),
        (
            {
                'events': [
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_1_ivr_call_0',
                        'payload': {
                            'action': 'missed_call',
                            'answered_timestamp': None,
                            'completed_timestamp': '2018-05-06T01:22:33Z',
                            'line': 'first',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
                    },
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_1_ivr_call_1',
                        'payload': {
                            'action': 'success_call',
                            'answered_timestamp': '2018-05-06T11:22:43Z',
                            'completed_timestamp': '2018-05-06T11:23:43Z',
                            'line': 'first',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
                    },
                ],
            },
            200,
            {
                'ivr_calls_events': [
                    {
                        'created_ts': datetime.datetime(
                            2018, 5, 5, 12, 34, 56, tzinfo=pytz.utc,
                        ),
                        'id': 'task_1_ivr_call_0',
                        'action_type': 'missed_call',
                        'answered_timestamp': None,
                        'completed_timestamp': datetime.datetime(
                            2018, 5, 6, 1, 22, 33, tzinfo=pytz.utc,
                        ),
                        'line': 'first',
                        'start_timestamp': datetime.datetime(
                            2018, 5, 5, 12, 34, 56, tzinfo=pytz.utc,
                        ),
                    },
                    {
                        'created_ts': datetime.datetime(
                            2018, 5, 5, 12, 34, 56, tzinfo=pytz.utc,
                        ),
                        'id': 'task_1_ivr_call_1',
                        'action_type': 'success_call',
                        'answered_timestamp': datetime.datetime(
                            2018, 5, 6, 11, 22, 43, tzinfo=pytz.utc,
                        ),
                        'completed_timestamp': datetime.datetime(
                            2018, 5, 6, 11, 23, 43, tzinfo=pytz.utc,
                        ),
                        'line': 'first',
                        'start_timestamp': datetime.datetime(
                            2018, 5, 5, 12, 34, 56, tzinfo=pytz.utc,
                        ),
                    },
                ],
            },
        ),
    ],
)
async def test_bulk(
        web_app_client, web_context, data, expected_code, expected_result,
):
    response = await web_app_client.post('/v1/bulk_process_event', json=data)
    assert response.status == expected_code
    if expected_code == 200:
        content = await response.json()
        assert content == {}
        db = web_context.postgresql.support_metrics[0]
        await _check_chatterbox_events(
            db, expected_result.get('chatterbox_events', []),
        )
        await _check_supporter_events(
            db, expected_result.get('supporter_events', []),
        )
        await _check_chatterbox_lines_backlog(
            db, expected_result.get('chatterbox_lines_backlog_events', []),
        )
        await _check_ivr_calls_events(
            db, expected_result.get('ivr_calls_events', []),
        )


@pytest.mark.pgsql('support_metrics', files=['pg_support_metrics_replace.sql'])
@pytest.mark.parametrize(
    'data, expected_code, expected_result',
    [
        (
            {
                'event': {
                    'id': 'replace_id',
                    'type': 'chatterbox_action',
                    'created': '2019-02-04T12:20:00.0+0000',
                    'payload': {
                        'task_id': 'test_id',
                        'login': 'superuser',
                        'action': 'create',
                        'line': 'first',
                        'in_addition': False,
                    },
                },
            },
            200,
            [
                {
                    'id': 'replace_id',
                    'type': 'chatterbox_action',
                    'task_id': 'replace_id',
                    'created_ts': datetime.datetime(
                        2019, 7, 2, 12, 0, 1, tzinfo=pytz.utc,
                    ),
                    'login': 'superuser',
                    'action_type': 'create',
                    'line': 'second',
                    'new_line': '',
                    'in_addition': False,
                },
            ],
        ),
        (
            {
                'event': {
                    'id': 'replace_id',
                    'type': 'supporter_status',
                    'created': '2019-02-04T12:20:00.0+0000',
                    'payload': {
                        'login': 'superuser',
                        'status': 'online',
                        'in_addition': True,
                        'start_timestamp': '2019-02-04T12:20:00.0+0000',
                        'finish_timestamp': '2019-02-04T12:30:00.0+0000',
                        'lines': ['first'],
                        'projects': ['taxi'],
                    },
                },
            },
            200,
            [
                {
                    'id': 'replace_id',
                    'type': 'supporter_status',
                    'created_ts': datetime.datetime(
                        2019, 2, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'login': 'superuser',
                    'status': 'online',
                    'in_addition': True,
                    'start_timestamp': datetime.datetime(
                        2019, 2, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'finish_timestamp': datetime.datetime(
                        2019, 2, 4, 12, 30, tzinfo=pytz.utc,
                    ),
                    'lines': ['first'],
                    'projects': ['taxi'],
                },
            ],
        ),
    ],
)
async def test_replace_event(
        web_app_client, web_context, data, expected_code, expected_result,
):
    response = await web_app_client.post('/v1/process_event', json=data)
    assert response.status == expected_code
    if expected_code == 200:
        content = await response.json()
        assert content == {}
        db = web_context.postgresql.support_metrics[0]
        if data['event']['type'] == 'chatterbox_action':
            await _check_chatterbox_events(db, expected_result)
        elif data['event']['type'] == 'supporter_status':
            await _check_supporter_events(db, expected_result)


@pytest.mark.now('2021-10-05T00:19:00.0+00')
@pytest.mark.pgsql(
    'support_metrics', files=['pg_support_metrics_offered_tasks.sql'],
)
@pytest.mark.parametrize(
    'data, expected_offered_tasks',
    [
        (
            {
                'events': [
                    {
                        'id': 'test_1_1',
                        'type': 'chatterbox_action',
                        'created': '2021-10-05T00:17:14.0+00',
                        'payload': {
                            'task_id': 'test_1',
                            'login': 'support_2',
                            'action': 'offer',
                            'line': 'first',
                            'in_addition': False,
                            'ready_to_send_at': '2021-10-05T00:17:16.0+00',
                        },
                    },
                    {
                        'id': 'test_1_2',
                        'type': 'chatterbox_action',
                        'created': '2021-10-05T00:18:00.0+00',
                        'payload': {
                            'task_id': 'test_1',
                            'login': 'support_2',
                            'action': 'accept',
                            'line': 'first',
                            'in_addition': False,
                        },
                    },
                    {
                        'id': 'test_2',
                        'type': 'sip_call',
                        'created': '2021-10-05T00:18:37.0+00',
                        'payload': {
                            'login': 'superuser',
                            'action': 'failed_call',
                            'line': 'first',
                            'start_timestamp': '2021-10-05T00:16:34.0+00',
                        },
                    },
                    {
                        'id': 'test_3',
                        'type': 'chatterbox_action',
                        'created': '2021-10-05T00:17:00.0+00',
                        'payload': {
                            'task_id': 'test_3',
                            'login': 'support_1',
                            'action': 'first_answer',
                            'line': 'second',
                            'in_addition': False,
                        },
                    },
                    {
                        'id': 'test_4_1',
                        'type': 'chatterbox_action',
                        'created': '2021-10-05T00:17:00.0+00',
                        'payload': {
                            'task_id': 'test_4',
                            'login': 'superuser',
                            'action': 'ensure_predispatched',
                            'line': 'first',
                            'in_addition': False,
                        },
                    },
                    {
                        'id': 'test_4_2',
                        'type': 'chatterbox_action',
                        'created': '2021-10-05T00:17:01.0+00',
                        'payload': {
                            'task_id': 'test_4',
                            'login': 'support_1',
                            'action': 'offer',
                            'line': 'first',
                            'in_addition': False,
                            'ready_to_send_at': '2021-10-05T00:17:05.0+00',
                        },
                    },
                    {
                        'id': 'test_5',
                        'type': 'chatterbox_action',
                        'created': '2021-10-05T03:18:00.0+03',
                        'payload': {
                            'task_id': 'test_5',
                            'login': 'support_3',
                            'action': 'offer',
                            'line': 'corp',
                            'in_addition': False,
                            'ready_to_send_at': '2021-10-05T03:19:25.0+03',
                        },
                    },
                ],
            },
            [
                {
                    'id': 'test_4',
                    'login': 'support_1',
                    'line': 'first',
                    'waiting_time': 120,
                    'offered_ts': datetime.datetime(
                        2021, 10, 5, 0, 17, 1, tzinfo=datetime.timezone.utc,
                    ),
                    'updated_ts': datetime.datetime(
                        2021, 10, 5, 0, 17, 5, tzinfo=datetime.timezone.utc,
                    ),
                },
                {
                    'id': 'test_5',
                    'login': 'support_3',
                    'line': 'corp',
                    'waiting_time': 60,
                    'offered_ts': datetime.datetime(
                        2021, 10, 5, 0, 18, tzinfo=datetime.timezone.utc,
                    ),
                    'updated_ts': datetime.datetime(
                        2021, 10, 5, 0, 19, 25, tzinfo=datetime.timezone.utc,
                    ),
                },
                {
                    'id': 'test_6',
                    'login': 'support_2',
                    'line': 'vip',
                    'waiting_time': 120,
                    'offered_ts': datetime.datetime(
                        2021, 10, 5, 0, 17, tzinfo=datetime.timezone.utc,
                    ),
                    'updated_ts': datetime.datetime(
                        2021, 10, 5, 0, 18, tzinfo=datetime.timezone.utc,
                    ),
                },
            ],
        ),
    ],
)
async def test_update_offered_tasks(
        web_app_client, web_context, data, expected_offered_tasks,
):
    response = await web_app_client.post('/v1/bulk_process_event', json=data)
    assert response.status == 200
    content = await response.json()
    assert content == {}
    db = web_context.postgresql.support_metrics[0]
    await _check_chatterbox_offered_tasks(db, expected_offered_tasks)
