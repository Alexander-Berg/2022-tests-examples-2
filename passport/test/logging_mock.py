# -*- coding: utf-8 -*-

import mock


class LogMock(object):
    def __init__(self):
        self.entries = []

    def log(self, record, level, args=None, kwargs=None):
        self.entries.append(
            (record, level, args or None, kwargs or None,),
        )

    def info(self, record, *args, **kwargs):
        self.log(record, 'INFO', args, kwargs)

    def debug(self, record, *args, **kwargs):
        self.log(record, 'DEBUG', args, kwargs)

    def warning(self, record, *args, **kwargs):
        self.log(record, 'WARNING', args, kwargs)

    def error(self, record, *args, **kwargs):
        self.log(record, 'ERROR', args, kwargs)

    def exception(self, record, *args, **kwargs):
        self.log(record, 'EXCEPTION', args, kwargs)

    def isEnabledFor(self, *args, **kwargs):
        return True


class LoggingMock(object):
    def __init__(self):
        self.loggers = {}
        self.mock = mock.patch('logging.getLogger', side_effect=self.getLogger)

    def getLogger(self, name):
        if name not in self.loggers:
            self.loggers[name] = LogMock()
        return self.loggers[name]

    def start(self):
        self.mock.start()

    def stop(self):
        self.mock.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
