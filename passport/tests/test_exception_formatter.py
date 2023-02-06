# -*- coding: utf-8 -*-
import logging
import unittest

from passport.backend.core.logging_utils.formatters import ExceptionFormatter
import six


class TestExceptionFormatter(unittest.TestCase):
    def test_exception_formatter(self):
        args = tuple()
        exc_info = None
        record = logging.LogRecord('name', 'level', 'pathname', 'lineno', 'msg', args, exc_info)
        formatted_text = ExceptionFormatter().format(record)
        assert isinstance(formatted_text, six.string_types)
