# -*- coding: utf-8 -*-

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    settings_context,
    with_settings,
)


@with_settings(
    TEST_1='foo',
    TEST_2='bar',
)
class SettingsUtilsTest(PassportTestCase):
    def test_1(self):
        with settings_context(TEST_3='zar'):
            ok_(not hasattr(settings, 'TEST_1'))
            ok_(not hasattr(settings, 'TEST_2'))
            eq_(settings.TEST_3, 'zar')

        eq_(settings.TEST_1, 'foo')
        eq_(settings.TEST_2, 'bar')
        ok_(not hasattr(settings, 'TEST_3'))

    def test_2(self):
        with settings_context(
            TEST_3='zar',
            inherit_if_set=('TEST_1', 'TEST_2'),
            real_settings=settings,
        ):
            eq_(settings.TEST_1, 'foo')
            eq_(settings.TEST_2, 'bar')
            eq_(settings.TEST_3, 'zar')

        eq_(settings.TEST_1, 'foo')
        eq_(settings.TEST_2, 'bar')
        ok_(not hasattr(settings, 'TEST_3'))
