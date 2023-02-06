# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import (
    EmailTestMixin,
    ProfileTestMixin,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import *
from passport.backend.api.views.bundle.constants import CHANGE_PASSWORD_REASON_FLUSHED
from passport.backend.core import authtypes
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_login_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.messenger_api.faker.fake_messenger_api import messenger_api_response
from passport.backend.core.counters import auth_email
from passport.backend.core.models.password import PASSWORD_CHANGING_REASON_FLUSHED_BY_ADMIN
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    TimeNow,
    TimeSpan,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.types.login.login import masked_login
from passport.backend.utils.common import merge_dicts


TEST_USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; LG-H818 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.95 Mobile Safari/537.36'
TEST_USER_AGENT_INFO = {
    'BrowserBase': 'Chromium',
    'BrowserBaseVersion': '48.0.2564.95',
    'BrowserEngine': 'WebKit',
    'BrowserEngineVersion': '537.36',
    'BrowserName': 'ChromeMobile',
    'BrowserVersion': '48.0.2564',
    'DeviceVendor': 'LG Electronics',
    'OSFamily': 'Android',
    'OSVersion': '6.0',
    'isBrowser': True,
    'isMobile': True,
    'isTablet': False,
    'isTouch': True,
}
TEST_LOCATION = u'Фэрфилд'
TEST_LOCATION_ENAME = u'Fairfield'
TEST_BROWSER = u'ChromeMobile 48.0.2564 (Android Marshmallow)'

TEST_COOKIE_TEMPLATE = 'passporttest=%s; Domain=.yandex.ru; Path=/'

TEST_FACEBOOK_IP = '31.13.76.68'

DEFAULT_PROFILE_SETTINGS = dict(
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    TENSORNET_MODEL_CONFIGS=TEST_MODEL_CONFIGS,
    TENSORNET_API_URL='http://tensornet:80/',
    WEB_PROFILE_DISTANCE_THRESHOLD=50,
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    FORCED_CHALLENGE_CHANCE=0.0,
    FORCED_CHALLENGE_PERIOD_LENGTH=3600,
    YDB_PERCENTAGE=0,
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    YABS_URL='localhost',
    **DEFAULT_PROFILE_SETTINGS
)
class BaseSubmitTestCase(BaseBundleTestViews, EmailTestMixin, ProfileTestMixin):
    url = None

    def setUp(self):
        self.patches = []

        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))

        self.setup_trackid_generator()
        self.setup_csrf_token_mock()
        self.start_patches()

        self.setup_blackbox_responses()
        self.setup_kolmogor_responses()
        self.setup_shakur_responses()
        self.setup_profile_patches()
        self.setup_profile_responses()
        self.setup_statbox_templates()

        self.setup_messenger_api_responses()

        self.setup_antifraud_responses()

    def tearDown(self):
        self.teardown_profile_patches()
        self.stop_patches()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches

    def start_patches(self):
        for patch in self.patches:
            patch.start()

    def stop_patches(self):
        for patch in reversed(self.patches):
            patch.stop()

    def setup_trackid_generator(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)
        self.patches.append(self.track_id_generator)

    def setup_csrf_token_mock(self):
        create_csrf_token_mock = mock.Mock(return_value=TEST_CSRF_TOKEN)
        patch = mock.patch(
            'passport.backend.api.views.bundle.auth.password.start.create_csrf_token',
            create_csrf_token_mock,
        )
        self.patches.append(patch)

    def setup_messenger_api_responses(self):
        self.env.messenger_api.set_response_value('check_user_lastseen', messenger_api_response(TEST_UID))

    def setup_blackbox_responses(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                domain=TEST_DOMAIN,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                ip=TEST_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                crypt_password='1:pwd',
                ttl=0,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )

    def setup_kolmogor_responses(self):
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.kolmogor.set_response_value('get', '1')

    def setup_shakur_responses(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def setup_antifraud_responses(self):
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response())

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='any_auth',
            track_id=self.track_id,
            ip=TEST_IP,
            consumer='dev',
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_COOKIE,
            origin=TEST_ORIGIN,
        )
        self.env.statbox.bind_entry(
            'start_commit_magic',
            action='start_commit_magic',
            type='auth_by_otp',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'submitted',
            action='submitted',
            referer=TEST_REFERER,
            retpath=TEST_RETPATH,
        )
        self.env.statbox.bind_entry(
            'updated',
            action='updated',
            referer=TEST_REFERER,
            uid=str(TEST_UID),
            _exclude=['track_id', 'origin'],
        )
        self.env.statbox.bind_entry(
            'profile_threshold_exceeded',
            uid=str(TEST_UID),
            action='profile_threshold_exceeded',
            is_password_change_required='0',
            email_sent='1',
            is_mobile='0',
            kind='ufo',
            **({'type': 'auth_by_otp'} if getattr(self, 'type', None) == 'magic' else {})
        )
        self.env.statbox.bind_entry(
            'redirect_to_password_change',
            action='redirect_to_password_change',
            mode='change_flushed_password',
            track_id=self.track_id,
            uid=str(TEST_UID),
            _exclude=['consumer', 'ip', 'origin', 'user_agent', 'yandexuid'],
        )
        self.env.statbox.bind_entry(
            'ufo_profile_checked',
            _inherit_from='local_base',
            action='ufo_profile_checked',
            current=self.make_user_profile(raw_env=TEST_RAW_ENV_FOR_PROFILE).as_json,
            ufo_status='1',
            ufo_distance='0',
            uid=str(TEST_UID),
            is_fresh_account='0',
            is_challenge_required='0',
            is_mobile='0',
            decision_source='ufo',
            kind='ufo',
            **({'type': 'auth_by_otp'} if getattr(self, 'type', None) == 'magic' else {})
        )
        self.env.statbox.bind_entry(
            'auth_notification',
            _inherit_from='local_base',
            action='auth_notification',
            consumer='dev',
            counter_exceeded='0',
            email_sent='1',
            uid=str(TEST_UID),
            **({'type': 'auth_by_otp'} if getattr(self, 'type', None) == 'magic' else {})
        )

    def get_headers(self, host=None, user_ip=None, cookie=None, user_agent=None):
        return mock_headers(
            host=host or TEST_HOST,
            user_agent=user_agent or TEST_USER_AGENT,
            cookie=cookie or 'Session_id=0:old-session; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            user_ip=user_ip or TEST_IP,
            referer=TEST_REFERER,
        )

    def get_base_query_params(self):
        raise NotImplementedError()  # pragma: no cover

    def query_params(self, exclude=None, **kwargs):
        base_params = self.get_base_query_params()
        for param in (exclude or []):
            base_params.pop(param)
        return merge_dicts(base_params, kwargs)

    def make_request(self, headers=None, exclude=None, **kwargs):
        return self.env.client.post(
            self.url,
            data=self.query_params(exclude=exclude, **kwargs),
            headers=headers or self.get_headers(),
        )

    def default_response_values(self):
        return {
            'track_id': self.track_id,
        }

    def account_response_values(self, login=TEST_LOGIN, is_workspace_user=False, domain=None):
        response = {
            'display_login': login,
            'display_name': {
                'default_avatar': '',
                'name': '',
            },
            'is_2fa_enabled': False,
            'is_rfc_2fa_enabled': False,
            'is_yandexoid': False,
            'is_workspace_user': is_workspace_user,
            'login': login,
            'person': {
                'birthday': u'1963-05-15',
                'country': u'ru',
                'firstname': u'\\u0414',
                'gender': 1,
                'language': u'ru',
                'lastname': u'\\u0424',
            },
            'uid': TEST_UID,
        }
        if domain is not None:
            response['domain'] = domain
        return response

    def base_challenge_auth_log_entry(self):
        return {
            'status': 'challenge_shown',
            'uid': str(TEST_UID),
            'type': authtypes.AUTH_TYPE_WEB,
            'comment': '-',
            'useragent': TEST_USER_AGENT,
            'yandexuid': TEST_YANDEXUID_COOKIE,
            'retpath': '-',
            'ip_from': TEST_IP,
            'client_name': 'passport',
        }

    def build_auth_log_entries(self, **kwargs):
        entry = self.base_challenge_auth_log_entry()
        entry.update(kwargs)
        return entry.items()

    def assert_authlog_records_written(self, expected_records):
        eq_(self.env.auth_handle_mock.call_count, len(expected_records))
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_records,
        )


class CommonContinueTests(object):
    def check_emails_not_sent(self):
        self.assert_emails_sent([])

    def check_emails_sent(self, login=TEST_LOGIN, email_login=None, location=TEST_LOCATION, browser=TEST_BROWSER,
                          native=True, external=True):
        email_login = email_login or login
        emails = []
        if external:
            emails.append(
                self.build_email('%s@%s' % (email_login, 'mail.ru'), location, browser, login),
            )
        if native:
            emails.append(
                self.build_email('%s@%s' % (email_login, 'yandex.ru'), location, browser, login, is_native=True),
            )
        self.assert_emails_sent(emails)

    def build_email(self, address, location, browser, login=TEST_LOGIN, is_native=False):
        data = {
            'language': 'ru',
            'addresses': [address],
            'subject': 'auth_challenge.subject',
            'tanker_keys': {
                'greeting': {'FIRST_NAME': u'\\u0414'},
                'auth_challenge.notice': {
                    'MASKED_LOGIN': login if is_native else masked_login(login),
                },
                'auth_challenge.if_hacked.with_url': {
                    'SUPPORT_URL': '<a href=\'https://yandex.ru/support/passport/troubleshooting/hacked.html\'>https://yandex.ru/support/passport/troubleshooting/hacked.html</a>',
                },
                'auth_challenge.journal.with_url': {
                    'JOURNAL_URL': '<a href=\'https://passport.yandex.ru/profile/journal\'>https://passport.yandex.ru/profile/journal</a>',
                },
                'signature.secure': {},
            },
        }
        if location or browser:
            data['tanker_keys']['auth_challenge.we_know'] = {}
        if location:
            data['tanker_keys']['user_meta_data.location'] = {
                'LOCATION': location,
            }
        if browser:
            data['tanker_keys']['user_meta_data.browser'] = {
                'BROWSER': browser,
            }
        return data

    def test_invalid_host_error(self):
        resp = self.make_request(
            headers=self.get_headers(host='google.com'),
        )
        self.assert_error_response(resp, ['host.invalid'])

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        expected_statbox_records = [
            self.env.statbox.entry('submitted'),
        ]
        if self.type == 'magic':
            expected_statbox_records.append(
                self.env.statbox.entry(
                    'start_commit_magic',
                    is_2fa_enabled='1',
                    password_like_otp='0',
                ),
            )
        else:
            expected_statbox_records.append(self.env.statbox.entry('ufo_profile_checked'))
        self.env.statbox.assert_has_written(expected_statbox_records)

        track = self.track_manager.read(self.track_id)
        eq_(track.password_verification_passed_at, TimeNow())
        eq_(
            track.is_otp_magic_passed,
            True if self.type == 'magic' else None,
        )
        eq_(
            track.auth_method,
            'magic' if self.type == 'magic' else 'password',  # otp протестируем отдельно
        )

    def test_fix_pdd_retpath(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                subscribed_to=[102],
                dbfields={
                    'userinfo_safe.hintq.uid': u'99:вопрос',
                    'userinfo_safe.hinta.uid': u'ответ',
                },
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = 'https://wordstat.yandex.ru/for/domain/?words=bla'

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.retpath, 'https://wordstat.yandex.ru/?words=bla')

    def test_pdd_empty_retpath(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                subscribed_to=[102],
                dbfields={
                    'userinfo_safe.hintq.uid': u'99:вопрос',
                    'userinfo_safe.hinta.uid': u'ответ',
                },
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = None

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.retpath is None)

    def test_cookies_logged(self):
        resp = self.make_request(
            headers=self.get_headers(
                cookie='yp=%s; ys=%s; %s' % (
                    COOKIE_YP_VALUE,
                    COOKIE_YS_VALUE,
                    TEST_USER_COOKIES,
                ),
            ),
        )
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        expected_statbox_records = [
            self.env.statbox.entry(
                'submitted',
                cookie_my=TEST_COOKIE_MY,
                cookie_yp=COOKIE_YP_VALUE,
                cookie_ys=COOKIE_YS_VALUE,
                l_login=TEST_LOGIN,
                l_uid=str(TEST_UID),
            ),
        ]
        if self.type == 'magic':
            expected_statbox_records.append(
                self.env.statbox.entry(
                    'start_commit_magic',
                    is_2fa_enabled='1',
                    password_like_otp='0',
                ),
            )
        else:
            expected_statbox_records.append(self.env.statbox.entry('ufo_profile_checked'))
        self.env.statbox.assert_has_written(expected_statbox_records)

    def test_cookie_l_invalid(self):
        resp = self.make_request(
            headers=self.get_headers(
                cookie=('yp=%s; ys=%s; %s' % (
                    COOKIE_YP_VALUE,
                    COOKIE_YS_VALUE,
                    TEST_USER_COOKIES,
                )).replace(TEST_COOKIE_L, 'foo'),
            ),
        )
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        expected_statbox_records = [
            self.env.statbox.entry(
                'submitted',
                cookie_my=TEST_COOKIE_MY,
                cookie_yp=COOKIE_YP_VALUE,
                cookie_ys=COOKIE_YS_VALUE,
            ),
        ]
        if self.type == 'magic':
            expected_statbox_records.append(
                self.env.statbox.entry(
                    'start_commit_magic',
                    is_2fa_enabled='1',
                    password_like_otp='0',
                ),
            )
        else:
            expected_statbox_records.append(self.env.statbox.entry('ufo_profile_checked'))
        self.env.statbox.assert_has_written(expected_statbox_records)

    def test_profile_show_captcha_no_challenges_available(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                emails=[
                    self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                ],
            ),
        )
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(tags=['email_hint']))

        with settings_context(
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **DEFAULT_PROFILE_SETTINGS
        ):
            resp = self.make_request()
        self.assert_error_response(
            resp,
            ['captcha.required'],
            track_id=self.track_id,
        )
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry(
                    'ufo_profile_checked',
                    af_action='ALLOW',
                    af_is_auth_forbidden='0',
                    af_is_challenge_required='1',
                    af_reason='some-reason',
                    af_tags='email_hint',
                    decision_source='antifraud_api',
                    is_challenge_required='1',
                ),
                self.env.statbox.entry(
                    'auth_notification',
                    email_sent='1',
                    is_challenged='1',
                ),
                self.env.statbox.entry(
                    'profile_threshold_exceeded',
                    decision_source='antifraud_api',
                    email_sent='1',
                    was_online_sec_ago=TimeSpan(0),
                ),
            ],
        )
        self.assert_authlog_records_written([self.build_auth_log_entries()])
        self.check_emails_sent(external=False)

    def test_profile_show_email_code_for_lite(self):
        lite_login = '%s@mail.ru' % TEST_LOGIN
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=lite_login,
                aliases={'lite': lite_login},
                crypt_password='1:pwd',
                emails=[
                    self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
                ],
            ),
        )
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(tags=['email_code']))

        with settings_context(
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **DEFAULT_PROFILE_SETTINGS
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(login=lite_login),
            )
        )
        self.assert_authlog_records_written([self.build_auth_log_entries()])
        self.check_emails_sent(login=lite_login, email_login=TEST_LOGIN, native=False)

    def test_profile_show_captcha_no_challenges_available_no_linguistics_for_location(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                emails=[
                    self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                ],
            ),
        )
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(tags=['email_hint']))

        region_mock = mock.Mock()
        region_mock().linguistics.side_effect = RuntimeError
        with settings_context(
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **DEFAULT_PROFILE_SETTINGS
        ), mock.patch(
            'passport.backend.api.views.bundle.mixins.account.Region',
            region_mock,
        ):
            resp = self.make_request()
        self.assert_error_response(
            resp,
            ['captcha.required'],
            track_id=self.track_id,
        )
        self.assert_authlog_records_written([self.build_auth_log_entries()])
        self.check_emails_sent(
            external=False,
            # При ошибке linguistics подставляется ename региона
            location=TEST_LOCATION_ENAME,
        )

    def test_show_forced_challenge(self):
        with settings_context(
                ALLOW_PROFILE_CHECK_FOR_WEB=True,
                **dict(DEFAULT_PROFILE_SETTINGS, FORCED_CHALLENGE_CHANCE=1.0)
        ):
            resp = self.make_request()

        if self.type == 'magic':
            self.assert_ok_response(
                resp,
                track_id=self.track_id,
                state='otp_auth_finished',
            )
            self.env.statbox.assert_has_written([
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry(
                    'start_commit_magic',
                    is_2fa_enabled='1',
                    password_like_otp='0',
                ),
            ])
        else:
            self.assert_error_response(
                resp,
                ['captcha.required'],
                track_id=self.track_id,
            )
            self.env.statbox.assert_has_written([
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry(
                    'ufo_profile_checked',
                    captcha_reason='8-ball',
                    decision_source='8-ball',
                    is_challenge_required='1',
                    is_fresh_profile_passed='0',
                    is_model_passed='1',
                    tensornet_estimate='0.1',
                    tensornet_model='profile-test',
                    tensornet_status='1',
                    ufo_distance='100',
                ),
                self.env.statbox.entry(
                    'profile_threshold_exceeded',
                    decision_source='8-ball',
                    email_sent='0',
                ),
            ])

    def test_show_forced_challenge_for_test_login(self):
        # Для логина тестировщиков всегда требуем каптчу, если конечно речь не об OTP
        FORCE_CHALLENGE_LOGIN = 'yndx.force-challenge.' + TEST_LOGIN

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=FORCE_CHALLENGE_LOGIN,
                crypt_password='1:pwd',
                attributes={'account.2fa_on': '1' if self.type == 'magic' else '0'},
            ),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = FORCE_CHALLENGE_LOGIN

        with settings_context(
                ALLOW_PROFILE_CHECK_FOR_WEB=True,
                **dict(DEFAULT_PROFILE_SETTINGS, FORCED_CHALLENGE_CHANCE=0.0)
        ):
            resp = self.make_request(login=FORCE_CHALLENGE_LOGIN)

        if self.type == 'magic':
            self.assert_ok_response(
                resp,
                track_id=self.track_id,
                state='otp_auth_finished',
            )
            self.env.statbox.assert_has_written([
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry(
                    'start_commit_magic',
                    is_2fa_enabled='1',
                    password_like_otp='0',
                ),
            ])
        else:
            self.assert_error_response(
                resp,
                ['captcha.required'],
                track_id=self.track_id,
            )
            self.env.statbox.assert_has_written([
                self.env.statbox.entry('submitted', input_login=FORCE_CHALLENGE_LOGIN),
                self.env.statbox.entry(
                    'ufo_profile_checked',
                    _exclude=['af_action', 'af_is_auth_forbidden', 'af_is_challenge_required', 'af_reason', 'af_tags'],
                    captcha_reason='8-ball',
                    decision_source='8-ball',
                    is_challenge_required='1',
                    is_fresh_profile_passed='0',
                    is_model_passed='1',
                    input_login=FORCE_CHALLENGE_LOGIN,
                    tensornet_estimate='0.1',
                    tensornet_model='profile-test',
                    tensornet_status='1',
                    ufo_distance='100',
                ),
                self.env.statbox.entry(
                    'profile_threshold_exceeded',
                    decision_source='8-ball',
                    email_sent='0',
                    input_login=FORCE_CHALLENGE_LOGIN,
                    was_online_sec_ago=TimeSpan(0),
                ),
            ])

    def test_show_forced_challenge_for_test_login_can_pass_captcha(self):
        # Если тестовый логин прошёл каптчу, то не надо показывать её вновь
        FORCE_CHALLENGE_LOGIN = 'yndx.force-challenge.' + TEST_LOGIN

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=FORCE_CHALLENGE_LOGIN,
                crypt_password='1:pwd',
                attributes={'account.2fa_on': '1' if self.type == 'magic' else '0'},
            ),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = FORCE_CHALLENGE_LOGIN
            # каптча пройдена
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        with settings_context(
                **dict(DEFAULT_PROFILE_SETTINGS, FORCED_CHALLENGE_CHANCE=0.0)
        ):
            resp = self.make_request(login=FORCE_CHALLENGE_LOGIN)

        if self.type == 'magic':
            self.assert_ok_response(
                resp,
                track_id=self.track_id,
                state='otp_auth_finished',
            )
            self.env.statbox.assert_has_written([
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry(
                    'start_commit_magic',
                    is_2fa_enabled='1',
                    password_like_otp='0',
                ),
            ])
        else:
            self.assert_ok_response(
                resp,
                track_id=self.track_id,
            )
            self.env.statbox.assert_has_written([
                self.env.statbox.entry(
                    'submitted',
                    input_login=FORCE_CHALLENGE_LOGIN,
                ),
            ])

    def test_show_forced_challenge_for_test_login_with_new_challenge(self):
        FORCE_CHALLENGE_LOGIN = 'yndx.force-challenge.' + TEST_LOGIN

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                emails=[
                    self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),  # новый челлендж
                ],
                login=FORCE_CHALLENGE_LOGIN,
                crypt_password='1:pwd',
                attributes={'account.2fa_on': '1' if self.type == 'magic' else '0'},
            ),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = FORCE_CHALLENGE_LOGIN
            # каптча пройдена
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        with settings_context(
                **dict(DEFAULT_PROFILE_SETTINGS, FORCED_CHALLENGE_CHANCE=0.0)
        ):
            resp = self.make_request(login=FORCE_CHALLENGE_LOGIN)

        if self.type == 'magic':
            self.assert_ok_response(
                resp,
                track_id=self.track_id,
                state='otp_auth_finished',
            )
            self.env.statbox.assert_has_written([
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry(
                    'start_commit_magic',
                    is_2fa_enabled='1',
                    password_like_otp='0',
                ),
            ])
        else:
            self.assert_ok_response(
                resp,
                track_id=self.track_id,
            )
            self.env.statbox.assert_has_written([
                self.env.statbox.entry(
                    'submitted',
                    input_login=FORCE_CHALLENGE_LOGIN,
                ),
            ])

    def test_no_forced_challenge(self):
        with settings_context(
            **dict(DEFAULT_PROFILE_SETTINGS, FORCED_CHALLENGE_CHANCE=0.0)
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )

        if self.type == 'magic':
            self.assert_ok_response(
                resp,
                track_id=self.track_id,
                state='otp_auth_finished',
            )

            self.env.statbox.assert_has_written([
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry(
                    'start_commit_magic',
                    is_2fa_enabled='1',
                    password_like_otp='0',
                ),
            ])
            track = self.track_manager.read(self.track_id)
            eq_(track.is_otp_magic_passed, True)
            eq_(track.auth_method, 'magic')
        else:
            self.env.statbox.assert_has_written([
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry('ufo_profile_checked'),
            ])

            track = self.track_manager.read(self.track_id)
            eq_(track.is_otp_magic_passed, None)
            eq_(track.auth_method, 'password')

    def test_profile_show_challenge(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                emails=[
                    self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                    self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
                ],
            ),
        )
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(tags=['email_hint']))

        with settings_context(
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **DEFAULT_PROFILE_SETTINGS
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(),
            )
        )
        self.assert_authlog_records_written([self.build_auth_log_entries()])
        self.check_emails_sent()

    def test_profile_challenge_disabled_in_config_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                emails=[
                    self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                    self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
                ],
            ),
        )

        with settings_context(
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **dict(
                DEFAULT_PROFILE_SETTINGS,
                AUTH_PROFILE_CHALLENGE_ENABLED=False,
            )
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.check_emails_not_sent()
        expected_statbox_records = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='ALLOW',
                af_is_auth_forbidden='0',
                af_is_challenge_required='0',
                af_reason='some-reason',
                af_tags='',
                decision_source='settings',
            ),
        ]
        if self.type == 'magic':
            expected_statbox_records.append(self.env.statbox.entry('start_commit_magic'))
        self.env.statbox.assert_has_written(expected_statbox_records)
        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_profile_challenge_disabled_from_yandex_server_ip_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                emails=[
                    self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                    self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
                ],
            ),
        )

        with settings_context(
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **DEFAULT_PROFILE_SETTINGS
        ), mock.patch('passport.backend.api.views.bundle.mixins.challenge.is_yandex_server_ip', lambda ip: True):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.check_emails_not_sent()
        expected_statbox_records = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='ALLOW',
                af_is_auth_forbidden='0',
                af_is_challenge_required='0',
                af_reason='some-reason',
                af_tags='',
                decision_source='yandex_ip',
            ),
        ]
        if self.type == 'magic':
            expected_statbox_records.append(self.env.statbox.entry('start_commit_magic'))
        self.env.statbox.assert_has_written(expected_statbox_records)
        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_profile_challenge_disabled_for_yandex_test_login_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_YANDEX_TEST_LOGIN,
                crypt_password='1:pwd',
                emails=[
                    self.create_native_email(TEST_YANDEX_TEST_LOGIN, 'yandex.ru'),
                    self.create_validated_external_email(TEST_YANDEX_TEST_LOGIN, 'mail.ru'),
                ],
            ),
        )

        with settings_context(
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **DEFAULT_PROFILE_SETTINGS
        ), mock.patch('passport.backend.api.views.bundle.mixins.challenge.is_yandex_ip', lambda ip: True):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.check_emails_not_sent()
        expected_statbox_records = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'ufo_profile_checked',
                _exclude=['af_action', 'af_is_auth_forbidden', 'af_is_challenge_required', 'af_reason', 'af_tags'],
                decision_source='test_login',
            ),
        ]
        if self.type == 'magic':
            expected_statbox_records.append(self.env.statbox.entry('start_commit_magic'))
        self.env.statbox.assert_has_written(expected_statbox_records)
        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_profile_challenge_disabled_for_yandex_test_login_from_external_network_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_YANDEX_TEST_LOGIN,
                crypt_password='1:pwd',
                emails=[
                    self.create_native_email(TEST_YANDEX_TEST_LOGIN, 'yandex.ru'),
                    self.create_validated_external_email(TEST_YANDEX_TEST_LOGIN, 'mail.ru'),
                ],
            ),
        )
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(tags=['email_hint']))

        with settings_context(
                BLACKBOX_URL='localhost',
                YABS_URL='localhost',
                **DEFAULT_PROFILE_SETTINGS
        ), mock.patch('passport.backend.api.views.bundle.mixins.challenge.is_yandex_ip', lambda ip: False):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
            )
        )
        expected_statbox_records = []
        expected_statbox_records.extend(
            [
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry(
                    'ufo_profile_checked',
                    _exclude=['af_action', 'af_is_auth_forbidden', 'af_is_challenge_required', 'af_reason', 'af_tags'],
                    is_challenge_required='0',
                ),
            ],
        )
        if self.type == 'magic':
            expected_statbox_records.append(self.env.statbox.entry('start_commit_magic'))
        self.env.statbox.assert_has_written(expected_statbox_records)

    def test_profile_show_challenge_without_useragent_and_ip_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                emails=[
                    self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                    self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
                ],
            ),
        )
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(tags=['email_hint']))

        with settings_context(
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **DEFAULT_PROFILE_SETTINGS
        ):
            resp = self.make_request(
                headers=self.get_headers(user_agent=TEST_USER_AGENT, user_ip='127.0.0.1'),
            )

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(),
            )
        )
        self.check_emails_sent(browser=None, location=None)
        self.assert_authlog_records_written([self.build_auth_log_entries(ip_from='127.0.0.1')])

    def test_profile_show_challenge_too_frequent_emails_not_sent_due_to_redis_counter(self):
        counter = auth_email.get_counter()
        counter.incr(TEST_UID)

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                emails=[
                    self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                    self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
                ],
            ),
        )
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(tags=['email_hint']))

        with settings_context(
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **DEFAULT_PROFILE_SETTINGS
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(),
            )
        )
        expected_statbox_records = [
            self.env.statbox.entry('submitted'),
        ]
        expected_statbox_records.extend(
            [
                self.env.statbox.entry(
                    'ufo_profile_checked',
                    af_action='ALLOW',
                    af_is_auth_forbidden='0',
                    af_is_challenge_required='1',
                    af_reason='some-reason',
                    af_tags='email_hint',
                    decision_source='antifraud_api',
                    is_challenge_required='1',
                ),
                self.env.statbox.entry(
                    'auth_notification',
                    counter_exceeded='1',
                    email_sent='0',
                    is_challenged='1',
                ),
                self.env.statbox.entry(
                    'profile_threshold_exceeded',
                    decision_source='antifraud_api',
                    email_sent='0',
                    was_online_sec_ago=TimeSpan(0),
                ),
            ],
        )
        if self.type == 'magic':
            expected_statbox_records.append(self.env.statbox.entry('start_commit_magic'))
        self.env.statbox.assert_has_written(expected_statbox_records)
        self.check_emails_not_sent()
        self.assert_authlog_records_written([self.build_auth_log_entries()])

    def test_always_show_challenge_for_profile_test_login(self):
        PROFILE_TRIAL_PERIOD = 60
        reg_time = datetime.now() - timedelta(seconds=PROFILE_TRIAL_PERIOD - 5)
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_PROFILE_USER_LOGIN,
                crypt_password='1:pwd',
                emails=[
                    self.create_native_email(TEST_PROFILE_USER_LOGIN, 'yandex.ru'),
                    self.create_validated_external_email(TEST_PROFILE_USER_LOGIN, 'mail.ru'),
                ],
                # Настраиваем условие пропуска челленджа для недавней регистрации,
                # которое не должно учитываться для тестового аккаунта
                dbfields={
                    'userinfo.reg_date.uid': reg_time.strftime('%Y-%m-%d %H:%M:%S'),
                },
            ),
        )

        with settings_context(
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **dict(
                DEFAULT_PROFILE_SETTINGS,
                AUTH_PROFILE_CHALLENGE_ENABLED=False,  # Тестовый логин имеет приоритет над этими настройками
            )
        ):
            resp = self.make_request(
                headers=self.get_headers(
                    cookie=('yp=%s; ys=%s; %s' % (
                        COOKIE_YP_VALUE,
                        COOKIE_YS_VALUE,
                        TEST_USER_COOKIES,
                    )).replace(TEST_COOKIE_L, 'foo'),
                ),
            )

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(login=TEST_PROFILE_USER_LOGIN),
            )
        )
        expected_statbox_records = []
        expected_statbox_records.extend(
            [
                self.env.statbox.entry(
                    'submitted',
                    cookie_my=TEST_COOKIE_MY,
                    cookie_yp=COOKIE_YP_VALUE,
                    cookie_ys=COOKIE_YS_VALUE,
                ),
                self.env.statbox.entry(
                    'ufo_profile_checked',
                    _exclude=['af_action', 'af_is_auth_forbidden', 'af_is_challenge_required', 'af_reason', 'af_tags'],
                    decision_source='test_login',
                    is_challenge_required='1',
                ),
                self.env.statbox.entry(
                    'auth_notification',
                    email_sent='1',
                    is_challenged='1',
                ),
                self.env.statbox.entry(
                    'profile_threshold_exceeded',
                    decision_source='test_login',
                    was_online_sec_ago=TimeSpan(0),
                ),
            ],
        )
        if self.type == 'magic':
            expected_statbox_records.append(self.env.statbox.entry('start_commit_magic'))
        self.env.statbox.assert_has_written(expected_statbox_records)
        self.check_emails_sent(login=TEST_PROFILE_USER_LOGIN)
        self.assert_authlog_records_written([self.build_auth_log_entries()])

    def test_ok_with_profile_disabled(self):
        with settings_context(
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **dict(
                DEFAULT_PROFILE_SETTINGS,
                AUTH_PROFILE_ENABLED=False,
            )
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        eq_(len(self.env.ufo_api.requests), 0)
        eq_(self.env.auth_challenge_handle_mock.call_count, 0)
        expected_statbox_records = [
            self.env.statbox.entry('submitted'),
        ]
        if self.type == 'magic':
            expected_statbox_records.append(
                self.env.statbox.entry(
                    'start_commit_magic',
                    is_2fa_enabled='1',
                    password_like_otp='0',
                ),
            )
        self.env.statbox.assert_has_written(expected_statbox_records)
        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_force_complete_lite(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LITE_LOGIN,
                crypt_password='1:pwd',
                aliases={
                    'lite': TEST_LITE_LOGIN,
                },
            ),
        )
        with settings_context(
                BLACKBOX_URL='localhost',
                YABS_URL='localhost',
                LITE_ACCOUNTS_ENFORCED_COMPLETION_DENOMINATOR=1,
                **dict(
                    DEFAULT_PROFILE_SETTINGS,
                    AUTH_PROFILE_ENABLED=False,
                )
        ):
            resp = self.make_request()
        expected_response = merge_dicts(
            self.default_response_values(),
            dict(
                account=self.account_response_values(login=TEST_LITE_LOGIN),
            ),
            dict(
                state='force_complete_lite',
                has_recovery_method=False,
            ),
        )
        self.assert_ok_response(resp, **expected_response)
        expected_statbox_records = [
            self.env.statbox.entry('submitted'),
        ]
        if self.type == 'magic':
            expected_statbox_records.append(self.env.statbox.entry('start_commit_magic'))
        self.env.statbox.assert_has_written(expected_statbox_records)

    def test_redirect_to_complete_pdd(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_PDD_LOGIN,
                crypt_password='1:pwd',
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            ),
        )
        resp = self.make_request()
        expected_response = merge_dicts(
            self.default_response_values(),
            dict(
                account=self.account_response_values(login=TEST_PDD_LOGIN, domain=TEST_PDD_DOMAIN_INFO),
            ),
            dict(
                state='complete_pdd',
            ),
        )
        self.assert_ok_response(resp, **expected_response)
        expected_statbox_records = [
            self.env.statbox.entry('submitted'),
        ]
        if self.type == 'magic':
            expected_statbox_records.append(
                self.env.statbox.entry('start_commit_magic'),
            )
        self.env.statbox.assert_has_written(expected_statbox_records)
        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(track.is_complete_pdd)
        ok_(not track.is_complete_pdd_with_password)

    def test_redirect_to_complete_workspace_pdd(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_PDD_LOGIN,
                crypt_password='1:pwd',
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                attributes={
                    'account.have_organization_name': '1',
                },
            ),
        )
        resp = self.make_request()
        expected_response = merge_dicts(
            self.default_response_values(),
            dict(
                account=self.account_response_values(
                    login=TEST_PDD_LOGIN,
                    domain=TEST_PDD_DOMAIN_INFO,
                    is_workspace_user=True,
                ),
            ),
            dict(
                state='complete_pdd',
            ),
        )
        self.assert_ok_response(resp, **expected_response)
        expected_statbox_records = [
            self.env.statbox.entry('submitted'),
        ]
        if self.type == 'magic':
            expected_statbox_records.append(self.env.statbox.entry('start_commit_magic'))
        self.env.statbox.assert_has_written(expected_statbox_records)
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_required)
        ok_(track.is_complete_pdd)
        ok_(not track.is_complete_pdd_with_password)

    def test_redirect_to_complete_workspace_pdd_with_password(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_PDD_LOGIN,
                crypt_password='1:pwd',
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                attributes={
                    'account.have_organization_name': '1',
                    'password.forced_changing_reason': '2',
                },
            ),
        )
        resp = self.make_request()
        expected_response = merge_dicts(
            self.default_response_values(),
            dict(
                account=self.account_response_values(
                    login=TEST_PDD_LOGIN,
                    domain=TEST_PDD_DOMAIN_INFO,
                    is_workspace_user=True,
                ),
            ),
            dict(
                state='complete_pdd_with_password',
            ),
        )
        self.assert_ok_response(resp, **expected_response)
        expected_statbox_records = [
            self.env.statbox.entry('submitted'),
        ]
        if self.type == 'magic':
            expected_statbox_records.append(
                self.env.statbox.entry('start_commit_magic'),
            )
        self.env.statbox.assert_has_written(expected_statbox_records)
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_required)
        ok_(not track.is_complete_pdd)
        ok_(track.is_complete_pdd_with_password)

    def test_redirect_to_change_password_requested_by_workspace_admin(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_PDD_LOGIN,
                crypt_password='1:pwd',
                subscribed_to=[102],
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                attributes={
                    'account.have_organization_name': '1',
                    'password.forced_changing_reason': PASSWORD_CHANGING_REASON_FLUSHED_BY_ADMIN,
                },
            ),
        )
        resp = self.make_request()
        expected_response = merge_dicts(
            self.default_response_values(),
            dict(
                account=self.account_response_values(
                    login=TEST_PDD_LOGIN,
                    domain=TEST_PDD_DOMAIN_INFO,
                    is_workspace_user=True,
                ),
            ),
            dict(
                state='change_password',
                change_password_reason=CHANGE_PASSWORD_REASON_FLUSHED,
                validation_method=None,
            ),
        )
        self.assert_ok_response(resp, **expected_response)
        expected_statbox_records = [
            self.env.statbox.entry('submitted'),
        ]
        expected_statbox_records.append(self.env.statbox.entry('redirect_to_password_change'))
        if self.type == 'magic':
            expected_statbox_records.append(self.env.statbox.entry('start_commit_magic'))
        self.env.statbox.assert_has_written(expected_statbox_records)
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_required)
        ok_(track.is_password_change)
        ok_(track.is_force_change_password)
        eq_(track.change_password_reason, CHANGE_PASSWORD_REASON_FLUSHED)
