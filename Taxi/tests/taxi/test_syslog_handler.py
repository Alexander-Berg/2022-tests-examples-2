import logging

from taxi.logs import formatters
from taxi.logs import log


def test_syslog_surrogate_pair():
    msg_with_surrogate_pair = 'HELLO\ud83d\ude4fHELLO'

    log_record = logging.Logger({}).makeRecord(
        name='vaysa',
        level='INFO',
        fn='(unknown file)',
        lno=0,
        msg=msg_with_surrogate_pair,
        args=(),
        exc_info=None,
        func='(unknown function)',
        extra=None,
        sinfo=None,
    )

    handler = log.SysLogHandler()
    formatter = formatters.TskvFormatter(log.DEFAULT_LOG_FORMAT)
    handler.setFormatter(formatter)
    # emit was called without UnicodeEncodeError (surrogates not allowed)
    handler.emit(log_record)
