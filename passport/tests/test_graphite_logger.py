# -*- coding: utf-8 -*-

import logging
from unittest import TestCase

from nose.tools import eq_
from passport.backend.core.logging_utils.faker.fake_tskv_logger import GraphiteLoggerFaker
from passport.backend.core.logging_utils.filters import TskvRequestIdFilter
from passport.backend.core.logging_utils.loggers.graphite import GraphiteLogger
from passport.backend.core.logging_utils.request_id import RequestIdManager


class GraphiteLoggerTestCase(TestCase):
    def setUp(self):
        self.graphite_logger = GraphiteLogger()

        self.faker = GraphiteLoggerFaker()
        self.faker.start()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_log(self):
        self.graphite_logger.log(foo='foo', bar='bar')
        self.faker.assert_has_written(
            [
                {
                    'tskv_format': 'passport-log',
                    'foo': 'foo',
                    'bar': 'bar',
                    'unixtime': self.faker.get_unixtime_mock(),
                    'timestamp': self.faker.get_timestamp_mock(),
                },
            ],
        )

    def test_make_context(self):
        self.graphite_logger.log(foo='bar', bar='foo')
        with self.graphite_logger.make_context(spam='spam'):
            self.graphite_logger.log(foo='bar', bar='foo')
        self.graphite_logger.log(foo='foo', bar='bar')

        self.faker.assert_has_written(
            [
                {
                    'tskv_format': 'passport-log',
                    'bar': 'foo',
                    'foo': 'bar',
                    'unixtime': self.faker.get_unixtime_mock(),
                    'timestamp': self.faker.get_timestamp_mock(),
                },
                {
                    'tskv_format': 'passport-log',
                    'bar': 'foo',
                    'foo': 'bar',
                    'spam': 'spam',
                    'unixtime': self.faker.get_unixtime_mock(),
                    'timestamp': self.faker.get_timestamp_mock(),
                },
                {
                    'tskv_format': 'passport-log',
                    'foo': 'foo',
                    'bar': 'bar',
                    'unixtime': self.faker.get_unixtime_mock(),
                    'timestamp': self.faker.get_timestamp_mock(),
                },
            ],
        )

    def test_graphite_logger_uses_init_context(self):
        graphite_logger = GraphiteLogger(foo='ctx')
        graphite_logger.log(bar='bar')

        self.faker.assert_has_written(
            [
                {
                    'tskv_format': 'passport-log',
                    'foo': 'ctx',
                    'bar': 'bar',
                    'unixtime': self.faker.get_unixtime_mock(),
                    'timestamp': self.faker.get_timestamp_mock(),
                },
            ],
        )

    def test_make_context_and_exception(self):
        class TestException(Exception):
            """Проверочное исключение"""

        try:
            with self.graphite_logger.make_context(spam='spam'):
                raise TestException()
        except TestException:
            pass
        self.graphite_logger.log(foo='foo', bar='bar')
        self.faker.assert_has_written(
            [
                {
                    'tskv_format': 'passport-log',
                    'foo': 'foo',
                    'bar': 'bar',
                    'unixtime': self.faker.get_unixtime_mock(),
                    'timestamp': self.faker.get_timestamp_mock(),
                },
            ],
        )


class TskvRequestIdFilterTestCase(TestCase):
    def setUp(self):
        self.record = logging.makeLogRecord({'msg': 'a'})
        RequestIdManager.clear_request_id()

    def filtered_record(self):
        TskvRequestIdFilter().filter(self.record)
        return self.record

    def test_format(self):
        eq_(self.filtered_record().request_id, '')

    def test_push_request_id(self):
        RequestIdManager.push_request_id(1)
        eq_(self.filtered_record().request_id, '@1')

    def test_push_request_id_many_times(self):
        RequestIdManager.push_request_id(1)
        RequestIdManager.push_request_id(2)
        eq_(self.filtered_record().request_id, '@1,2')

    def test_push_request_id_that_needs_escape(self):
        RequestIdManager.push_request_id('\t1')
        eq_(self.filtered_record().request_id, '@\\t1')
