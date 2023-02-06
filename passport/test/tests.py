# -*- coding: utf-8 -*-
import logging
import math

from django.conf import settings
import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.oauth.core.db.config.scopes import get_scopes
from passport.backend.oauth.core.test.fake_configs import (
    FakeLoginToUidMapping,
    FakeScopes,
)
from passport.backend.oauth.core.test.fake_logs import FakeLoggingHandler
from passport.backend.oauth.core.test.framework import BaseTestCase
from passport.backend.oauth.core.test.utils import (
    iter_eq,
    set_side_effect_errors,
    with_setting_sets,
)


TEST_SCOPES_CONFIG = {
    1: {
        'keyword': 'test_scope',
        'ttl': None,
    },
}


class TestSetSideEffectErrors(BaseTestCase):
    def setUp(self):
        super(TestSetSideEffectErrors, self).setUp()
        self.floor_mock = mock.Mock(wraps=math.floor)
        self.floor_patch = mock.patch('math.floor', self.floor_mock)
        self.floor_patch.start()

    def tearDown(self):
        self.floor_patch.stop()
        super(TestSetSideEffectErrors, self).tearDown()

    def test_no_side_effect(self):
        eq_(math.floor(1.5), 1.0)

    def test_side_effect(self):
        set_side_effect_errors(self.floor_mock, [ValueError, TypeError])
        with assert_raises(ValueError):
            math.floor(1.5)
        with assert_raises(TypeError):
            math.floor(1.5)
        eq_(math.floor(1.5), 1.0)


class TestFakeScopes(BaseTestCase):
    def setUp(self):
        super(TestFakeScopes, self).setUp()
        self.fake_login_to_uid_mapping = FakeLoginToUidMapping()
        self.fake_login_to_uid_mapping.start()
        self.fake_scopes = FakeScopes()
        self.fake_scopes.start()

    def tearDown(self):
        self.fake_scopes.stop()
        self.fake_login_to_uid_mapping.stop()
        super(TestFakeScopes, self).tearDown()

    def test_load(self):
        self.fake_scopes.set_data(TEST_SCOPES_CONFIG)
        eq_(get_scopes().data, TEST_SCOPES_CONFIG)


class TestIterEq(BaseTestCase):
    def test_ok(self):
        iter_eq(1, 1)
        iter_eq([1, 2, 3], [1, 2, 3])
        iter_eq('hello', 'hello')

    def test_inequal_dicts(self):
        with assert_raises(AssertionError) as context:
            iter_eq({1: 1, 2: 2}, {2: 2, 3: 3})
        eq_(
            str(context.exception),
            '{1: 1, 2: 2} != {2: 2, 3: 3}\n\nIn first: [(1, 1)]\n\nIn second: [(3, 3)]',
        )

    def test_inequal_lists(self):
        with assert_raises(AssertionError) as context:
            iter_eq([1, 2], [2, 3])
        eq_(
            str(context.exception),
            '[1, 2] != [2, 3]\n\nIn first: [1]\n\nIn second: [3]',
        )

    def test_inequal_strings(self):
        with assert_raises(AssertionError) as context:
            iter_eq('12', '23')
        eq_(
            str(context.exception),
            '12 != 23',
        )


class TestFakeLogs(BaseTestCase):
    def setUp(self):
        super(TestFakeLogs, self).setUp()
        self.logger = logging.getLogger('smth')
        self._fake_log_handler = FakeLoggingHandler()
        self.logger.addHandler(self._fake_log_handler)

    def test_ok(self):
        self.logger.debug('debug1')
        self.logger.info('info1')
        self.logger.debug('debug2')

        self._fake_log_handler.assert_written('debug1', 'debug', -2)
        self._fake_log_handler.assert_written('debug2', 'DeBuG', -1)
        self._fake_log_handler.assert_written('info1', 'info')
        with assert_raises(AssertionError):
            self._fake_log_handler.assert_written('error1', 'error')


@with_setting_sets(
    {'SOME_SETTING': 1},
    {'SOME_SETTING': 2},
)
class TestWithSettingSets(BaseTestCase):
    def test_ok(self):
        ok_(settings.SOME_SETTING in [1, 2])
