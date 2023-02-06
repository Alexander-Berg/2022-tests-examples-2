import logging

import pytest

from taxi.core.log import formatters


class RecordFactory(object):
    logger = logging.Logger(__name__)

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        record = self._make_record(*self.args, **self.kwargs)
        return record

    def _make_record(self, name='foo', level=logging.INFO, fn='f()', lno=123,
                     msg='', args=(), exc_info=None, func=None, extra=None):
        return self.logger.makeRecord(
            name, level, fn, lno, msg, args, exc_info, func=func, extra=extra
        )


@pytest.mark.parametrize(
    'formatter,record_factory,expected_message,expected_tskv,'
    'expected_requestid', [
        (
            formatters.SyslogConsoleFormatter(),
            RecordFactory(msg='foo'),
            'foo',
            '_type=log\thost=test-host:None',
            None,
        ),
        (
            formatters.SyslogConsoleFormatter(
                default_link='link', default_extdict={'command': 'foo'}
            ),
            RecordFactory(msg='foo'),
            'foo',
            '_type=log\tcommand=foo\thost=test-host:None',
            'link',
        ),
        (
            formatters.SyslogConsoleFormatter(
                default_link='link', default_extdict={'command': 'foo'}
            ),
            RecordFactory(
                msg='foo', extra={
                    '_link': 'link2',
                    'extdict': {
                        'command': 'bar'
                    }
                }
            ),
            'foo',
            '_type=log\tcommand=bar\thost=test-host:None',
            'link2',
        ),
])
@pytest.mark.asyncenv('blocking')
def test_syslog_console_formatter(
        patch, formatter, record_factory, expected_message, expected_tskv,
        expected_requestid):
    @patch('os.uname')
    def uname():
        return 'Linux', 'test-host'

    record = record_factory()
    message = formatter.format(record)

    tskv = '\t'.join(sorted(record.extra_tskv.split('\t')))
    assert message == expected_message
    assert tskv == expected_tskv
    assert record.requestid == expected_requestid
