# pylint: disable=too-many-locals

import datetime
import logging

import pytest

from libstall.loggers.base import LavkaLogger, LavkaTSKVFormatter


class FakeHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.formatted_records = []

    def emit(self, record) -> None:
        self.formatted_records.append(self.format(record))


def tskv_str_to_dict(tskv_str: str):
    d = {}
    for kv in tskv_str.split('\t'):
        if '=' in kv:
            k, v = kv.split('=', 1)
        else:
            k, v = kv, None
        d[k] = v
    return d


@pytest.mark.parametrize(
    'test_input,expected',
    [
        (
            {'msg': 'hello'},
            {'text': 'hello'},
        ),
        (
            {'msg': 'hello \n world'},
            {'text': 'hello \\n world'},
        ),
        (
            {'msg': 'hello, %s', 'args': ('sosiska',)},
            {'text': 'hello, sosiska'},
        ),
        (
            {'msg': 'hello, %s', 'args': ('sosiska', 'kolbaska')},
            {'text': 'hello, %s', 'msg_args': str(('sosiska', 'kolbaska'))},
        ),
        (
            {'msg': 'hello, %s', 'args': ('sosiska', 'kolbaska')},
            {'text': 'hello, %s', 'msg_args': str(('sosiska', 'kolbaska'))},
        ),
        (
            {'msg': 'hello, %s-%d', 'args': ('sosiska', 42)},
            {'text': 'hello, sosiska-42'},
        ),
        (
            {'msg': 'hello', 'kwargs': {'yes': 'no'}},
            {'text': 'hello', 'yes': 'no'},
        ),
        (
            {
                'msg': 'hello, %s',
                'args': ('kolbaska',),
                'kwargs': {
                    'int': 42,
                    'float': 3.14,
                    'bool': True,
                    'datetime': datetime.datetime(1970, 1, 1, 0, 0),
                    'dict': {0: 0},
                    'None': None,
                }
            },
            {
                'text': 'hello, kolbaska',
                'int': '42',
                'float': '3.14',
                'bool': 'True',
                'datetime': str(datetime.datetime(1970, 1, 1, 0, 0)),
                'dict': '{0: 0}',
                'None': 'None',
            },
        ),
    ]
)
def test_log(tap, test_input, expected):
    with tap:
        logging.setLoggerClass(LavkaLogger)

        formatter = LavkaTSKVFormatter()

        handler = FakeHandler()
        handler.setFormatter(formatter)

        log = logging.getLogger('test_log')
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)

        log_msg = test_input['msg']
        log_args = test_input.get('args', ())
        log_kwargs = test_input.get('kwargs', {})

        # общие кейсы

        log.debug(log_msg, *log_args, **log_kwargs)
        log.info(log_msg, *log_args, **log_kwargs)
        log.warning(log_msg, *log_args, **log_kwargs)
        log.error(log_msg, *log_args, **log_kwargs)
        log.exception(log_msg, *log_args, **log_kwargs)

        levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'ERROR')

        for ind, line in enumerate(handler.formatted_records):
            d = tskv_str_to_dict(line)
            tap.ok(
                {
                    'tskv',
                    'timestamp',
                    'host',
                    'level',
                    'module',
                    'fpath',
                    'line',
                    'text',
                }.issubset(d.keys()),
                'All fields are here',
            )

            tap.eq_ok(d['level'], levels[ind], 'level')

            for k, v in expected.items():
                tap.eq_ok(d[k], v, f'{k}={v}')

        # складываем ошибку

        try:
            raise ZeroDivisionError('Oops')
        except ZeroDivisionError:
            log.exception('Oops')

        last = tskv_str_to_dict(handler.formatted_records[-1])
        tap.like(last['exc_info'], r'ZeroDivisionError: Oops', 'exc_info')

        # обший контекст

        with log.context(foo='bar'):
            log.info('with context 1')
            log.info('with context 2')

        last = tskv_str_to_dict(handler.formatted_records[-1])
        tap.eq_ok(
            (last['foo'], last['text']),
            ('bar', 'with context 2'),
            'with context 2'
        )

        last = tskv_str_to_dict(handler.formatted_records[-2])
        tap.eq_ok(
            (last['foo'], last['text']),
            ('bar', 'with context 1'),
            'with context 1'
        )

        log.info('no context')
        last = tskv_str_to_dict(handler.formatted_records[-1])
        tap.eq_ok(
            (last.get('foo', 'no bar'), last['text']),
            ('no bar', 'no context'),
            'no context'
        )
