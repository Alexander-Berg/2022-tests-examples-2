# -*- coding: utf-8 -*-

import json
import re

import mock
from passport.backend.api.test.mixins import ProfileTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.mixins.challenge import DecisionSource
from passport.backend.core.test.consts import *
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.faker import FakeTrackIdGenerator

from .base_test_data import (
    TEST_BROKER_CONSUMER,
    TEST_SOCIAL_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
    TEST_YANDEXUID_COOKIE,
)
from .builders import (
    PrimaryTestBuilder,
    ThirdPartyTestBuilder,
)
from .statbox_mixin import setup_statbox_templates


TEST_SOCIAL_SUGGEST_RELATED_ACCOUNT_CONSUMERS_RE_LIST = [
    'dev',
    TEST_BROKER_CONSUMER,
    TEST_CONSUMER1,
]
TEST_SOCIAL_SUGGEST_RELATED_ACCOUNT_CONSUMERS_RE_LIST = [re.compile('^%s$' % c) for c in TEST_SOCIAL_SUGGEST_RELATED_ACCOUNT_CONSUMERS_RE_LIST]


class FakeSocialLoginGenerator(object):
    def __init__(self):
        self._mock = mock.Mock()
        self._patch = mock.patch('passport.backend.api.common.login.types.login.login.generate_social_login', self._mock)

    def start(self):
        self._patch.start()
        return self

    def stop(self):
        self._patch.stop()

    def set_return_value(self, value):
        self._mock.return_value = value


@with_settings_hosts(
    SOCIAL_SUGGEST_RELATED_ACCOUNT_CONSUMERS_RE_LIST=TEST_SOCIAL_SUGGEST_RELATED_ACCOUNT_CONSUMERS_RE_LIST,
    SOCIAL_SUGGEST_RELATED_ACCOUNT_ENABLED=True,
)
class BaseTestCase(
    ProfileTestMixin,
    BaseBundleTestViews,
):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.setup_grants()

        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(TEST_TRACK_ID1)

        self._social_login_generator = FakeSocialLoginGenerator().start()
        self.track_manager = self.env.track_manager.get_manager()
        self.setup_profile_patches()

    def tearDown(self):
        self.teardown_profile_patches()
        del self.track_manager
        self._social_login_generator.stop()
        del self._social_login_generator
        self.track_id_generator.stop()
        del self.track_id_generator
        self.env.stop()
        del self.env
        super(BaseTestCase, self).tearDown()

    def setup_grants(self, **kwargs):
        self.env.grants.set_grants_return_value(
            {
                'dev': {
                    'grants': {'auth_social': ['base']},
                    'networks': [TEST_CONSUMER_IP1],
                },
            },
        )

    def get_primary_builder(self):
        return PrimaryTestBuilder(
            env=self.env,
            social_login_generator=self._social_login_generator,
        )

    def get_third_party_builder(self):
        return ThirdPartyTestBuilder(
            env=self.env,
            social_login_generator=self._social_login_generator,
        )

    def assert_session_cookies_ok(self, rv):
        rv = json.loads(rv.data)
        self.assertIn('cookies', rv)
        cookies = rv['cookies']

        self.assert_cookie_ok(cookies[0], 'Session_id', expires=None)
        self.assert_cookie_ok(cookies[1], 'sessionid2', expires=None)

    def patch_build_auth_cookies_and_session(self):
        self.build_auth_cookies_and_session_response = mock.Mock()
        self.patch_for_build_auth_cookies_and_session = mock.patch(
            'passport.backend.api.views.bundle.auth.social.base.build_auth_cookies_and_session',
            mock.Mock(side_effect=self.build_auth_cookies_and_session_response),
        )
        self.patch_for_build_auth_cookies_and_session.start()

    def unpatch_build_auth_cookies_and_session(self):
        self.patch_for_build_auth_cookies_and_session.stop()
        del self.patch_for_build_auth_cookies_and_session
        del self.build_auth_cookies_and_session_response

    def patch_check_session_cookie(self):
        self.patch_for_check_session_cookie = mock.patch('passport.backend.api.views.bundle.auth.social.controllers.StartView.check_session_cookie')
        self.is_session_valid_response = self.patch_for_check_session_cookie.start()

    def unpatch_check_session_cookie(self):
        del self.is_session_valid_response
        self.patch_for_check_session_cookie.stop()
        del self.patch_for_check_session_cookie

    def patch_build_available_social_login(self):
        self.build_available_social_login_response = mock.Mock()
        self.patch_for_build_available_social_login = mock.patch(
            'passport.backend.api.views.bundle.auth.social.controllers.build_available_social_login',
            mock.Mock(side_effect=self.build_available_social_login_response),
        )
        self.patch_for_build_available_social_login.start()

    def unpatch_build_available_social_login(self):
        self.patch_for_build_available_social_login.stop()
        del self.patch_for_build_available_social_login
        del self.build_available_social_login_response

    def patch_get_countries_suggest(self):
        self.patch_for_get_countries_suggest = mock.patch(
            'passport.backend.api.common.account.get_countries_suggest',
            mock.Mock(return_value=['en']),
        )
        self.patch_for_get_countries_suggest.start()

    def unpatch_get_countries_suggest(self):
        self.patch_for_get_countries_suggest.stop()
        del self.patch_for_get_countries_suggest

    def patch_get_language_suggest(self):
        self.patch_for_get_language_suggest = mock.patch(
            'passport.backend.api.common.account.get_language_suggest',
            mock.Mock(return_value='en'),
        )
        self.patch_for_get_language_suggest.start()

    def unpatch_get_language_suggest(self):
        self.patch_for_get_language_suggest.stop()
        del self.patch_for_get_language_suggest

    def setup_statbox_templates(self):
        setup_statbox_templates(self.env.statbox)
        self.env.statbox.bind_entry(
            'ufo_profile_checked',
            action='ufo_profile_checked',
            af_action='ALLOW',
            af_is_auth_forbidden='0',
            af_is_challenge_required='0',
            af_reason='some-reason',
            af_tags='',
            current=self.make_user_profile(
                raw_env=dict(
                    ip=TEST_USER_IP,
                    user_agent_info=None,
                    yandexuid=TEST_YANDEXUID_COOKIE,
                ),
            ).as_json,
            decision_source=DecisionSource.UFO,
            ip=str(TEST_USER_IP),
            is_challenge_required='0',
            is_fresh_account='0',
            is_fresh_profile_passed='0',
            is_mobile='0',
            is_model_passed='1',
            kind='ufo',
            mode='any_auth',
            tensornet_estimate=str(TEST_PROFILE_GOOD_ESTIMATE1),
            tensornet_model='profile-passp-16385',
            tensornet_status='1',
            track_id=self.track_id,
            ufo_distance='100',
            ufo_status='1',
            uid=str(TEST_SOCIAL_UID),
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_COOKIE,
        )
