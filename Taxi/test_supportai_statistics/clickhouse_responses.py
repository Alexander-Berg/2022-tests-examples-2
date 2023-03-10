from typing import List


def get_separate_calls(limit: int, offset: int):
    data = [
        {
            'call_id': '2199',
            'user_phone_number': '+79166914539',
            'service_phone_number': '+74950852266',
            'initiated_at': '2022-05-30 16:57:42',
            'started_at': None,
            'duration': 0,
            'attempts_taken': 1,
            'status': 'user_busy',
        },
        {
            'call_id': '2200',
            'user_phone_number': '+79166914539',
            'service_phone_number': '+74950852266',
            'initiated_at': '2022-05-30 16:57:43',
            'started_at': '2022-05-30 16:57:46',
            'duration': 22,
            'attempts_taken': 2,
            'status': 'error',
        },
        {
            'call_id': '2201',
            'user_phone_number': '+79166914539',
            'service_phone_number': None,
            'initiated_at': '2022-05-30 16:57:44',
            'started_at': None,
            'duration': 0,
            'attempts_taken': 1,
            'status': 'no_answer',
        },
        {
            'call_id': '2202',
            'user_phone_number': '+79166914539',
            'service_phone_number': '+74950852266',
            'initiated_at': '2022-05-30 16:57:45',
            'started_at': '2022-05-30 16:57:50',
            'duration': 50,
            'attempts_taken': 1,
            'status': 'ended',
        },
    ]
    return {
        'meta': [
            {'name': 'call_id', 'type': 'String'},
            {'name': 'user_phone_number', 'type': 'String'},
            {'name': 'service_phone_number', 'type': 'Nullable(String)'},
            {'name': 'initiated_at', 'type': 'DateTime(\'Europe/Moscow\')'},
            {
                'name': 'started_at',
                'type': 'Nullable(DateTime(\'Europe/Moscow\'))',
            },
            {'name': 'duration', 'type': 'UInt16'},
            {'name': 'attempts_taken', 'type': 'UInt8'},
            {
                'name': 'status',
                'type': 'Enum8(\'no_answer\' = 1, \'user_busy\' = 2, \'hangup\' = 3, \'ended\' = 4, \'forwarded\' = 5, \'error\' = 6)',  # noqa
            },
        ],
        'data': data[offset : offset + limit],
        'rows': 3,
        'rows_before_limit_at_least': 3,
        'statistics': {
            'elapsed': 0.00041986,
            'rows_read': 12,
            'bytes_read': 1380,
        },
    }


def _get_calls_grouped_by_batch_id():
    return {
        'meta': [
            {'name': 'title', 'type': 'Nullable(String)'},
            {'name': 'start_at', 'type': 'DateTime(\'Europe/Moscow\')'},
            {'name': 'total_seconds', 'type': 'UInt64'},
            {'name': 'calls', 'type': 'UInt64'},
            {'name': 'call_attempts', 'type': 'UInt64'},
            {'name': 'connected_first_attempt', 'type': 'UInt64'},
            {'name': 'connected_second_attempt', 'type': 'UInt64'},
            {'name': 'ended_count', 'type': 'UInt64'},
            {'name': 'forwarded_count', 'type': 'UInt64'},
            {'name': 'no_answer_count', 'type': 'UInt64'},
            {'name': 'user_busy_count', 'type': 'UInt64'},
            {'name': 'hangup_count', 'type': 'UInt64'},
            {'name': 'error_count', 'type': 'UInt64'},
        ],
        'data': [
            {
                'title': '3462',
                'start_at': '2022-05-30 12:32:25',
                'total_seconds': '0',
                'calls': '1',
                'call_attempts': '1',
                'connected_first_attempt': '0',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '0',
                'hangup_count': '0',
                'error_count': '1',
            },
            {
                'title': '3463',
                'start_at': '2022-05-30 16:57:42',
                'total_seconds': '0',
                'calls': '3',
                'call_attempts': '3',
                'connected_first_attempt': '0',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '3',
                'hangup_count': '0',
                'error_count': '0',
            },
            {
                'title': '3464',
                'start_at': '2022-05-30 16:59:29',
                'total_seconds': '22',
                'calls': '1',
                'call_attempts': '1',
                'connected_first_attempt': '1',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '0',
                'hangup_count': '1',
                'error_count': '0',
            },
            {
                'title': '3467',
                'start_at': '2022-05-30 18:23:42',
                'total_seconds': '20',
                'calls': '1',
                'call_attempts': '1',
                'connected_first_attempt': '1',
                'connected_second_attempt': '0',
                'ended_count': '1',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '0',
                'hangup_count': '0',
                'error_count': '0',
            },
            {
                'title': '3468',
                'start_at': '2022-05-30 18:29:29',
                'total_seconds': '10',
                'calls': '1',
                'call_attempts': '2',
                'connected_first_attempt': '0',
                'connected_second_attempt': '1',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '1',
                'hangup_count': '1',
                'error_count': '0',
            },
            {
                'title': '3469',
                'start_at': '2022-05-30 18:31:36',
                'total_seconds': '0',
                'calls': '1',
                'call_attempts': '1',
                'connected_first_attempt': '0',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '1',
                'hangup_count': '0',
                'error_count': '0',
            },
            {
                'title': '3470',
                'start_at': '2022-05-30 18:31:53',
                'total_seconds': '10',
                'calls': '1',
                'call_attempts': '3',
                'connected_first_attempt': '0',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '1',
                'user_busy_count': '1',
                'hangup_count': '1',
                'error_count': '0',
            },
        ],
        'rows': 7,
        'statistics': {
            'elapsed': 0.000397258,
            'rows_read': 12,
            'bytes_read': 828,
        },
    }


def _get_calls_grouped_by_hour():
    return {
        'meta': [
            {'name': 'title', 'type': 'String'},
            {'name': 'start_at', 'type': 'DateTime(\'Europe/Moscow\')'},
            {'name': 'total_seconds', 'type': 'UInt64'},
            {'name': 'calls', 'type': 'UInt64'},
            {'name': 'call_attempts', 'type': 'UInt64'},
            {'name': 'connected_first_attempt', 'type': 'UInt64'},
            {'name': 'connected_second_attempt', 'type': 'UInt64'},
            {'name': 'ended_count', 'type': 'UInt64'},
            {'name': 'forwarded_count', 'type': 'UInt64'},
            {'name': 'no_answer_count', 'type': 'UInt64'},
            {'name': 'user_busy_count', 'type': 'UInt64'},
            {'name': 'hangup_count', 'type': 'UInt64'},
            {'name': 'error_count', 'type': 'UInt64'},
        ],
        'data': [
            {
                'title': '2022-05-30 12:00:00',
                'start_at': '2022-05-30 12:32:25',
                'total_seconds': '0',
                'calls': '1',
                'call_attempts': '1',
                'connected_first_attempt': '0',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '0',
                'hangup_count': '0',
                'error_count': '1',
            },
            {
                'title': '2022-05-30 16:00:00',
                'start_at': '2022-05-30 16:57:42',
                'total_seconds': '22',
                'calls': '4',
                'call_attempts': '4',
                'connected_first_attempt': '1',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '3',
                'hangup_count': '1',
                'error_count': '0',
            },
            {
                'title': '2022-05-30 18:00:00',
                'start_at': '2022-05-30 18:23:42',
                'total_seconds': '40',
                'calls': '4',
                'call_attempts': '7',
                'connected_first_attempt': '1',
                'connected_second_attempt': '1',
                'ended_count': '1',
                'forwarded_count': '0',
                'no_answer_count': '1',
                'user_busy_count': '3',
                'hangup_count': '2',
                'error_count': '0',
            },
            {
                'title': '2022-05-31 11:00:00',
                'start_at': '2022-05-31 11:49:05',
                'total_seconds': '4',
                'calls': '1',
                'call_attempts': '1',
                'connected_first_attempt': '1',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '0',
                'hangup_count': '1',
                'error_count': '0',
            },
        ],
        'rows': 4,
        'statistics': {
            'elapsed': 0.000767717,
            'rows_read': 13,
            'bytes_read': 714,
        },
    }


def _get_call_grouped_by_month():
    return {
        'meta': [
            {'name': 'title', 'type': 'String'},
            {'name': 'start_at', 'type': 'DateTime(\'Europe/Moscow\')'},
            {'name': 'total_seconds', 'type': 'UInt64'},
            {'name': 'calls', 'type': 'UInt64'},
            {'name': 'call_attempts', 'type': 'UInt64'},
            {'name': 'connected_first_attempt', 'type': 'UInt64'},
            {'name': 'connected_second_attempt', 'type': 'UInt64'},
            {'name': 'ended_count', 'type': 'UInt64'},
            {'name': 'forwarded_count', 'type': 'UInt64'},
            {'name': 'no_answer_count', 'type': 'UInt64'},
            {'name': 'user_busy_count', 'type': 'UInt64'},
            {'name': 'hangup_count', 'type': 'UInt64'},
            {'name': 'error_count', 'type': 'UInt64'},
        ],
        'data': [
            {
                'title': '2022-05-01',
                'start_at': '2022-05-30 12:32:25',
                'total_seconds': '66',
                'calls': '10',
                'call_attempts': '13',
                'connected_first_attempt': '3',
                'connected_second_attempt': '1',
                'ended_count': '1',
                'forwarded_count': '0',
                'no_answer_count': '1',
                'user_busy_count': '6',
                'hangup_count': '4',
                'error_count': '1',
            },
        ],
        'rows': 1,
        'statistics': {
            'elapsed': 0.00106017,
            'rows_read': 13,
            'bytes_read': 714,
        },
    }


def _get_calls_batches_by_hour():
    return {
        'meta': [
            {'name': 'title', 'type': 'DateTime(\'Europe/Moscow\')'},
            {'name': 'title', 'type': 'Nullable(String)'},
            {'name': 'start_at', 'type': 'DateTime(\'Europe/Moscow\')'},
            {'name': 'total_seconds', 'type': 'UInt64'},
            {'name': 'calls', 'type': 'UInt64'},
            {'name': 'call_attempts', 'type': 'UInt64'},
            {'name': 'connected_first_attempt', 'type': 'UInt64'},
            {'name': 'connected_second_attempt', 'type': 'UInt64'},
            {'name': 'ended_count', 'type': 'UInt64'},
            {'name': 'forwarded_count', 'type': 'UInt64'},
            {'name': 'no_answer_count', 'type': 'UInt64'},
            {'name': 'user_busy_count', 'type': 'UInt64'},
            {'name': 'hangup_count', 'type': 'UInt64'},
            {'name': 'error_count', 'type': 'UInt64'},
        ],
        'data': [
            {
                'period': '2022-05-30 12:00:00',
                'title': '3462',
                'start_at': '2022-05-30 12:32:25',
                'total_seconds': '0',
                'calls': '1',
                'call_attempts': '1',
                'connected_first_attempt': '0',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '0',
                'hangup_count': '0',
                'error_count': '1',
            },
            {
                'period': '2022-05-30 16:00:00',
                'title': '3463',
                'start_at': '2022-05-30 16:57:42',
                'total_seconds': '0',
                'calls': '3',
                'call_attempts': '3',
                'connected_first_attempt': '0',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '3',
                'hangup_count': '0',
                'error_count': '0',
            },
            {
                'period': '2022-05-30 16:00:00',
                'title': '3464',
                'start_at': '2022-05-30 16:59:29',
                'total_seconds': '22',
                'calls': '1',
                'call_attempts': '1',
                'connected_first_attempt': '1',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '0',
                'hangup_count': '1',
                'error_count': '0',
            },
            {
                'period': '2022-05-30 18:00:00',
                'title': '3467',
                'start_at': '2022-05-30 18:23:42',
                'total_seconds': '20',
                'calls': '1',
                'call_attempts': '1',
                'connected_first_attempt': '1',
                'connected_second_attempt': '0',
                'ended_count': '1',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '0',
                'hangup_count': '0',
                'error_count': '0',
            },
            {
                'period': '2022-05-30 18:00:00',
                'title': '3468',
                'start_at': '2022-05-30 18:29:29',
                'total_seconds': '10',
                'calls': '1',
                'call_attempts': '2',
                'connected_first_attempt': '0',
                'connected_second_attempt': '1',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '1',
                'hangup_count': '1',
                'error_count': '0',
            },
            {
                'period': '2022-05-30 18:00:00',
                'title': '3469',
                'start_at': '2022-05-30 18:31:36',
                'total_seconds': '0',
                'calls': '1',
                'call_attempts': '1',
                'connected_first_attempt': '0',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '1',
                'hangup_count': '0',
                'error_count': '0',
            },
            {
                'period': '2022-05-30 18:00:00',
                'title': '3470',
                'start_at': '2022-05-30 18:31:53',
                'total_seconds': '10',
                'calls': '1',
                'call_attempts': '3',
                'connected_first_attempt': '0',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '1',
                'user_busy_count': '1',
                'hangup_count': '1',
                'error_count': '0',
            },
            {
                'period': '2022-05-31 11:00:00',
                'title': '3471',
                'start_at': '2022-05-31 11:49:05',
                'total_seconds': '4',
                'calls': '1',
                'call_attempts': '1',
                'connected_first_attempt': '1',
                'connected_second_attempt': '0',
                'ended_count': '0',
                'forwarded_count': '0',
                'no_answer_count': '0',
                'user_busy_count': '0',
                'hangup_count': '1',
                'error_count': '0',
            },
        ],
        'rows': 8,
        'statistics': {
            'elapsed': 0.000397258,
            'rows_read': 12,
            'bytes_read': 828,
        },
    }


GROUP_BY_TO_RESPONSE = {
    'batch_id': _get_calls_grouped_by_batch_id,
    'hour': _get_calls_grouped_by_hour,
    'month': _get_call_grouped_by_month,
}


def get_calls_grouped(group_by: str, tags: List[str]):
    response = GROUP_BY_TO_RESPONSE[group_by]()
    for tag_idx, tag in enumerate(tags):
        for row_idx, row in enumerate(response['data']):
            row[f'{tag}_tag_number'] = (row_idx + 2) * 10 ** tag_idx
    return response


def get_calls_batches_by_hour(tags: List[str]):
    response = _get_calls_batches_by_hour()
    for tag_idx, tag in enumerate(tags):
        for row_idx, row in enumerate(response['data']):
            row[f'{tag}_tag_number'] = (row_idx + 2) * 10 ** tag_idx
    return response


def get_dialogs(with_topics, period_type, tags: List[str]):
    datetime_suffix = ' 00:00:00' if period_type != 'month' else ''
    data = [
        {
            'sure_topic': 'topic1',
            'title': '2021-03-18' + datetime_suffix,
            'total_number': 10,
            'automated_number': 5,
            'closed_number': 2,
            'forwarded_number': 0,
            'not_answered_number': 2,
            'reopened_number': 1,
            'messages_number': 4,
            'messages_automated_number': 3,
            'minutes': 12.5,
        },
        {
            'sure_topic': 'topic1',
            'title': '2021-03-19' + datetime_suffix,
            'total_number': 10,
            'automated_number': 4,
            'closed_number': 1,
            'forwarded_number': 0,
            'not_answered_number': 2,
            'reopened_number': 2,
            'messages_number': 3,
            'messages_automated_number': 0,
            'minutes': 13.5,
        },
        {
            'sure_topic': 'topic2',
            'title': '2021-03-20' + datetime_suffix,
            'total_number': 10,
            'automated_number': 5,
            'closed_number': 1,
            'forwarded_number': 1,
            'not_answered_number': 2,
            'reopened_number': 1,
            'messages_number': 3,
            'messages_automated_number': 1,
            'minutes': 14.5,
        },
    ]
    if not with_topics:
        for row in data:
            row.pop('sure_topic')
    for tag_idx, tag in enumerate(tags):
        for row_idx, row in enumerate(data):
            row[f'{tag}_tag_number'] = (row_idx + 2) * 10 ** tag_idx
    return {
        'data': data,
        'rows': 3,
        'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
        'meta': [],
    }


def get_empty():
    return {
        'data': [],
        'rows': 0,
        'statistics': {'elapsed': 0.0, 'rows_read': 0, 'bytes_read': 0},
        'meta': [],
    }
