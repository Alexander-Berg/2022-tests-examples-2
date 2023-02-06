# pylint: disable=too-many-lines
import datetime
import functools

import pytest
import pytz


@pytest.mark.config(
    CHATTERBOX_LINES={
        'eda_online': {'projects': ['eats'], 'mode': 'online'},
        'yet_another_eda_online': {'projects': ['eats'], 'mode': 'online'},
        'eda_offline': {'projects': ['eats']},
        'eda_line_not_in_config': {'projects': ['eats']},
        'not_eda': {'projects': ['taxi']},
    },
    SUPPORT_METRICS_EATS_SUPPORT_TRACKED_LINES=[
        'eda_online',
        'eda_offline',
        'yet_another_eda_online',
    ],
)
@pytest.mark.parametrize(
    'data, expected_stats',
    [
        ([], []),
        (
            {
                'events': [
                    {
                        'id': 'test_forward_out_online',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'forward',
                            'line': 'eda_online',
                            'new_line': 'not_eda',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'forward_out',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
            ],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_no_login',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': '',
                            'action': 'forward',
                            'line': 'eda_online',
                            'new_line': 'not_eda',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_forward_out_online',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'forward',
                            'line': 'not_eda',
                            'new_line': 'eda_online',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'forward_in',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
            ],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_close_in_offline',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'close',
                            'line': 'eda_offline',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'close',
                        'line': 'eda_offline',
                        'line_mode': 'offline',
                        'executor': 'superuser',
                    },
                },
            ],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_not_eats_line',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'close',
                            'line': 'other',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_line_not_in_config',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'close',
                            'line': 'eda_line_not_in_config',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_operator_as_executor',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'leshka',
                            'action': 'close',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'close',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'operator',
                    },
                },
            ],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_two_create_in_diff_ts_1',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'create',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                    {
                        'id': 'test_two_create_in_diff_ts_2',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:03.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'create',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'create',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, 3, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'create',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
            ],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_two_create_in_diff_lines_1',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'create',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                    {
                        'id': 'test_two_create_in_diff_ts_2',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'create',
                            'line': 'yet_another_eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'create',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'create',
                        'line': 'yet_another_eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
            ],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_two_assign_in_same_ts_1',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'assign',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                    {
                        'id': 'test_two_assign_in_same_ts_2',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'assign',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [
                {
                    'value': 2.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'assign',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
            ],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_diff_actions_in_same_ts_1',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'reopen',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                    {
                        'id': 'test_diff_actions_in_same_ts_2',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'offer',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                            'ready_to_send_at': '2019-05-04T12:22:00.0+00',
                        },
                    },
                ],
            },
            [
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'offer',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'reopen',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
            ],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_diff_lines_with_same_action_1',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'reopen',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                    {
                        'id': 'test_diff_lines_with_same_action_2',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'reopen',
                            'line': 'eda_offline',
                            'new_line': '',
                            'in_addition': True,
                            'ready_to_send_at': '2019-05-04T12:22:00.0+00',
                        },
                    },
                ],
            },
            [
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'reopen',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'reopen',
                        'line': 'eda_offline',
                        'line_mode': 'offline',
                        'executor': 'superuser',
                    },
                },
            ],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_duplicate_protection',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:19:01.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'create',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [],
        ),
        (
            {
                'events': [
                    {
                        'id': 'test_complex_1',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'assign',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                    {
                        'id': 'test_complex_2',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'offer',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                    {
                        'id': 'test_complex_3',
                        'type': 'chatterbox_action',
                        'created': '2019-05-04T12:20:00.0+00',
                        'payload': {
                            'task_id': 'test_id',
                            'login': 'superuser',
                            'action': 'assign',
                            'line': 'eda_online',
                            'new_line': '',
                            'in_addition': True,
                        },
                    },
                ],
            },
            [
                {
                    'value': 2.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'assign',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
                {
                    'value': 1.0,
                    'kind': 'DGAUGE',
                    'timestamp': datetime.datetime(
                        2019, 5, 4, 12, 20, tzinfo=pytz.utc,
                    ),
                    'labels': {
                        'sensor': 'eats_support.chatterbox.actions',
                        'action_type': 'offer',
                        'line': 'eda_online',
                        'line_mode': 'online',
                        'executor': 'superuser',
                    },
                },
            ],
        ),
    ],
)
async def test_bulk(
        web_app_client,
        web_app,
        get_stats_by_label_values,
        data,
        expected_stats,
):
    await web_app_client.post('/v1/bulk_process_event', json=data)

    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'eats_support.chatterbox.actions'},
    )
    _sorted = functools.partial(
        sorted, key=lambda item: item['labels']['action_type'],
    )
    assert _sorted(stats) == _sorted(expected_stats)
