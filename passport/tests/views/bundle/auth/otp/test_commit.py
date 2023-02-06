# -*- coding: utf-8 -*-
import json
import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.authorization import AUTHORIZATION_SESSION_POLICY_SESSIONAL
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    EXPECTED_L_COOKIE,
    EXPECTED_LAH_COOKIE,
    EXPECTED_MDA2_BEACON_COOKIE,
    EXPECTED_SESSGUARD_COOKIE,
    EXPECTED_SESSIONID_COOKIE,
    EXPECTED_SESSIONID_SECURE_COOKIE,
    EXPECTED_YANDEX_LOGIN_COOKIE,
    EXPECTED_YP_COOKIE,
    EXPECTED_YS_COOKIE,
    MDA2_BEACON_VALUE,
    SESSION,
    TEST_AUTH_ID,
    TEST_CLEANED_PDD_RETPATH,
    TEST_COOKIE_AGE,
    TEST_COOKIE_TIMESTAMP,
    TEST_HOST,
    TEST_IP,
    TEST_LOGIN,
    TEST_OLD_AUTH_ID,
    TEST_PDD_LOGIN,
    TEST_PDD_RETPATH,
    TEST_PDD_UID,
    TEST_PHONE_NUMBER,
    TEST_REFERER,
    TEST_RETPATH,
    TEST_RETPATH_HOST,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_YANDEXUID_COOKIE,
)
from passport.backend.api.views.bundle.constants import X_TOKEN_OAUTH_SCOPE
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_hosted_domains_response,
    blackbox_login_response,
    blackbox_sessionid_multi_response,
    blackbox_sign_response,
    blackbox_userinfo_response,
)
from passport.backend.core.historydb.entry import AuthEntry
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    check_all_url_params_match,
    check_url_contains_params,
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)


TEST_OTP = 'abcd efgh'
TEST_CSRF_TOKEN = '708ab6a91d336ba09b5aa1cec5bde098'
TEST_OAUTH_X_TOKEN = 'x-token'
TEST_OAUTH_HEADER = 'OAuth %s' % TEST_OAUTH_X_TOKEN
TEST_OAUTH_SCOPE = X_TOKEN_OAUTH_SCOPE


eq_ = iterdiff(eq_)


class BaseOtpAuthCommitTestCase(BaseBundleTestViews):

    def setUp(self):
        self.patches = []

        self.setup_cookie_mocks()

        self.start_patches()

        self.setup_env()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['auth']}))

        self.default_headers = self.get_headers()

        self.setup_trackid_generator()
        self.setup_track()

        self.setup_blackbox_responses(self.env)
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        self.stop_patches()
        del self.patches
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.build_cookies_yx
        del self.build_cookie_l
        del self.build_cookie_lah

    def get_headers(self, host=None, user_ip=None, cookie=None):
        return mock_headers(
            host=host or TEST_HOST,
            user_agent=TEST_USER_AGENT,
            cookie=cookie or 'Session_id=0:old-session; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            user_ip=user_ip or TEST_IP,
            referer=TEST_REFERER,
        )

    def get_base_query_params(self):
        return {
            'track_id': self.track_id,
            'csrf_token': TEST_CSRF_TOKEN,
        }

    def query_params(self, exclude=None, **kwargs):
        base_params = self.get_base_query_params()
        if exclude:
            for key in exclude:
                if key in base_params:
                    del base_params[key]
        return merge_dicts(base_params, kwargs)

    def make_request(self, data, headers):
        return self.env.client.post(
            '/2/bundle/auth/otp/commit/?consumer=dev',
            data=data,
            headers=headers,
        )

    def setup_statbox_templates(self):

        self.env.statbox.bind_base(
            user_agent=TEST_USER_AGENT,
            ip=TEST_IP,
            yandexuid=TEST_YANDEXUID_COOKIE,
            track_id=self.track_id,
            type='otp',
            mode='any_auth',
        )
        self.env.statbox.bind_entry(
            'failed_auth',
            action='failed_auth',
        )
        self.env.statbox.bind_entry(
            'captcha_failed',
            _exclude=['type'],
            action='captcha_failed',
        )
        self.env.statbox.bind_entry(
            'cookie_set',
            _exclude=['type'],
            person_country='ru',
            ip_country='us',
            input_login=TEST_LOGIN,
            is_2fa_enabled='1',
            authid=TEST_AUTH_ID,
            ip=TEST_IP,
        )
        self.env.statbox.bind_entry(
            'otp_auth_finished',
            action='otp_auth_finished',
        )

        self.env.statbox.bind_entry(
            'subscription_added',
            _exclude=['yandexuid', 'type', 'track_id', 'mode'],
            entity='subscriptions',
            operation='added',
            event='account_modification',
            consumer='-',
        )

    def base_track(self):
        return dict(
            otp=TEST_OTP,
            login=TEST_LOGIN,
            is_allow_otp_magic=True,
            csrf_token=TEST_CSRF_TOKEN,
        )

    def base_auth_log_entries(self):
        return {
            'login': TEST_LOGIN,
            'type': authtypes.AUTH_TYPE_WEB,
            'status': '',
            'uid': str(TEST_UID),
            'useragent': TEST_USER_AGENT,
            'yandexuid': TEST_YANDEXUID_COOKIE,
            'comment': 'aid=%s;ttl=0' % TEST_AUTH_ID,
            'ip_from': TEST_IP,
            'client_name': 'passport',
        }

    def build_auth_log_entries(self, **kwargs):
        entries = self.base_auth_log_entries()
        entries.update(kwargs)
        return entries.items()

    def assert_track_ok(self, **kwargs):
        """Трек заполнен полностью и корректно"""
        params = self.base_track()
        params.update(kwargs)
        track = self.track_manager.read(self.track_id)
        for attr_name, expected_value in params.items():
            actual_value = getattr(track, attr_name)
            eq_(actual_value, expected_value, [attr_name, actual_value, expected_value])

    def assert_track_empty(self):
        """Трек пуст в случае какой-либо ошибки"""
        track = self.track_manager.read(self.track_id)
        for attr_name in self.base_track().keys():
            self.assertIsNone(getattr(track, attr_name))

    def assert_successful_auth_recorded_to_statbox(self, uid=TEST_UID, ttl=0, captcha_passed=False,
                                                   auth_args=None, additional_entries=None, type_='otp',
                                                   auth_exclude=None, finished_exclude=None,
                                                   with_check_cookies=False):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry(
                'cookie_set',
                _exclude=auth_exclude or [],
                captcha_passed=tskv_bool(captcha_passed),
                ttl=str(ttl),
                uid=str(uid),
                is_2fa_enabled='1',
                **(auth_args or {})
            ),
            self.env.statbox.entry(
                'otp_auth_finished',
                _exclude=finished_exclude,
                uid=str(uid),
                type=type_,
                is_2fa_enabled='1',
                password_like_otp='1',
            ),
        ])

        if additional_entries:
            entries += additional_entries

        self.env.statbox.assert_has_written(entries)
        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ["auth_2fa.rps"],
            {"auth_2fa.rps.total_dmmm": 1}
        )

    def get_expected_cookies(self, with_lah=True, with_sessguard=False):
        cookies = [
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_SESSIONID_SECURE_COOKIE,
            EXPECTED_YANDEX_LOGIN_COOKIE,
            EXPECTED_YP_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_L_COOKIE,
            EXPECTED_MDA2_BEACON_COOKIE,
        ]
        if with_lah:
            cookies.append(EXPECTED_LAH_COOKIE)
        if with_sessguard:
            cookies.append(EXPECTED_SESSGUARD_COOKIE)
        return sorted(cookies)

    def _get_expected_response(self, status='ok', state=None, cookies=None,
                               retpath=None, uid=TEST_UID,
                               login=TEST_LOGIN, accounts=None, display_login=None,
                               **kwargs):
        expected = {
            'status': status,
            'track_id': self.track_id,
            'account': {
                'uid': uid,
                'login': login,
                # Этот хардкод отсылает нас к `passport.test.blackbox.py:_blackbox_userinfo`
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
            'retpath': retpath,
        }
        if cookies:
            expected.update(
                cookies=cookies,
                default_uid=uid,
            )
        if state:
            expected.update(state=state)
        if accounts:
            expected['accounts'] = accounts
        expected.update(kwargs)
        return expected

    def get_expected_response(self, *args, **kwargs):
        return self._get_expected_response(*args, **kwargs)

    def assert_response_ok(self, response, is_2fa_enabled_yp=True, **kwargs):
        eq_(response.status_code, 200, [response.status_code, response.data])
        expected_response = self.get_expected_response(**kwargs)
        actual_response = json.loads(response.data)
        if 'cookies' in actual_response:
            actual_response['cookies'] = sorted(actual_response['cookies'])
        eq_(actual_response, expected_response)
        # Проверим, что при построении куки yp передали флаг включенности 2fa
        if is_2fa_enabled_yp:
            eq_(self.build_cookies_yx.call_args_list[0][1]['is_2fa_enabled_yp'], is_2fa_enabled_yp)

    def not_authorized(self):
        """Логгер авторизации не вызывался - пользователю не создавалась новая сессия"""
        eq_(self.env.auth_handle_mock.call_count, 0)

    def setup_env(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def setup_trackid_generator(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)
        self.patches.append(self.track_id_generator)

    def setup_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = True
            track.otp = TEST_OTP
            track.login = TEST_LOGIN
            track.authorization_session_policy = 'long'
            track.csrf_token = TEST_CSRF_TOKEN

    def setup_cookie_mocks(self):
        self.build_cookies_yx = mock.Mock(return_value=[EXPECTED_YP_COOKIE, EXPECTED_YS_COOKIE])
        self.build_cookie_l = mock.Mock(return_value=EXPECTED_L_COOKIE)
        self.build_cookie_lah = mock.Mock(return_value=EXPECTED_LAH_COOKIE)

        self.patches.extend([
            mock.patch(
                'passport.backend.api.common.authorization.build_cookies_yx',
                self.build_cookies_yx,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_l',
                self.build_cookie_l,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_lah',
                self.build_cookie_lah,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
        ])

    def setup_blackbox_responses(self, env):
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            **deep_merge(
                dict(attributes={
                    'account.2fa_on': '1',
                }),
                build_phone_secured(
                    1,
                    TEST_PHONE_NUMBER.e164,
                )
            )
        )

        env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
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
        env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
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
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            **deep_merge(
                dict(attributes={
                    'account.2fa_on': '1',
                }),
                build_phone_secured(
                    1,
                    TEST_PHONE_NUMBER.e164,
                )
            )
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

    def assert_blackbox_createsession_called(self, call_index=1, ttl='5', check_password=True, extra_guard_host=None):
        guard_hosts = ['passport-test.yandex.ru']
        if extra_guard_host is not None:
            guard_hosts.append(extra_guard_host)
        kwargs = {
            'have_password': '1',
            'method': 'createsession',
            'is_lite': '0',
            'ttl': ttl,
            'ver': '3',
            'uid': str(TEST_UID),
            'lang': '1',
            'format': 'json',
            'keyspace': 'yandex.ru',
            'userip': TEST_IP,
            'host_id': '7f',
            'create_time': TimeNow(),
            'auth_time': TimeNow(as_milliseconds=True),
            'guard_hosts': ','.join(guard_hosts),
            'request_id': mock.ANY,
            'get_login_id': 'yes',
        }
        if check_password:
            kwargs.update({
                'password_check_time': TimeNow(),
            })
        check_all_url_params_match(
            self.env.blackbox._mock.request.call_args_list[call_index][0][1],
            kwargs,
        )

    def assert_blackbox_sessionid_called(self, call_index=1):
        check_url_contains_params(
            self.env.blackbox._mock.request.call_args_list[call_index][0][1],
            {
                'method': 'sessionid',
                'sessionid': '0:old-session',
            },
        )

    def assert_blackbox_login_called(self, call_index=0, retpath=None, service=None):
        if service is None:
            service = 'passport'
        login_data = self.env.blackbox._mock.request.call_args_list[call_index][0][2]
        eq_(login_data['method'], 'login')
        eq_(login_data['authtype'], authtypes.AUTH_TYPE_WEB)
        eq_(login_data['yandexuid'], TEST_YANDEXUID_COOKIE)
        eq_(login_data['from'], service)
        if retpath:
            eq_(login_data['xretpath'], retpath)
        eq_(login_data['userip'], TEST_IP)
        eq_(login_data['login'], TEST_LOGIN)
        eq_(login_data['password'], TEST_OTP)

    def assert_blackbox_userinfo_called(self):
        self.env.blackbox.requests[0].assert_post_data_contains(
            {
                'method': 'userinfo',
                'uid': str(TEST_UID),
                'format': 'json',
            },
        )

    def assert_blackbox_sign_sessguard_called(self):
        request = self.env.blackbox.get_requests_by_method('sign')[0]
        sessguard_cookie = 'sessguard=1.sessguard; Domain=.%s; Secure; HttpOnly; Path=/' % TEST_RETPATH_HOST
        request.assert_query_equals(
            {
                'format': 'json',
                'method': 'sign',
                'sign_space': 'sessguard_container',
                'ttl': '60',
                'value': json.dumps({
                    'cookies': [sessguard_cookie],
                    'retpath': TEST_RETPATH,
                }),
            },
        )

    def assert_phone_logged(self, uid=TEST_UID, phone=TEST_PHONE_NUMBER.e164,
                            yandexuid=TEST_YANDEXUID_COOKIE):
        self.env.phone_logger.assert_has_written([
            self.env.phone_logger.get_log_entry(uid, phone, yandexuid),
        ])

    def start_patches(self):
        """Запускаем mocks"""
        for patch in self.patches:
            patch.start()

    def stop_patches(self):
        """
        Здесь мы останавливаем все зарегистрированные ранее mocks
        """
        for patch in self.patches:
            patch.stop()


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    YABS_URL='localhost',
    DISABLE_FAILED_CAPTCHA_LOGGING=False,
    PASSPORT_SUBDOMAIN='passport-test',
)
class OtpAuthCommitTestCase(BaseOtpAuthCommitTestCase):

    def test_without_track_id_error(self):
        resp = self.make_request(
            self.query_params(track_id=''),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'errors': ['track_id.empty'],
            },
        )

    def test_no_magic_track_error(self):
        """Пришли с треком, не предназначенным для магической отп-авторизации"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = False
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['track.invalid_state'],
            },
        )

    def test_magic_auth_already_passed_error(self):
        """Пришли с треком, на котором уже случилась магическая авторизация"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '0:session'
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['account.auth_passed'],
            },
        )

    def test_password_auth_already_passed_error(self):
        """Пришли с треком, на котором уже случилась авторизация по паролю"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '0:session'
            track.otp = ''
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['account.auth_passed'],
            },
        )

    def test_invalid_track_state_error(self):
        """Пришли с треком, в котором не записали логин или отп"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = ''
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['track.invalid_state'],
            },
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.otp = ''
            track.login = TEST_LOGIN
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['track.invalid_state'],
            },
        )

    def test_auth_not_ready(self):
        """Пришли с треком, в котором eще не записали логин и отп"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.otp = ''
            track.login = ''
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'ok',
                'track_id': self.track_id,
                'state': 'otp_auth_not_ready',
            },
        )
        self.not_authorized()

    def test_account_disabled_error(self):
        """Проверили авторизацию, но ЧЯ сказал, что аккаунт заблокирован"""
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                login_status=blackbox.BLACKBOX_LOGIN_DISABLED_STATUS,
            ),
        )
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['account.disabled'],
            },
        )
        self.assert_blackbox_login_called()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed_auth',
                uid=str(TEST_UID),
                login_status=blackbox.BLACKBOX_LOGIN_DISABLED_STATUS,
                password_status=blackbox.BLACKBOX_PASSWORD_VALID_STATUS,
            ),
        ])
        self.not_authorized()

    def test_account_disabled_on_deletion_error(self):
        """Проверили авторизацию, но ЧЯ сказал, что аккаунт заблокирован"""
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                login_status=blackbox.BLACKBOX_LOGIN_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['account.disabled_on_deletion'],
            },
        )
        self.assert_blackbox_login_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed_auth',
                uid=str(TEST_UID),
                login_status=blackbox.BLACKBOX_LOGIN_DISABLED_STATUS,
                password_status=blackbox.BLACKBOX_PASSWORD_VALID_STATUS,
            ),
        ])
        self.not_authorized()

    def test_blackbox_unknown_error(self):
        """Проверили авторизацию, но ЧЯ сказал unknown erorr"""
        for params in (
            dict(login_status=blackbox.BLACKBOX_LOGIN_UNKNOWN_STATUS),
            dict(password_status=blackbox.BLACKBOX_PASSWORD_UNKNOWN_STATUS),
        ):
            self.env.blackbox.set_blackbox_response_value(
                'login',
                blackbox_login_response(**params),
            )
            resp = self.make_request(
                self.query_params(),
                self.get_headers(),
            )
            eq_(resp.status_code, 200)
            resp = json.loads(resp.data)
            eq_(
                resp,
                {
                    'status': 'error',
                    'track_id': self.track_id,
                    'errors': ['backend.blackbox_failed'],
                },
            )
            self.assert_blackbox_login_called()
            self.not_authorized()
            # Удостоверимся, что не кешируем такой ответ ЧЯ
            track = self.track_manager.read(self.track_id)
            ok_(track.blackbox_login_status is None)
            ok_(track.blackbox_password_status is None)

    def test_account_not_found_error(self):
        """Проверили авторизацию, но ЧЯ сказал, что аккаунт не найден"""
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                login_status=blackbox.BLACKBOX_LOGIN_NOT_FOUND_STATUS,
            ),
        )
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['account.not_found'],
            },
        )
        self.assert_blackbox_login_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed_auth',
                login_status=blackbox.BLACKBOX_LOGIN_NOT_FOUND_STATUS,
                password_status=blackbox.BLACKBOX_PASSWORD_VALID_STATUS,
            ),
        ])
        self.not_authorized()

    def test_password_not_mached_error(self):
        """Проверили авторизацию, но otp не подошел"""
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        )
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['password.not_matched'],
            },
        )
        self.assert_blackbox_login_called()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed_auth',
                uid=str(TEST_UID),
                login_status=blackbox.BLACKBOX_LOGIN_VALID_STATUS,
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        ])
        self.not_authorized()

    def test_no_blackbox_login_call_on_errors(self):
        """
        Проверим, что для случаев, когда аккаунт не найден, заблокирован или
        не подошел пароль, мы не ходим второй раз method=login в ЧЯ,
        а пользуемся знанием из трека.
        """
        for login_status, password_status, error_code in (
                (
                    blackbox.BLACKBOX_LOGIN_VALID_STATUS,
                    blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
                    'password.not_matched',  # Здесь еще придет информация о пользователе
                ),
                (
                    blackbox.BLACKBOX_LOGIN_DISABLED_STATUS,
                    '',
                    'account.disabled',
                ),
                (
                    blackbox.BLACKBOX_LOGIN_NOT_FOUND_STATUS,
                    '',
                    'account.not_found',
                ),
        ):
            with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
                track.blackbox_login_status = login_status
                track.blackbox_password_status = password_status
                if login_status != blackbox.BLACKBOX_LOGIN_NOT_FOUND_STATUS:
                    track.uid = TEST_UID

            resp = self.make_request(
                self.query_params(),
                self.get_headers(),
            )
            eq_(resp.status_code, 200)
            resp = json.loads(resp.data)
            eq_(resp['status'], 'error')
            eq_(resp['track_id'], self.track_id)
            eq_(resp['errors'], [error_code])
            # FIXME: по-хорошему нужно ходить в ЧЯ один раз
            bb_call_count = 2 if error_code == 'password.not_matched' else 1
            eq_(self.env.blackbox._mock.request.call_count, bb_call_count)
            self.not_authorized()
            self.env.blackbox._mock.request.reset_mock()

    def test_bad_password_captcha_is_required__error(self):
        """ЧЯ сказал, что нужна капча при неправильном пароле"""
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
                bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )

        resp = self.make_request(self.query_params(), self.get_headers())
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['captcha.required'],
            },
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(not track.is_captcha_recognized)
        eq_(track.blackbox_login_status, blackbox.BLACKBOX_LOGIN_VALID_STATUS)
        eq_(track.blackbox_password_status, blackbox.BLACKBOX_PASSWORD_BAD_STATUS)
        eq_(track.bruteforce_status, blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed_auth',
                uid=str(TEST_UID),
                bruteforce=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
                login_status=blackbox.BLACKBOX_LOGIN_VALID_STATUS,
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        ])
        self.not_authorized()
        self.assert_blackbox_login_called()

    def test_captcha_is_required_for_valid_password__error(self):
        """ЧЯ сказал, что нужна капча при правильном пароле"""
        login_response = blackbox_login_response(
            bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.get_headers())
        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['captcha.required'],
            },
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(not track.is_captcha_recognized)
        eq_(track.blackbox_login_status, blackbox.BLACKBOX_LOGIN_VALID_STATUS)
        eq_(track.blackbox_password_status, blackbox.BLACKBOX_PASSWORD_VALID_STATUS)
        eq_(track.uid, str(TEST_UID))

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed_auth',
                uid=str(TEST_UID),
                bruteforce=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
                login_status=blackbox.BLACKBOX_LOGIN_VALID_STATUS,
                password_status=blackbox.BLACKBOX_PASSWORD_VALID_STATUS,
            ),
        ])
        self.not_authorized()
        self.assert_blackbox_login_called()

    def test_captcha_is_required_in_track__error(self):
        """В треке записано что нужна капча, но она не была пройдена"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = False
            track.bruteforce_status = 'captcha'

        resp = self.make_request(self.query_params(), self.get_headers())
        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['captcha.required'],
            },
        )
        self.not_authorized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('captcha_failed'),
        ])

    def test_account_global_logout_after_track_created_ok(self):
        """
        Магически авторизуем пользователя, на пользователя поставили глобал логаут
        после того, как был создан магический трек. Авторизуем успешно, т.к.
        магическая отп-авторизация равносильна авторизации по предьявлению
        логина-пароля в метод login ЧЯ.
        """
        login_response = blackbox_login_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            **deep_merge(
                dict(attributes={
                    'account.2fa_on': '1',
                    'account.global_logout_datetime': str(int(time.time()) + 1),
                }),
                build_phone_secured(
                    1,
                    TEST_PHONE_NUMBER.e164,
                )
            )
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            state='otp_auth_finished',
            accounts=[self.get_account_info()],
        )

    def test_ok_with_retpath(self):
        """
        Все проходит хорошо, кук не было, выписываем новые куки через createsession.
        А так же в треке есть retpath
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_track_ok(
            session=SESSION['session']['value'],
        )
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            state='otp_auth_finished',
            retpath=TEST_RETPATH,
            accounts=[self.get_account_info()],
        )
        self.assert_blackbox_login_called(retpath=TEST_RETPATH)
        self.assert_blackbox_createsession_called(extra_guard_host='test.yandex.ru')
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    comment='aid=%s;mgc=1;ttl=5' % TEST_AUTH_ID,
                    retpath=TEST_RETPATH,
                ),
            ],
        )
        self.assert_successful_auth_recorded_to_statbox(
            ttl=5,
            auth_args=dict(retpath=TEST_RETPATH),
        )
        self.assert_phone_logged()

    def test_ok_with_service_subscription(self):
        """
        Все проходит хорошо, кук не было, выписываем новые куки через createsession.
        А так же в треке есть service, на который мы подпишем юзера
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.service = 'lenta'
        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_track_ok(
            session=SESSION['session']['value'],
        )
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            state='otp_auth_finished',
            accounts=[self.get_account_info()],
        )
        self.assert_blackbox_login_called(service='lenta')
        self.assert_blackbox_createsession_called()
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    login=TEST_LOGIN,
                    comment='aid=%s;mgc=1;ttl=5' % TEST_AUTH_ID,
                ),
            ],
        )

        self.assert_successful_auth_recorded_to_statbox(
            ttl=5,
            auth_args={
                'from': 'lenta',
            },
            additional_entries=[
                self.env.statbox.entry(
                    'subscription_added',
                    uid=str(TEST_UID),
                    sid='23',
                ),
            ],
        )
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'subscription.23', '1', uid=TEST_UID, db='passportdbshard1')
        self.assert_phone_logged()

    def test_ok_with_totp_check_time_saved(self):
        """
        Все проходит хорошо, кук не было, выписываем новые куки через createsession.
        ЧЯ вернул account.totp.check_time, запишем его в базу
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                totp_check_time=123,
                **deep_merge(
                    dict(attributes={
                        'account.2fa_on': '1',
                    }),
                    build_phone_secured(
                        1,
                        TEST_PHONE_NUMBER.e164,
                    )
                )
            ),
        )
        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_track_ok(
            session=SESSION['session']['value'],
            blackbox_totp_check_time='123',
        )
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            state='otp_auth_finished',
            accounts=[self.get_account_info()],
        )
        self.assert_blackbox_login_called()
        self.assert_blackbox_createsession_called()
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    login=TEST_LOGIN,
                    comment='aid=%s;mgc=1;ttl=5' % TEST_AUTH_ID,
                ),
            ],
        )
        self.assert_successful_auth_recorded_to_statbox(ttl=5)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.assert_phone_logged()

    def test_ok_valid_same_user_session(self):
        """Все проходит хорошо, пришли со своей же кукой, выписываем новые куки через editsession"""
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_track_ok(
            session=SESSION['session']['value'],
        )
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(with_lah=False),
            default_uid=TEST_UID,
            state='otp_auth_finished',
            accounts=[self.get_account_info()],
        )
        self.assert_blackbox_login_called()
        self.assert_blackbox_sessionid_called()
        self.assert_edit_session_called(call_index=2)
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_update',
                    comment='aid=%s;mgc=1;ttl=0' % TEST_AUTH_ID,
                ),
            ],
        )
        self.assert_successful_auth_recorded_to_statbox(
            ttl=0,
            auth_args=dict(old_session_uids=str(TEST_UID), session_method='edit'),
            with_check_cookies=True,
        )
        self.assert_phone_logged()

        self.env.credentials_logger.assert_has_written([
            self.env.credentials_logger.entry(
                'auth',
                auth_id=TEST_AUTH_ID,
                login=TEST_LOGIN,
                ip=TEST_IP,
                track_id=self.track_id,
                uids_count='1',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT,
                region_id='102630',
                is_new='0',
                surface='web_otp',
                yandexuid=TEST_YANDEXUID_COOKIE,
            )
        ])

    def test_ok_captcha_passed_with_good_password_cached_in_track(self):
        """
        Все проходит хорошо, капча требуется, ее ввели,
        проверка логина пароля была проведена ранее.
        Заодно проверяем, что сохранили кешированный totp.check_time
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True
            track.blackbox_login_status = blackbox.BLACKBOX_LOGIN_VALID_STATUS
            track.blackbox_password_status = blackbox.BLACKBOX_PASSWORD_VALID_STATUS
            track.blackbox_totp_check_time = 123
            track.bruteforce_status = 'captcha'

        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            state='otp_auth_finished',
            accounts=[self.get_account_info()],
        )
        self.assert_track_ok(
            session=SESSION['session']['value'],
            is_captcha_required=False,
        )
        self.assert_blackbox_userinfo_called()
        self.assert_blackbox_createsession_called()
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    login=TEST_LOGIN,
                    comment='aid=%s;cpt=1;mgc=1;ttl=5' % TEST_AUTH_ID,
                ),
            ],
        )
        self.assert_successful_auth_recorded_to_statbox(
            ttl=5,
            captcha_passed=True,
            auth_args=dict(bruteforce='captcha'),
        )
        self.assert_phone_logged()

    def assert_edit_session_called(self, call_index=2, extra_guard_host=None):
        guard_hosts = ['passport-test.yandex.ru']
        if extra_guard_host is not None:
            guard_hosts.append(extra_guard_host)
        check_all_url_params_match(
            self.env.blackbox._mock.request.call_args_list[call_index][0][1],
            {
                'sessionid': '0:old-session',
                'method': 'editsession',
                'op': 'add',
                'uid': str(TEST_UID),
                'lang': '1',
                'password_check_time': TimeNow(),
                'have_password': '1',
                'format': 'json',
                'keyspace': 'yandex.ru',
                'host': TEST_HOST,
                'userip': TEST_IP,
                'new_default': str(TEST_UID),
                'create_time': TimeNow(),
                'guard_hosts': ','.join(guard_hosts),
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def get_account_info(self, login=TEST_LOGIN, uid=TEST_UID, display_name=None, display_login=None):
        info = {
            'uid': uid,
            'login': login,
            'display_name': {'name': '', 'default_avatar': ''},
            'display_login': login if display_login is None else display_login,
        }
        if display_name:
            info['display_name'] = display_name
        return info

    def test_ok_with_cookies(self):
        """
        Все проходит без ошибок по пути с валидной сессионной кукой того же пользователя.
        Для выдачи сессионных кук вызывается editsession op=add
        """
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_response_ok(
            resp,
            state='otp_auth_finished',
            cookies=self.get_expected_cookies(with_lah=False),
            default_uid=TEST_UID,
            accounts=[self.get_account_info()],
        )

        self.assert_track_ok(
            session=SESSION['session']['value'],
        )

        self.assert_blackbox_login_called()
        self.assert_blackbox_sessionid_called()
        self.assert_edit_session_called()

        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_update',
                    comment='aid=%s;mgc=1;ttl=0' % TEST_AUTH_ID,
                ),
            ],
        )
        self.assert_successful_auth_recorded_to_statbox(
            ttl=0,
            auth_args=dict(session_method='edit', old_session_uids=str(TEST_UID)),
            with_check_cookies=True,
        )
        self.assert_phone_logged()

    def test_ok_without_cookies(self):
        """
        Все проходит без ошибок по пути без куки.
        Для выдачи сессионных кук вызывается createsession
        """
        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )

        self.assert_response_ok(
            resp,
            state='otp_auth_finished',
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            accounts=[self.get_account_info()],
        )

        self.assert_track_ok(
            session=SESSION['session']['value'],
        )

        self.assert_blackbox_login_called()
        self.assert_blackbox_createsession_called()

        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    comment='aid=%s;mgc=1;ttl=5' % TEST_AUTH_ID,
                ),
            ],
        )
        self.assert_successful_auth_recorded_to_statbox(ttl=5)
        self.assert_phone_logged()

    def test_ok_with_foreign_cookies(self):
        """
        Все проходит без ошибок по пути с валидной сессионной кукой другого пользователя.
        Для выдачи сессионных кук вызывается editsession op=add
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=1234,
                login='other_login',
                authid=TEST_OLD_AUTH_ID,
                age=TEST_COOKIE_AGE,
                ttl=5,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_response_ok(
            resp,
            state='otp_auth_finished',
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            accounts=[
                self.get_account_info(uid=1234, login='other_login'),
                self.get_account_info(),
            ],
        )

        self.assert_track_ok(
            session=SESSION['session']['value'],
        )

        self.assert_blackbox_login_called()
        self.assert_blackbox_sessionid_called()
        self.assert_edit_session_called()

        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    uid='1234',
                    login='other_login',
                    status='ses_update',
                    comment='aid=%s;ttl=5' % TEST_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    status='ses_create',
                    login=TEST_LOGIN,
                    comment='aid=%s;mgc=1;ttl=5' % TEST_AUTH_ID,
                ),
            ],
        )
        self.assert_successful_auth_recorded_to_statbox(
            ttl=5,
            auth_args=dict(
                session_method='edit',
                uids_count='2',
                old_session_uids='1234',
            ),
            with_check_cookies=True,
        )
        self.assert_phone_logged()

    def test_cookie_overflow_error(self):
        """
        Приходим с мультикукой, логин и отп верные, но
        ЧЯ говорит, что в куку больше нельзя дописать пользователей
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                authid=TEST_OLD_AUTH_ID,
                age=TEST_COOKIE_AGE,
                ttl=5,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
                allow_more_users=False,
            ),
        )
        resp = self.make_request(self.query_params(), self.get_headers())
        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        actual_response = json.loads(resp.data)
        eq_(
            actual_response,
            {
                'status': 'error',
                'errors': [u'sessionid.overflow'],
                'track_id': self.track_id,
            },
        )

    def test_ok_pdd_retpath_cleaned(self):
        """
        Все проходит без ошибок по пути с валидной сессионной кукой того же пользователя.
        Для выдачи сессионных кук вызывается editsession op=add
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                **deep_merge(
                    dict(attributes={
                        'account.2fa_on': '1',
                    }),
                    build_phone_secured(
                        1,
                        TEST_PHONE_NUMBER.e164,
                    )
                )
            ),
        )

        hosted_domains_response = blackbox_hosted_domains_response(
            count=1,
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                authid=TEST_OLD_AUTH_ID,
                age=TEST_COOKIE_AGE,
                ttl=5,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_PDD_RETPATH

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        eq_(resp.status_code, 200)
        data = json.loads(resp.data)
        eq_(data['retpath'], TEST_CLEANED_PDD_RETPATH)

    def test_ok_with_policy(self):
        """
        Проверим, что параметр policy при передаче в ручку отрабатывает
        """
        resp = self.make_request(
            self.query_params(policy=AUTHORIZATION_SESSION_POLICY_SESSIONAL),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )

        self.assert_response_ok(
            resp,
            state='otp_auth_finished',
            cookies=self.get_expected_cookies(with_lah=False),
            default_uid=TEST_UID,
            accounts=[self.get_account_info()],
        )

        self.assert_track_ok(
            session=SESSION['session']['value'],
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_SESSIONAL,
        )

        self.assert_blackbox_login_called()
        self.assert_blackbox_createsession_called(ttl='0')

        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    comment='aid=%s;mgc=1;ttl=0' % TEST_AUTH_ID,
                ),
            ],
        )
        self.assert_successful_auth_recorded_to_statbox(ttl=0)
        self.assert_phone_logged()

    def test_commit_csrf_token_empty_error(self):
        resp = self.make_request(
            self.query_params(exclude=['csrf_token']),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'errors': ['csrf_token.empty'],
            },
        )

    def test_commit_csrf_token_with_spaces_empty_error(self):
        resp = self.make_request(
            self.query_params(csrf_token='          '),
            self.get_headers(),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'errors': ['csrf_token.empty'],
            },
        )

    def test_commit_csrf_token_invalid_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.csrf_token = 'testblabla'

        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'errors': ['csrf_token.invalid'],
                'track_id': self.track_id,
            },
        )

    def test_x_token_valid_and_no_uid__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'valid'
            track.otp = None
            track.login = None

        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_x_token_invalid_alone__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'invalid'
            track.otp = None
            track.login = None

        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_error_response(resp, ['oauth_token.invalid'], track_id=self.track_id)

    def test_x_token_invalid_with_otp__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'invalid'

        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            state='otp_auth_finished',
            accounts=[self.get_account_info()],
        )
        self.assert_track_ok(session=SESSION['session']['value'])
        self.assert_blackbox_login_called()
        self.assert_blackbox_createsession_called()
        self.assert_successful_auth_recorded_to_statbox(
            ttl=5,
        )
        self.assert_phone_logged()

    def test_both_choose_otp__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'valid'
            track.uid = TEST_UID

        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            state='otp_auth_finished',
            accounts=[self.get_account_info()],
        )
        self.assert_track_ok(session=SESSION['session']['value'])
        self.assert_blackbox_login_called()
        self.assert_blackbox_createsession_called()
        self.assert_successful_auth_recorded_to_statbox(
            ttl=5,
        )
        self.assert_phone_logged()

    def test_by_x_token__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'valid'
            track.uid = TEST_UID
            track.otp = ''
            track.login = ''

        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
            state='otp_auth_finished',
            accounts=[self.get_account_info()],
            is_2fa_enabled_yp=False,
        )
        self.assert_track_ok(
            session=SESSION['session']['value'],
            otp='',
            uid=str(TEST_UID),
            cred_status='valid',
        )
        self.assert_blackbox_userinfo_called()
        self.assert_blackbox_createsession_called(check_password=False)
        self.assert_successful_auth_recorded_to_statbox(
            ttl=5,
            auth_args={'auth_source': 'xtoken'},
            type_='x_token',
            auth_exclude=['is_2fa_enabled'],
            finished_exclude=['is_2fa_enabled', 'password_like_otp'],
        )
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    comment='aid=%s;asrc=xtoken;mgcxt=1;ttl=5' % TEST_AUTH_ID,
                ),
            ],
        )

    def test_by_x_token_2fa__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'valid'
            track.uid = TEST_UID
            track.otp = ''
            track.login = ''

        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_error_response(
            resp,
            ['account.invalid_type'],
            track_id=self.track_id,
        )

    def test_ok_with_retpath_and_sessguard(self):
        """
        Все проходит хорошо, кук не было, выписываем новые куки через createsession.
        В треке есть retpath, в ответе blackbox - sessguard кука для текущего хоста и хоста из retpath.
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
        createsession_response = blackbox_createsession_response(
            authid=TEST_AUTH_ID,
            ip=TEST_IP,
            time=TEST_COOKIE_TIMESTAMP,
            sessguard_hosts=['passport-test.yandex.ru', TEST_RETPATH_HOST],
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            createsession_response,
        )
        self.env.blackbox.set_blackbox_response_value('sign', blackbox_sign_response())
        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        self.assert_track_ok(
            session=SESSION['session']['value'],
        )
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(with_sessguard=True),
            default_uid=TEST_UID,
            state='otp_auth_finished',
            retpath=TEST_RETPATH,
            accounts=[self.get_account_info()],
            service_guard_container='123.abc',
        )
        self.assert_blackbox_sign_sessguard_called()
        self.assert_blackbox_login_called(retpath=TEST_RETPATH)
        self.assert_blackbox_createsession_called(extra_guard_host=TEST_RETPATH_HOST)
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    comment='aid=%s;mgc=1;ttl=5' % TEST_AUTH_ID,
                    retpath=TEST_RETPATH,
                ),
            ],
        )
        self.assert_successful_auth_recorded_to_statbox(
            ttl=5,
            auth_args=dict(retpath=TEST_RETPATH),
        )
        self.assert_phone_logged()

    def test_ok_with_cookies_retpath_and_sessguard(self):
        """
        Все проходит без ошибок по пути с валидной сессионной кукой того же пользователя.
        Для выдачи сессионных кук вызывается editsession op=add.
        В треке есть retpath, в ответе blackbox - sessguard кука для текущего хоста и хоста из retpath.
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
        editsession_response = blackbox_editsession_response(
            authid=TEST_AUTH_ID,
            ip=TEST_IP,
            time=TEST_COOKIE_TIMESTAMP,
            sessguard_hosts=['passport-test.yandex.ru', TEST_RETPATH_HOST],
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            editsession_response,
        )
        self.env.blackbox.set_blackbox_response_value('sign', blackbox_sign_response())
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_response_ok(
            resp,
            state='otp_auth_finished',
            cookies=self.get_expected_cookies(with_lah=False, with_sessguard=True),
            default_uid=TEST_UID,
            accounts=[self.get_account_info()],
            retpath=TEST_RETPATH,
            service_guard_container='123.abc',
        )

        self.assert_track_ok(
            session=SESSION['session']['value'],
        )

        self.assert_blackbox_login_called(retpath=TEST_RETPATH)
        self.assert_blackbox_sessionid_called()
        self.assert_edit_session_called(extra_guard_host=TEST_RETPATH_HOST)

        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_update',
                    comment='aid=%s;mgc=1;ttl=0' % TEST_AUTH_ID,
                ),
            ],
        )
        self.assert_successful_auth_recorded_to_statbox(
            ttl=0,
            auth_args=dict(session_method='edit', old_session_uids=str(TEST_UID), retpath=TEST_RETPATH),
            with_check_cookies=True,
        )
        self.assert_phone_logged()
