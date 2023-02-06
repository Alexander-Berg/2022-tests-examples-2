# -*- coding: utf-8 -*-
import copy
import logging

import pytest

from taxi.conf import settings
from taxi.core import log


@pytest.mark.filldb(_fill=False)
def test_syslog_handler(capsys):
    logger = logging.getLogger(__name__)

    handler_syslog = log.SysLogHandler(
        ident='yandex-taxi-stq', level=logging.DEBUG
    )
    handler_syslog.setFormatter(
        log.SyslogConsoleFormatter(fmt=settings.LOG_CONSOLE_FORMAT)
    )

    while logger.handlers:
        logger.removeHandler(logger.handlers[0])
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler_syslog)

    logger.info(u'Привет', extra={
        u'_link': u'16eaa79e9eee4f4c97e2acb9f661ff8e',
        u'evlog_group': u'4abcb68cf662498c9a22a446439fcdda'
    })
    logger.info('Привет, %s', u'мир', extra={
        u'_link': u'16eaa79e9eee4f4c97e2acb9f661ff8e',
        u'evlog_group': u'4abcb68cf662498c9a22a446439fcdda'
    })
    logger.info('Привет', extra={
        u'_link': u'16eaa79e9eee4f4c97e2acb9f661ff8e',
        u'evlog_group': u'4abcb68cf662498c9a22a446439fcdda'
    })

    stdout, stderr = capsys.readouterr()
    # Check that logging statements above did NOT fail and write to stderr
    assert not stderr, stderr
    assert 'UNFORMATTABLE' not in stdout


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('record,expected', [
    (logging.LogRecord(
        'ok', logging.INFO, 'path', 1, 'all is %s', ('ok',), None
    ), 'ok - all is ok'),
    (logging.LogRecord(
        'ok', logging.INFO, 'path', 1, u'utf is %s', ('ok',), None
    ), u'ok - utf is ok'),
    (logging.LogRecord(
        'ok', logging.INFO, 'path', 1, u'utf-8 - это ок', (), None
    ), u'ok - utf-8 - это ок'.encode('utf-8')),
    (logging.LogRecord(
        u'name по-русски', logging.INFO, 'path', 1, 'all is %s', ('ok',), None
    ), u'name по-русски - all is ok'.encode('utf-8')),
    (logging.LogRecord(
        'ok', logging.INFO, 'path', 1, 'all is %s', (u'хорошо',), None
    ), u'ok - all is хорошо'.encode('utf-8')),
    (logging.LogRecord(
        'ok', logging.INFO, 'path', 1, 'all is %s',
        (u'борат'.encode('cp1251'),), None
    ), (
            u'ok - UNFORMATTABLE \'all is %%s\' %% (%r,): '
            u'\'ascii\' codec can\'t decode byte 0xe1 in position 0: '
            u'ordinal not in range(128)' % u'борат'.encode('cp1251')
        ).encode('utf-8')),
    (logging.LogRecord(
        'ok', logging.INFO, 'path', 1, 'all is %s',
        (u'борат'.encode('utf-8'),), None
    ), (
             u'ok - UNFORMATTABLE \'all is %%s\' %% (%r,): '
             u'\'ascii\' codec can\'t decode byte 0xd0 in position 0: '
             u'ordinal not in range(128)' % u'борат'.encode('utf-8')
     ).encode('utf-8')),
    (logging.LogRecord(
        'ok', logging.INFO, 'path', 1, 'привет, мир', (), None
    ), u'ok - привет, мир'.encode('utf-8')),
    (logging.LogRecord(
        'ok', logging.INFO, 'path', 1, 'привет,\tмир\r\n\0\\"\'', (), None
    ), u'ok - привет,\\tмир\\r\\n\\0\\\\\"\''.encode('utf-8')),
])
def test_taxi_formatter(record, expected):
    record = copy.deepcopy(record)
    f = log.SyslogConsoleFormatter(fmt='%(name)s - %(message)s')
    r = f.format(record)
    assert isinstance(r, str)
    assert expected == r
