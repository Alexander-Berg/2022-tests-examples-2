# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from taxi.core import async

import pytest

from taxi.internal import dbh
from taxi_stq.tasks.bulk_notify import process_source_task


@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_task_parse_failure(patch, task_id='task1'):
    @patch('taxi.external.mds.download')
    @async.inline_callbacks
    def mds_download(path, log_extra=None):
        yield
        async.return_value('')

    @patch('taxi_stq.tasks.bulk_notify.process_source_task.'
           'SourceFileParser')
    def sourcefileparser(data, text=None):
        raise process_source_task.ParseError('test failure')

    yield process_source_task._task(task_id)

    task = yield dbh.bulk_notify_tasks.Doc.find_one_by_id(task_id)
    assert task.status == dbh.bulk_notify_tasks.STATUS_FAILED
    assert task.message == 'test failure'


@pytest.mark.parametrize('text,data,expected_result', [
    (
        None,
        [
            b'type;user_id;text',
            b'apns;foo;hello, world',
            b'gcm;bar;hello, world',
        ],
        [
            {
                'line': 2,
                'type': 'apns',
                'user_id': 'foo',
                'text': 'hello, world',
                'payload': {},
            },
            {
                'line': 3,
                'type': 'gcm',
                'user_id': 'bar',
                'text': 'hello, world',
                'payload': {},
            },
        ]
    ),
    (
        None,
        [
            b'type;user_id;text',
            b'apns;foo;тест',
        ],
        [
            {
                'line': 2,
                'type': 'apns',
                'user_id': 'foo',
                'text': 'тест',
                'payload': {},
            },
        ]
    ),
    (
        None,
        [
            b'type;user_id;text',
            b'bad;bar;hello, world',
        ],
        [
            {
                'line': 2,
                'status': 'error',
                'reason': 'unsupported notification type bad',
            },
        ]
    ),
    (
        'тест',
        [
            b'type;user_id',
            b'apns;foo',
        ],
        [
            {
                'line': 2,
                'type': 'apns',
                'user_id': 'foo',
                'text': 'тест',
                'payload': {},
            },
        ]
    ),
    (
        'тест',
        [
            b'type;user_id;text',
            b'apns;foo;',
            b'apns;bar;тест2',
        ],
        [
            {
                'line': 2,
                'type': 'apns',
                'user_id': 'foo',
                'text': 'тест',
                'payload': {},
            },
            {
                'line': 3,
                'type': 'apns',
                'user_id': 'bar',
                'text': 'тест2',
                'payload': {},
            },
        ]
    ),
])
@pytest.mark.filldb(_fill=False)
def test_source_parser(text, data, expected_result):
    parser = process_source_task.SourceFileParser(data, text=text)
    result = list(
        parser.parse()
    )
    assert result == expected_result


@pytest.mark.parametrize('data,expected_exc', [
    (
        [],
        process_source_task.ParseError,
    ),
    (
        [b'foo,bar'],
        process_source_task.ParseError,
    ),
    (
        [
            b'type;user_id;text',
            b'apns;foo',
        ],
        process_source_task.ParseError,
    ),
    (
        [
            b'type;user_id;text',
            'apns;foo;тест'.encode('koi8-r'),
        ],
        process_source_task.ParseError,
    ),
    (
        [b'type;user_id;text'],
        process_source_task.ParseError,
    )
])
@pytest.mark.filldb(_fill=False)
def test_source_parser_failures(data, expected_exc):
    with pytest.raises(expected_exc):
        parser = process_source_task.SourceFileParser(data)
        list(parser.parse())
