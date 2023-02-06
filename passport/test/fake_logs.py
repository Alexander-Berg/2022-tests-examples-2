# -*- coding: utf-8 -*-
import logging

from nose.tools import (
    eq_,
    ok_,
)


class FakeLoggingHandler(logging.Handler):
    """
    Работает только для логгеров, которые не перехватываются nose'ом
    (например, для тех, что пишут в StreamHandler)
    """
    def __init__(self, level='DEBUG'):
        self.reset()
        super(FakeLoggingHandler, self).__init__(level)

    def emit(self, record):
        self._messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self._messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }

    def assert_written(self, message, level, index=-1):
        ok_(
            len(self.messages(level=level)) > 0,
            'No messages for level "%s". All written messages: %s' % (level, self.messages()),
        )
        eq_(
            self.messages(level=level)[index],
            message,
            '%s != %s. \n\nAll written messages: %s' % (self.messages(level=level)[index], message, self.messages()),
        )

    def messages(self, level=None):
        messages = self._messages
        if level is not None:
            messages = messages[level.lower()]
        return messages
