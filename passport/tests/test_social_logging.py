# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import traceback

from mock import Mock
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.social_logging import (
    ExceptionFilter,
    ExceptionFormatter,
    LevelFilter,
    WarningFormatter,
)
from passport.backend.social.common.test.consts import (
    REQUEST_ID1,
    UNIXTIME1,
)
from passport.backend.social.common.test.test_case import TestCase


class _BaseTestCase(TestCase):
    def _format_unixtime(self, timestamp):
        timestamp = datetime.fromtimestamp(timestamp)
        return timestamp.strftime('%Y-%m-%d %H:%M:%S,000')

    def _build_log_record(self, created_at=UNIXTIME1, level_name='INFO', exc_info=None,
                          msg='hello yello'):
        record = Mock(
            name='log_record',
            exc_info=exc_info,
            exc_text=None,
            levelname=level_name,
            created=created_at,
            msecs=0,
            msg=msg,
        )
        record.getMessage = Mock(name='getMessage', return_value=msg)
        return record

    def _build_context(self, request_id, handler_id='dudley', provider=None,
                       application=None):
        return Mock(
            name='context',
            request_id=request_id,
            application=application,
            provider=provider,
            handler_id=handler_id,
        )

    def _build_exc_info(self, message='hello'):
        try:
            raise_line = self._current_line_no() + 1
            raise Exception(message)
        except Exception:
            return dict(
                exc_info=sys.exc_info(),
                line_no=raise_line,
            )

    def _current_line_no(self):
        stack_trace = traceback.extract_stack()
        return stack_trace[-2][1]


class TestExceptionFilter(_BaseTestCase):
    def test_with_exception_info(self):
        exc_info = self._build_exc_info()
        record = self._build_log_record(exc_info=exc_info['exc_info'])

        self.assertTrue(ExceptionFilter().filter(record))

    def test_no_exception_info(self):
        record = Mock(exc_info=None)

        self.assertFalse(ExceptionFilter().filter(record))


class TestExceptionFormatter(_BaseTestCase):
    def test_exception(self):
        context = self._build_context(request_id=REQUEST_ID1)
        formatter = ExceptionFormatter(
            context,
            logtype='deedley',
        )
        exc_info = self._build_exc_info('hello hello')
        record = self._build_log_record(
            created_at=UNIXTIME1,
            exc_info=exc_info['exc_info'],
        )

        self.assertEqual(
            formatter.format(record),
            '%s unixtime=%s deedley %s Exception %s:%s hello hello' % (
                self._format_unixtime(UNIXTIME1),
                UNIXTIME1,
                REQUEST_ID1,
                __file__,
                exc_info['line_no'],
            ),
        )

    def test_no_exception(self):
        context = self._build_context(request_id=REQUEST_ID1)
        formatter = ExceptionFormatter(context)
        record = self._build_log_record(
            created_at=UNIXTIME1,
            exc_info=None,
        )

        self.assertEqual(
            formatter.format(record),
            '%s unixtime=%s - %s -' % (
                self._format_unixtime(UNIXTIME1),
                UNIXTIME1,
                REQUEST_ID1,
            ),
        )


class TestWarningFormatter(_BaseTestCase):
    def setUp(self):
        super(TestWarningFormatter, self).setUp()
        LazyLoader.register('slave_db_engine', self._fake_db.get_engine)
        providers.init()

    def test(self):
        app = providers.get_application_for_provider(Vkontakte.code)
        context = self._build_context(
            request_id=REQUEST_ID1,
            handler_id='dudley',
            application=app,
            provider=app.provider,
        )
        formatter = WarningFormatter(
            context,
            logtype='deedley',
        )
        record = self._build_log_record(
            created_at=UNIXTIME1,
            msg='hello yello',
        )

        self.assertEqual(
            formatter.format(record),
            '%s unixtime=%s deedley %s dudley vk %s * hello yello' % (
                self._format_unixtime(UNIXTIME1),
                UNIXTIME1,
                REQUEST_ID1,
                app.name,
            ),
        )


class TestLevelFilter(_BaseTestCase):
    def test_allowed_level(self):
        level_filter = LevelFilter(['foo', 'bar'])
        record = self._build_log_record(level_name='bar')
        self.assertTrue(level_filter.filter(record))

    def test_not_allowed_level(self):
        level_filter = LevelFilter(['foo'])
        record = self._build_log_record(level_name='spam')
        self.assertFalse(level_filter.filter(record))
