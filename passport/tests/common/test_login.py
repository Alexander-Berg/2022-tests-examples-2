# -*- coding: utf-8 -*-

from mock import (
    Mock,
    patch,
)
from nose.tools import eq_
from passport.backend.api.common.login import build_available_social_login
from passport.backend.api.exceptions import SuggestSocialLoginError
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_loginoccupation_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestBuildSocialLogin(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'uid-username': 'free'}),
        )
        self.generate_social_login_mock = Mock(return_value='uid-username')
        self.generate_social_login_patch = patch(
            'passport.backend.core.types.login.login.generate_social_login',
            self.generate_social_login_mock,
        )
        self.generate_social_login_patch.start()

    def tearDown(self):
        self.env.stop()
        self.generate_social_login_patch.stop()
        del self.env
        del self.generate_social_login_mock
        del self.generate_social_login_patch

    def test_simple(self):
        login = build_available_social_login(retries=3, env=Mock())
        eq_(login, 'uid-username')

    def test_not_available_any_login(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'uid-username': 'occupied'}),
        )

        with self.assertRaises(SuggestSocialLoginError):
            build_available_social_login(retries=3, env=Mock())

        eq_(self.generate_social_login_mock.call_count, 3)
