# -*- coding: utf-8 -*-
import hashlib
import json
import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import *
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
    BLACKBOX_LOGIN_VALID_STATUS,
    BLACKBOX_PASSWORD_BAD_STATUS,
    BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
    BLACKBOX_PASSWORD_VALID_STATUS,
    BLACKBOX_SECOND_STEP_RFC_TOTP,
    BLACKBOX_SESSIONID_INVALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_hosted_domains_response,
    blackbox_login_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.shakur import ShakurTemporaryError
from passport.backend.core.builders.shakur.faker.fake_shakur import shakur_check_password_no_postfix
from passport.backend.core.models.password import PASSWORD_CHANGING_REASON_PWNED
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import deep_merge


eq_ = iterdiff(eq_)

TEST_COOKIE_TEMPLATE = 'passporttest=%s; Domain=.yandex.ru; Path=/'
TEST_CSRF_TOKEN = 'csrf'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    YABS_URL='localhost',
)
class BaseConfirmTestCase(BaseBundleTestViews, EmailTestMixin):
    http_method = 'POST'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie='Session_id=0:old-session; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
        user_ip=TEST_IP,
        referer=TEST_REFERER,
    )

    def setUp(self):
        self.patches = []

        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['confirm']}))

        self.setup_cookie_mocks()
        self.setup_trackid_generator()
        self.setup_csrf_token_mock()
        self.start_patches()

        self.setup_blackbox_responses()
        self.setup_kolmogor_responses()
        self.setup_shakur_responses()
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        self.stop_patches()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches
        del self.build_cookies_yx
        del self.build_cookie_l

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
            'passport.backend.api.views.bundle.auth.password.confirm.create_csrf_token',
            create_csrf_token_mock,
        )
        self.patches.append(patch)

    def setup_cookie_mocks(self):
        self.build_cookies_yx = mock.Mock(return_value=[EXPECTED_YP_COOKIE, EXPECTED_YS_COOKIE])
        self.build_cookie_l = mock.Mock(return_value=EXPECTED_L_COOKIE)

        self.patches.extend([
            mock.patch(
                'passport.backend.api.common.authorization.build_cookies_yx',
                self.build_cookies_yx,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_l',
                self.build_cookie_l,
            ),
        ])

    def setup_blackbox_responses(self):
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password='1:pwd',
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        hosted_domains_response = blackbox_hosted_domains_response(
            count=1,
            domain=TEST_DOMAIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )

        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            authid=TEST_OLD_AUTH_ID,
            ip=TEST_IP,
            age=TEST_COOKIE_AGE,
            time=TEST_COOKIE_TIMESTAMP,
            crypt_password='1:pwd',
            ttl=0,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        createsession_response = blackbox_createsession_response(
            authid=TEST_AUTH_ID,
            ip=TEST_IP,
            time=TEST_COOKIE_TIMESTAMP,
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            createsession_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

    def setup_kolmogor_responses(self):
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.kolmogor.set_response_value('get', '1')

    def setup_shakur_responses(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='confirm_password',
            track_id=self.track_id,
            ip=TEST_IP,
            consumer='dev',
            user_agent=TEST_USER_AGENT,
            uid=str(TEST_UID),
            yandexuid=TEST_YANDEXUID_COOKIE,
            origin=TEST_ORIGIN,
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'confirmed',
            _inherit_from='local_base',
            action='confirmed',
        )
        self.env.statbox.bind_entry(
            'change_password',
            action='redirect_to_password_change',
            is_pwned='0',
            is_weak='1',
            mode='change_weak_password',
            track_id=self.track_id,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'account_password_changing_required',
            uid=str(TEST_UID),
            event='account_modification',
            entity='password.is_changing_required',
            user_agent=TEST_USER_AGENT,
            ip=TEST_IP,
            new=PASSWORD_CHANGING_REASON_PWNED,
            old='-',
            operation='created',
        )

    def get_expected_response_values(self, uid=TEST_UID, login=TEST_LOGIN, display_login=None,
                                     domain=None, **kwargs):
        expected = {
            'track_id': self.track_id,
            'account': {
                'uid': uid,
                'login': login,
                'display_name': {'name': '', 'default_avatar': ''},
                'person': {
                    'firstname': u'\\u0414',
                    'lastname': u'\\u0424',
                    'birthday': '1963-05-15',
                    'gender': 1,
                    'language': 'ru',
                    'country': 'ru',
                },
                'display_login': login if display_login is None else display_login,
            },
        }
        if domain:
            expected['account']['domain'] = domain

        expected.update(kwargs)
        return expected

    def assert_statbox_logged(self, entries):
        self.check_statbox_log_entries(self.env.statbox_handle_mock, entries)

    def check_statbox_empty(self):
        self.assert_statbox_logged([])

    def check_statbox_check_cookies(self):
        self.assert_statbox_logged([self.env.statbox.entry('check_cookies')])


class TestConfirmSubmit(BaseConfirmTestCase):
    default_url = '/1/bundle/auth/password/confirm/submit/?consumer=dev'
    http_query_args = {
        'retpath': TEST_RETPATH,
        'origin': TEST_ORIGIN,
    }

    def setUp(self):
        super(TestConfirmSubmit, self).setUp()
        self.http_query_args.update(track_id=self.track_id)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID

    def check_track_ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        eq_(track.retpath, TEST_RETPATH)
        eq_(track.origin, TEST_ORIGIN)
        eq_(track.authorization_session_policy, 'sessional')
        ok_(track.is_allow_otp_magic)
        ok_(track.csrf_token)
        eq_(track.login_required_for_magic, TEST_LOGIN)

    def check_statbox_ok(self):
        self.assert_statbox_logged([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted'),
        ])

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values(csrf_token=TEST_CSRF_TOKEN)
        )
        self.check_track_ok()
        self.check_statbox_ok()

    def test_account_without_password(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                login=TEST_LOGIN,
                attributes={'password.encrypted': ''},
            ),
        )
        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['account.without_password'],
            **self.get_expected_response_values()
        )
        self.check_statbox_check_cookies()

    def test_action_not_required(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                age=1,
            ),
        )
        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['action.not_required'],
            **self.get_expected_response_values()
        )
        self.check_statbox_check_cookies()

    def test_session_cookie_invalid(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )
        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['sessionid.invalid'],
            track_id=self.track_id,
        )
        self.check_statbox_check_cookies()

    def test_uid_not_in_session_cookie(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = '456'

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['sessionid.no_uid'],
            track_id=self.track_id,
        )
        self.check_statbox_check_cookies()

    def test_captcha_required(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_recognized = False
        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['captcha.required'],
            **self.get_expected_response_values(csrf_token=TEST_CSRF_TOKEN)
        )


class BaseConfirmCommitTestCase(BaseConfirmTestCase):
    method = None

    def setUp(self):
        super(BaseConfirmCommitTestCase, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.retpath = TEST_RETPATH
            track.origin = TEST_ORIGIN
            track.authorization_session_policy = 'sessional'

    def check_track_ok(self, uid=TEST_UID, allow_authorization=True, password_verified=True, **kwargs):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(uid))
        eq_(track.retpath, TEST_RETPATH)
        eq_(track.authorization_session_policy, 'sessional')
        eq_(track.allow_authorization, allow_authorization)
        if allow_authorization:
            ok_(track.dont_change_default_uid)
        ok_(not track.allow_oauth_authorization)
        eq_(track.password_verification_passed_at, TimeNow() if password_verified else None)
        for key, value in kwargs.items():
            actual = getattr(track, key)
            eq_(
                actual,
                value,
                'track_field=%s expected=%s actual=%s' % (key, value, actual),
            )

    def check_statbox_ok(self, uid=TEST_UID):
        self.assert_statbox_logged([
            self.env.statbox.entry(
                'confirmed',
                method=self.method,
                uid=str(uid),
            ),
        ])


@with_settings_hosts(
    PWNED_PASSWORD_CHANGE_DENOMINATOR=1,
    PASSWORD_PWN_CHECK_SUSPENSION_DAYS=2,
)
class TestConfirmCommitWithPassword(BaseConfirmCommitTestCase):
    default_url = '/1/bundle/auth/password/confirm/commit_password/?consumer=dev'
    http_query_args = {
        'password': 'long_password',
    }
    method = 'password'

    def setUp(self):
        super(TestConfirmCommitWithPassword, self).setUp()
        self.http_query_args.update(track_id=self.track_id)

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values()
        )
        self.check_track_ok()
        self.check_statbox_ok()

    def test_ok_for_pdd(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                subscribed_to=[102],
                crypt_password='1:pwd',
                dbfields={
                    'userinfo_safe.hintq.uid': u'99:вопрос',
                    'userinfo_safe.hinta.uid': u'ответ',
                },
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                domain={
                    'punycode': TEST_DOMAIN,
                    'unicode': TEST_DOMAIN,
                },
            )
        )
        self.check_track_ok(uid=TEST_PDD_UID)
        self.check_statbox_ok(uid=TEST_PDD_UID)

    def test_auth_already_passed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = 'session'

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['account.auth_passed'],
            track_id=self.track_id,
        )
        self.check_statbox_empty()

    def test_password_weak_for_sid_67(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                subscribed_to=[67],
                dbfields={
                    'password_quality.quality.uid': 10,
                },
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values(
                state='change_password',
                change_password_reason='password_weak',
                validation_method=None,
            )
        )
        self.check_track_ok(allow_authorization=False)
        self.assert_statbox_logged([
            self.env.statbox.entry(
                'change_password',
                is_weak='1',
            ),
        ])

    def test_password_short_for_sid_67(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                subscribed_to=[67],
                dbfields={
                    'password_quality.quality.uid': 90,
                },
            ),
        )

        rv = self.make_request(query_args={'password': 'weak'})
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values(
                state='change_password',
                change_password_reason='password_weak',
                validation_method=None,
            )
        )
        self.check_track_ok(allow_authorization=False)

    def test_password_is_pwned(self):
        password = b'password'
        self.http_query_args.update(password=password)
        encrypted_password = hashlib.sha1(password).hexdigest()

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:{}'.format(encrypted_password),
                dbfields={
                    'password_quality.quality.uid': 10,
                },
            ),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password_no_postfix(encrypted_password.upper())),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values(
                state='change_password',
                change_password_reason='password_pwned',
                validation_method=None,
            )
        )

        self.assert_statbox_logged([
            self.env.statbox.entry(
                'change_password',
                action='redirect_to_password_change',
                mode='change_pwned_password',
                is_pwned='1',
                is_weak='1',
                is_experiment_enabled='1',
                sms_2fa_on='0',
                is_no_change_password_pdd='0',
                is_pwn_check_suspended='0',
            ),
            self.env.statbox.entry(
                'account_password_changing_required',
                consumer='dev',
            )
        ])

        track = self.track_manager.read(self.track_id)
        eq_(
            track.submit_response_cache,
            dict(
                self.get_expected_response_values(
                    state='change_password',
                    change_password_reason='password_pwned',
                    validation_method=None,
                ),
                status='ok',

            ),
        )

        self.env.db.check_db_attr(TEST_UID, 'password.forced_changing_reason', PASSWORD_CHANGING_REASON_PWNED)
        eq_(len(self.env.shakur.requests), 1)

    def test_scholar_with_pwned_password_ok(self):
        password = b'password'
        self.http_query_args.update(password=password)
        encrypted_password = hashlib.sha1(password).hexdigest()

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                aliases={
                    'scholar': TEST_LOGIN,
                },
                crypt_password='1:{}'.format(encrypted_password),
                dbfields={
                    'password_quality.quality.uid': 10,
                },
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values()
        )
        self.check_track_ok()
        self.check_statbox_ok()
        eq_(len(self.env.shakur.requests), 0)

    def test_pwned_check_suspension(self):
        password = b'password'
        self.http_query_args.update(password=password)
        encrypted_password = hashlib.sha1(password).hexdigest()

        significantly_less_than_2_days_ago = int(time.time()) - 24 * 3600 * 2 + 1000
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:{}'.format(encrypted_password),
                dbfields={
                    'password_quality.quality.uid': 50,
                },
                attributes={
                    'password.pwn_forced_changing_suspended_at': significantly_less_than_2_days_ago,
                }
            ),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.get_expected_response_values()
        )
        self.check_track_ok()
        self.assert_statbox_logged([
            self.env.statbox.entry(
                'change_password',
                action='no_action',
                mode='change_pwned_password',
                is_weak='0',
                is_pwned='0',
                is_experiment_enabled='0',
                sms_2fa_on='0',
                is_no_change_password_pdd='0',
                is_pwn_check_suspended='1',
            ),
            self.env.statbox.entry(
                'confirmed',
                method=self.method,
                uid=str(TEST_UID),
            ),
        ])

        eq_(len(self.env.shakur.requests), 0)

    def test_pwned_check_suspension_expired(self):
        password = b'password'
        self.http_query_args.update(password=password)
        encrypted_password = hashlib.sha1(password).hexdigest()

        more_than_2_days_ago = int(time.time()) - 24 * 3600 * 2 - 1
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:{}'.format(encrypted_password),
                dbfields={
                    'password_quality.quality.uid': 10,
                },
                attributes={
                    'password.pwn_forced_changing_suspended_at': more_than_2_days_ago,
                }
            ),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password_no_postfix(encrypted_password.upper())),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values(
                state='change_password',
                change_password_reason='password_pwned',
                validation_method=None,
            )
        )

        self.assert_statbox_logged([
            self.env.statbox.entry(
                'change_password',
                action='redirect_to_password_change',
                mode='change_pwned_password',
                is_pwned='1',
                is_weak='1',
                is_experiment_enabled='1',
                sms_2fa_on='0',
                is_no_change_password_pdd='0',
                is_pwn_check_suspended='0',
            ),
            self.env.statbox.entry(
                'account_password_changing_required',
                consumer='dev',
            )
        ])

        track = self.track_manager.read(self.track_id)
        eq_(
            track.submit_response_cache,
            dict(
                self.get_expected_response_values(
                    state='change_password',
                    change_password_reason='password_pwned',
                    validation_method=None,
                ),
                status='ok',

            ),
        )

        self.env.db.check_db_attr(TEST_UID, 'password.forced_changing_reason', PASSWORD_CHANGING_REASON_PWNED)
        eq_(len(self.env.shakur.requests), 1)

    def test_password_is_pwned_with_sms_2fa_on(self):
        password = b'password'
        self.http_query_args.update(password=password)
        encrypted_password = hashlib.sha1(password).hexdigest()

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                attributes={
                    'account.sms_2fa_on': '1',
                },
                crypt_password='1:{}'.format(encrypted_password),
                dbfields={
                    'password_quality.quality.uid': 10,
                },
            ),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password_no_postfix(encrypted_password.upper())),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values()
        )

        self.assert_statbox_logged([
            self.env.statbox.entry(
                'change_password',
                action='no_action',
                mode='change_pwned_password',
                is_weak='1',
                is_pwned='1',
                is_experiment_enabled='1',
                sms_2fa_on='1',
                is_no_change_password_pdd='0',
                is_pwn_check_suspended='0',
            ),
            self.env.statbox.entry(
                'confirmed',
                method=self.method,
                uid=str(TEST_UID),
            ),
        ])

        eq_(len(self.env.shakur.requests), 1)

    def test_password_is_pwned_with_whitelist_login(self):
        self.http_query_args.update(password=TEST_NOT_STRONG_PASSWORD)
        encrypted_password = hashlib.sha1(TEST_NOT_STRONG_PASSWORD).hexdigest()

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login='yndx-miss-shakur111',
                crypt_password='1:{}'.format(encrypted_password),
                dbfields={
                    'password_quality.quality.uid': TEST_NOT_STRONG_PASSWORD_QUALITY,
                },
            ),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password_no_postfix(encrypted_password)),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values(
                login='yndx-miss-shakur111',
                display_login='yndx-miss-shakur111',
            )
        )

        self.assert_statbox_logged([
            self.env.statbox.entry(
                'change_password',
                action='no_action',
                mode='change_pwned_password',
                is_weak='0',
                is_pwned='0',
                is_experiment_enabled='0',
                sms_2fa_on='0',
                is_no_change_password_pdd='0',
                is_pwn_check_suspended='0',
            ),
            self.env.statbox.entry(
                'confirmed',
                method=self.method,
                uid=str(TEST_UID),
            ),
        ])

        eq_(len(self.env.shakur.requests), 0)

    def test_password_is_not_pwned(self):
        self.http_query_args.update(password=TEST_NOT_STRONG_PASSWORD)
        encrypted_password = hashlib.sha1(TEST_NOT_STRONG_PASSWORD).hexdigest()

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:{}'.format(encrypted_password),
                dbfields={
                    'password_quality.quality.uid': TEST_NOT_STRONG_PASSWORD_QUALITY,
                },
            ),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.get_expected_response_values()
        )
        self.check_track_ok()
        self.assert_statbox_logged([
            self.env.statbox.entry(
                'change_password',
                action='no_action',
                mode='change_pwned_password',
                is_weak='0',
                is_experiment_enabled='0',
                sms_2fa_on='0',
                is_no_change_password_pdd='0',
                is_pwn_check_suspended='0',
            ),
            self.env.statbox.entry(
                'confirmed',
                method=self.method,
                uid=str(TEST_UID),
            ),
        ])

        eq_(len(self.env.shakur.requests), 1)

    def test_password_shakur_temporary_error_ok(self):
        self.env.shakur.set_response_side_effect(
            'check_password',
            ShakurTemporaryError,
        )

        with settings_context(
            SHAKUR_RETRIES=2,
        ):
            rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.get_expected_response_values()
        )
        self.check_track_ok()
        self.check_statbox_ok()

        eq_(len(self.env.shakur.requests), 2)

    def test_password_change_required(self):
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password='1:pwd',
            dbfields={'subscription.login_rule.8': 4},
            attributes={
                'password.forced_changing_reason': '1',
            },
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**account_kwargs),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.get_expected_response_values(
                state='change_password',
                change_password_reason='account_hacked',
                validation_method='captcha',
            )
        )
        self.check_track_ok(
            secure_phone_number=TEST_PHONE_NUMBER.e164,
            can_use_secure_number_for_password_validation=True,
            allow_authorization=False,
        )

        # Проверяем вызовы Я.смс
        requests = self.env.yasms.requests
        eq_(len(requests), 0)

        self.env.blackbox.requests[0].assert_post_data_contains({
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

    def test_captcha_required(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['captcha.required'],
            track_id=self.track_id,
        )

    def test_use_blackbox_status_from_track(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
            ),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.blackbox_login_status = BLACKBOX_LOGIN_VALID_STATUS
            track.blackbox_password_status = BLACKBOX_PASSWORD_VALID_STATUS

        resp = self.make_request(exclude_args=['password'])
        self.assert_ok_response(
            resp,
            **self.get_expected_response_values()
        )

        eq_(len(self.env.blackbox.requests), 1)
        self.env.blackbox.requests[0].assert_post_data_contains({'method': 'userinfo'})

    def test_blackbox_status_from_track_not_used(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.blackbox_login_status = BLACKBOX_LOGIN_VALID_STATUS
            track.blackbox_password_status = BLACKBOX_PASSWORD_VALID_STATUS

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.get_expected_response_values()
        )

        eq_(len(self.env.blackbox.requests), 1)
        self.env.blackbox.requests[0].assert_post_data_contains({'method': 'login'})

    def test_rfc_2fa(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
                allowed_second_steps=[BLACKBOX_SECOND_STEP_RFC_TOTP],
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.get_expected_response_values(
                state='rfc_totp',
            )
        )
        self.check_track_ok(
            allow_authorization=False,
            is_second_step_required=True,
            password_verified=False,
        )

    def test_integrational(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
            ),
        )

        # Пытаемся сделать запрос без пароля
        rv = self.make_request(exclude_args=['password'])
        self.assert_error_response(
            rv,
            ['password.not_matched'],
            track_id=self.track_id,
        )

        # Вводим "неправильный" пароль
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        )
        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['password.not_matched'],
            track_id=self.track_id,
        )

        for _ in range(2):
            # Вводим ещё один "неправильный" пароль, получаем капчу от ЧЯ
            self.env.blackbox.set_blackbox_response_value(
                'login',
                blackbox_login_response(
                    password_status=BLACKBOX_PASSWORD_BAD_STATUS,
                    bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
                ),
            )
            rv = self.make_request()
            self.assert_error_response(
                rv,
                ['captcha.required'],
                track_id=self.track_id,
            )

            # "Разгадываем" капчу и делаем ещё один запрос (без пароля)
            with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
                track.is_captcha_checked = True
                track.is_captcha_recognized = True

            rv = self.make_request(exclude_args=['password'])
            self.assert_error_response(
                rv,
                ['password.not_matched'],
                track_id=self.track_id,
            )

        # Вспоминаем "правильный" пароль
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
            ),
        )
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values()
        )
        self.check_track_ok()


class TestConfirmCommitWithMagic(BaseConfirmCommitTestCase):
    default_url = '/1/bundle/auth/password/confirm/commit_magic/?consumer=dev'
    http_query_args = {
        'csrf_token': TEST_CSRF_TOKEN,
    }
    method = 'magic'

    def setUp(self):
        super(TestConfirmCommitWithMagic, self).setUp()
        self.http_query_args.update(track_id=self.track_id)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = True
            track.login = TEST_LOGIN
            track.otp = 'otp'
            track.csrf_token = TEST_CSRF_TOKEN

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values()
        )
        self.check_track_ok()
        self.check_statbox_ok()

    def test_csrf_token_invalid(self):
        rv = self.make_request(query_args={'csrf_token': 'foo'})
        self.assert_error_response(
            rv,
            ['csrf_token.invalid'],
            track_id=self.track_id,
        )
        self.check_statbox_empty()

    def test_auth_already_passed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = 'session'

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['account.auth_passed'],
            track_id=self.track_id,
        )
        self.check_statbox_empty()

    def test_non_magic_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = False

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['track.invalid_state'],
            track_id=self.track_id,
        )
        self.check_statbox_empty()

    def test_invalid_track_state(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = TEST_LOGIN
            track.otp = None

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['track.invalid_state'],
            track_id=self.track_id,
        )
        self.check_statbox_empty()

    def test_auth_not_ready(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = None
            track.otp = None

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            state='otp_auth_not_ready',
            track_id=self.track_id,
        )
        self.check_statbox_empty()

    def test_account_changed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login_required_for_magic = TEST_PDD_LOGIN

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['account.changed'],
            track_id=self.track_id,
        )
        self.check_statbox_empty()

    def test_login_normalization(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'test.login'
            track.login_required_for_magic = 'test-login'

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values()
        )

    def test_wrong_pin(self):
        login_response = blackbox_login_response(
            password_status=BLACKBOX_PASSWORD_BAD_STATUS,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['password.not_matched'],
            track_id=self.track_id,
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.login is None)
        ok_(track.otp is None)

    def test_use_blackbox_status_from_track(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
            ),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.blackbox_login_status = BLACKBOX_LOGIN_VALID_STATUS
            track.blackbox_password_status = BLACKBOX_PASSWORD_VALID_STATUS

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.get_expected_response_values()
        )

        eq_(len(self.env.blackbox.requests), 1)
        self.env.blackbox.requests[0].assert_post_data_contains({'method': 'userinfo'})

    def test_integrational(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )

        # Вводим "неправильный" пин, сканируем QR-код, получаем капчу от ЧЯ
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
                bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )
        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['captcha.required'],
            track_id=self.track_id,
        )

        # "Разгадываем" капчу и делаем ещё один запрос - узнаём, что пароль неверен
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['password.not_matched'],
            track_id=self.track_id,
        )

        # Делаем ещё один запрос
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            state='otp_auth_not_ready',
            track_id=self.track_id,
        )

        # Вновь сканируем QR-код, уже с правильным пином
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = TEST_LOGIN
            track.otp = 'otp'

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.get_expected_response_values()
        )
        self.check_track_ok()
