# -*- coding: utf-8 -*-
from mock import (
    Mock,
    patch,
)
from nose.tools import (
    assert_is_none,
    eq_,
)
from passport.backend.api.common.suggest import safe_detect_timezone
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts(
    ALLOWED_SOCIAL_RETPATH_SCHEMES=[],
)
class SafeDetectTimezoneTestCase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok(self):
        eq_(safe_detect_timezone('213.180.193.11').zone, 'Europe/Moscow')
        eq_(safe_detect_timezone('8.8.8.8').zone, 'America/New_York')

        assert_is_none(safe_detect_timezone('127.0.0.1'))

        with patch('passport.backend.api.common.suggest.Region', Mock(timezone='abc')):
            assert_is_none(safe_detect_timezone('8.8.8.8'))
