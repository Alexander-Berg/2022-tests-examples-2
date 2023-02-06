# -*- coding: utf-8 -*-
import json
import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.authorization import (
    AUTHORIZATION_SESSION_POLICY_SESSIONAL,
    build_cookie_yp,
    SessionScope,
)
from passport.backend.api.test.mixins import ProfileTestMixin
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core import Undefined
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_ip_response,
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_sign_response,
    blackbox_userinfo_response,
)
from passport.backend.core.cookies import (
    cookie_l,
    cookie_lah,
    cookie_y,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    check_all_url_params_match,
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.utils.pkce import make_code_challenge_s256


TEST_UID = 1
TEST_PDD_UID = 1130000000000001
TEST_PDD_LOGIN = 'login@fakedomain.com'
TEST_HOST = '.yandex.ru'
TEST_USER_IP = '127.0.0.1'
TEST_USER_AGENT = 'curl'
TEST_YANDEXUID_COOKIE = 'cookie_yandexuid'
TEST_USER_COOKIES = 'yandexuid=%s' % TEST_YANDEXUID_COOKIE
TEST_REFERER = 'http://passportdev-python.yandex.ru/passport?mode=passport'
TEST_RETPATH = 'http://test.yandex.ru'
TEST_RETPATH_HOST = 'test.yandex.ru'
TEST_OLD_AUTH_ID = '123:0000000:555'
TEST_LOGIN_ID = 'login-id'
TEST_DEVICE_ID = 'A3B35F7E-09CE-4A8D-A53B-4C8A87CE73C9'

EXPECTED_SESSIONID_COOKIE = u'Session_id=2:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/'
EXPECTED_SESSIONID_SECURE_COOKIE = u'sessionid2=2:sslsession; Domain=.yandex.ru; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'
EXPECTED_AUTH_ID = '123:1422501443:126'
COOKIE_L_VALUE = 'VFV5DX94f0RRfXFTXVl5YH8GB2F6VlJ7XzNUTyYaIB1HBlpZBSd6QFkfOAJ7OgEACi5QFlIEGUM+KjlhRgRXZw==.1376993918.1002323.298859.ee75287c1dfd8b073375aee93158eb5b'
EXPECTED_L_COOKIE = u'L=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/' % COOKIE_L_VALUE

COOKIE_LAH_VALUE = 'OG5EOF8wU_bOAGhjXFp7YXkHAGB9UVFyB2IACGZedV4DWl8FWXF5BgJXYFVzYQVKV3kFVlpaU0p2f31iRkZRYQ.1473090908.1002323.1.2fe2104fff29aa69e867d7d1ea601470'
EXPECTED_LAH_COOKIE = u'lah=%s; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; HttpOnly; Path=/' % COOKIE_LAH_VALUE

COOKIE_YP_VALUE = '1692607429.udn.bG9naW4%3D%0A'
EXPECTED_YP_COOKIE = u'yp=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % COOKIE_YP_VALUE

COOKIE_YP_WITH_2FA_ENABLED_VALUE = '1751012630.udn.p%3Atest#1751012630.2fa.1'

COOKIE_YS_VALUE = 'udn.bG9naW4%3D%0A'
EXPECTED_YS_COOKIE = u'ys=%s; Domain=.yandex.ru; Secure; Path=/' % COOKIE_YS_VALUE

EXPECTED_YANDEX_LOGIN_COOKIE = u'yandex_login=test; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/'

EXPECTED_SESSGUARD_COOKIE = u'sessguard=1.sessguard; Domain=.passport-test.yandex.ru; Secure; HttpOnly; Path=/'

TEST_SESSIONID = '0:old-session'
TEST_USER_COOKIES_WITH_SESSION = TEST_USER_COOKIES + ';Session_id=%s' % TEST_SESSIONID

TEST_RICH_USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; LG-H818 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.95 Mobile Safari/537.36'

TEST_RICH_USER_AGENT_INFO = {
    'BrowserBase': 'Chromium',
    'BrowserBaseVersion': '48.0.2564.95',
    'BrowserEngine': 'WebKit',
    'BrowserEngineVersion': '537.36',
    'BrowserName': 'ChromeMobile',
    'BrowserVersion': '48.0.2564',
    'DeviceModel': 'H818',
    'DeviceName': 'LG-H818',
    'DeviceVendor': 'LG Electronics',
    'OSFamily': 'Android',
    'OSName': 'Android Marshmallow',
    'OSVersion': '6.0',
    'isBrowser': True,
    'isMobile': True,
    'isTouch': True,
    'CSP1Support': True,
    'CSP2Support': True,
    'historySupport': True,
    'localStorageSupport': True,
    'postMessageSupport': True,
    'SVGSupport': True,
    'WebPSupport': True,
}

TEST_RAW_ENV_FOR_PROFILE = {
    'ip': TEST_USER_IP,
    'yandexuid': TEST_YANDEXUID_COOKIE,
    'user_agent_info': TEST_RICH_USER_AGENT_INFO,
}

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE

TEST_CODE_VERIFIER = 'verifier'
TEST_CODE_CHALLENGE = make_code_challenge_s256(TEST_CODE_VERIFIER)


def build_headers(cookie=TEST_USER_COOKIES, user_agent=TEST_USER_AGENT, host=TEST_HOST):
    return mock_headers(
        host=host,
        user_ip=TEST_USER_IP,
        user_agent=user_agent,
        cookie=cookie,
        referer=TEST_REFERER,
    )


class BaseTestSessionCreate(
    ProfileTestMixin,
    BaseBundleTestViews,
):
    def setUp(self, track_type='authorize'):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'session': ['create']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(track_type)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.login = 'test'
            track.human_readable_login = 'test'
            track.machine_readable_login = 'test'
            track.language = 'ru'
            track.allow_authorization = True
            track.have_password = True
            track.is_password_passed = True
            if track_type == 'authorize':
                track.auth_method = 'password'

        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(),
        )
        self.setup_statbox_templates()

        self._cookie_l_pack = mock.Mock(return_value=COOKIE_L_VALUE)

        self._cookie_ys_pack = mock.Mock(return_value=COOKIE_YS_VALUE)
        self._cookie_yp_pack = mock.Mock(return_value=COOKIE_YP_VALUE)

        self._cookie_lah_pack = mock.Mock(return_value=COOKIE_LAH_VALUE)

        self.cookies_patches = [
            mock.patch.object(
                cookie_l.CookieL,
                'pack',
                self._cookie_l_pack,
            ),
            mock.patch.object(
                cookie_y.SessionCookieY,
                'pack',
                self._cookie_ys_pack,
            ),
            mock.patch.object(
                cookie_y.PermanentCookieY,
                'pack',
                self._cookie_yp_pack,
            ),
            mock.patch.object(
                cookie_lah.CookieLAH,
                'pack',
                self._cookie_lah_pack,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
        ]
        for patch in self.cookies_patches:
            patch.start()
        self.setup_profile_patches()

        self.env.blackbox.set_response_side_effect(
            'createsession',
            [
                blackbox_createsession_response(login_id=TEST_LOGIN_ID),
            ],
        )

    def tearDown(self):
        self.teardown_profile_patches()
        for patch in reversed(self.cookies_patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.cookies_patches
        del self._cookie_l_pack
        del self._cookie_ys_pack
        del self._cookie_lah_pack
        del self._cookie_yp_pack

    def build_auth_log_entry(self, status, uid, login, comment, user_agent=TEST_USER_AGENT):
        return [
            ('login', login),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('status', status),
            ('uid', str(uid)),
            ('useragent', user_agent),
            ('yandexuid', TEST_YANDEXUID_COOKIE),
            ('comment', comment),
        ]

    def build_auth_log_entries(self, uid=TEST_UID, extra_entry=None):
        entries = [
            ('login', 'test'),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('status', 'ses_create'),
            ('uid', str(uid)),
            ('useragent', TEST_USER_AGENT),
            ('yandexuid', TEST_YANDEXUID_COOKIE),
        ]
        if extra_entry:
            entries.append(extra_entry)
        return entries

    def make_request(
        self,
        data=None,
        headers=None,
    ):
        if data is None:
            data = self.query_params()
        if headers is None:
            headers = self.headers()
        return self.env.client.post(
            '/1/bundle/session/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        params = {
            'track_id': self.track_id,
        }
        params.update(kwargs)
        return params

    def headers(self):
        return build_headers()

    def assert_createsession_called(
        self,
        uid=TEST_UID,
        call_index=1,
        password_check_time_is_sent=True,
        have_password=True,
        is_yastaff=False,
        is_betatester=False,
        ttl=5,
        login_id=None,
        guard_hosts=None,
        is_scholar=None,
        yateam_auth=None,
    ):
        if guard_hosts is None:
            guard_hosts = ['passport-test.yandex.ru']
        sessionid_url = self.env.blackbox._mock.request.call_args_list[call_index][0][1]
        expected_params = {
            'auth_time': TimeNow(as_milliseconds=True),
            'create_time': TimeNow(),
            'format': 'json',
            'guard_hosts': ','.join(guard_hosts),
            'have_password': str(int(have_password)),
            'host_id': '7f',
            'is_lite': '0',
            'keyspace': 'yandex.ru',
            'lang': '1',
            'method': 'createsession',
            'request_id': mock.ANY,
            'ttl': str(ttl),
            'uid': str(uid),
            'userip': TEST_USER_IP,
            'ver': '3',
            'get_login_id': 'yes',
        }

        if login_id is not None:
            expected_params['login_id'] = login_id
        if is_betatester:
            expected_params['is_betatester'] = '1'
        if is_scholar:
            expected_params['is_scholar'] = '1'
        if is_yastaff:
            expected_params['is_yastaff'] = '1'
        if password_check_time_is_sent:
            expected_params['password_check_time'] = TimeNow()
        if yateam_auth is not None:
            expected_params['yateam_auth'] = '1' if yateam_auth else '0'

        check_all_url_params_match(sessionid_url, expected_params)

    def assert_check_ip_called(self, call_index=1):
        self.env.blackbox.requests[call_index].assert_query_contains(dict(
            method='checkip',
            ip=TEST_USER_IP,
            nets='yandexusers',
        ))

    def assert_error_response(self, response, expected_errors):
        eq_(response.status_code, 200)
        response = json.loads(response.data)
        eq_(response['status'], 'error')
        eq_(response['errors'], expected_errors)

    def assert_error_response_with_track_id(self, response, expected_errors, retpath=None):
        eq_(response.status_code, 200)
        response = json.loads(response.data)
        eq_(response['status'], 'error')
        eq_(response['errors'], expected_errors)
        eq_(response['track_id'], self.track_id)
        if retpath:
            eq_(response['retpath'], retpath)
        else:
            ok_('retpath' not in response)

    def get_expected_cookies(self, with_lah=True, with_sessguard=False):
        specific = [
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_YANDEX_LOGIN_COOKIE,
            EXPECTED_SESSIONID_SECURE_COOKIE,
            EXPECTED_MDA2_BEACON_COOKIE,
        ]

        cookies = [
            EXPECTED_YP_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_L_COOKIE,
        ]
        if with_lah:
            cookies.append(EXPECTED_LAH_COOKIE)
        if with_sessguard:
            cookies.append(EXPECTED_SESSGUARD_COOKIE)
        return sorted(specific + cookies)

    def get_expected_response(self, uid=TEST_UID, retpath=None, with_lah=True, with_sessguard=False, with_service_guard_container=False):
        expected = {
            'status': 'ok',
            'track_id': self.track_id,
            'cookies': self.get_expected_cookies(with_lah=with_lah, with_sessguard=with_sessguard),
            'default_uid': uid,
        }
        if retpath:
            expected['retpath'] = retpath
        if with_service_guard_container:
            expected['service_guard_container'] = '123.abc'
        return expected

    def assert_response_ok(self, response, **kwargs):
        self.assert_ok_response(response, ignore_order_for=['cookies'], **self.get_expected_response(**kwargs))

    def assert_track_ok(self, with_sessguard=False):
        track = self.track_manager.read(self.track_id)
        eq_(track.session, '2:session')
        eq_(track.sslsession, '2:sslsession')
        eq_(track.sessguard, '1.sessguard' if with_sessguard else None)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'cookie_set',
            track_id=self.track_id,
            cookie_version='3',
            ttl='5',
            mode='any_auth',
            captcha_passed='0',
            action='cookie_set',
            yandexuid=TEST_YANDEXUID_COOKIE,
            ip=TEST_USER_IP,
            authid=EXPECTED_AUTH_ID,
            input_login='test',
            user_agent=TEST_USER_AGENT,
            session_method='create',
            uids_count='1',
            uid=str(TEST_UID),
        )


@with_settings_hosts(
    SESSIONAL_COOKIE_TTL=0,
    PERMANENT_COOKIE_TTL=5,
    PASSPORT_SUBDOMAIN='passport-test',
    YDB_PERCENTAGE=0,
)
class TestSessionCreate(BaseTestSessionCreate):
    def test_without_headers(self):
        rv = self.make_request(
            self.query_params(),
            {},
        )

        self.assert_error_response(rv, ['host.empty', 'ip.empty', 'cookie.empty'])

    def test_without_track(self):
        rv = self.make_request(
            {},
            build_headers(),
        )

        self.assert_error_response(rv, ['track_id.empty'])

    def test_incorrect_track_id(self):
        with self.track_manager.transaction(self.track_id).delete():
            pass

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['track.not_found'])

    def test_authorization_not_allowed_with_retpath(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
            track.allow_authorization = False

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response_with_track_id(
            rv,
            ['auth.not_allowed'],
            retpath=TEST_RETPATH,
        )

    def test_account_global_logout_after_track_created_error(self):
        """
        Дергаем ручку с треком, после создания которого был сделан
        глогаут на аккаунте
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                attributes={'account.global_logout_datetime': str(int(time.time()) + 1)},
            ),
        )
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )
        self.assert_error_response_with_track_id(
            rv,
            ['account.global_logout'],
        )

    def test_with_already_created_session(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = 'abc123'
            track.sslsession = 'abc123'

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response_with_track_id(rv, ['account.auth_passed'])

    def test_https_session_response_password_not_passed(self):
        """
        Просим создать сессию по хттпс, но пароль не передавался.
        Секьюрная кука должна быть выписана.
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_passed = False

        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called(password_check_time_is_sent=False)
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.assert_track_ok()

    def test_session_response(self):
        """
        Просим создать сессию и пароль передавался.
        Куки должны быть выписаны.
        """
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(login_id=TEST_LOGIN_ID),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called()
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.env.antifraud_logger.assert_has_written([
            self.env.antifraud_logger.entry(
                'base',
                status='OK',
                authid=EXPECTED_AUTH_ID,
                external_id='track-{}'.format(self.track_id),
                ip=TEST_USER_IP,
                channel='auth',
                login_id=TEST_LOGIN_ID,
                request='auth',
                sub_channel='login',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT,
                yandexuid=TEST_YANDEXUID_COOKIE,
                lah_uids='',
                service_id='login',
                cookie_auth='true',
            )
        ])
        self.assert_track_ok()

    def test_track_with_device_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(login_id=TEST_LOGIN_ID),
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'
            track.device_application = 'ru.yandex.test'
            track.device_id = TEST_DEVICE_ID
            track.surface = 'mobile_proxy_password'

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called()
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.env.antifraud_logger.assert_has_written([
            self.env.antifraud_logger.entry(
                'base',
                status='OK',
                authid=EXPECTED_AUTH_ID,
                external_id='track-{}'.format(self.track_id),
                ip=TEST_USER_IP,
                channel='auth',
                sub_channel='login',
                request='auth',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT,
                yandexuid=TEST_YANDEXUID_COOKIE,
                lah_uids='',
                login_id=TEST_LOGIN_ID,
                service_id='login',
                # вся соль теста ниже!
                account_manager_version='5.0.0',
                device_os_id='iPhone',
                device_application='ru.yandex.test',
                device_id=TEST_DEVICE_ID,
                cookie_auth='true',
            )
        ])
        self.env.credentials_logger.assert_has_written([
            self.env.credentials_logger.entry(
                'auth',
                auth_id=EXPECTED_AUTH_ID,
                login='test',
                ip=TEST_USER_IP,
                track_id=self.track_id,
                uids_count='1',
                deviceid=TEST_DEVICE_ID,
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT,
                yandexuid=TEST_YANDEXUID_COOKIE,
                is_new='1',
                surface='mobile_proxy_password',
            )
        ])
        self.assert_track_ok()

    def test_track_with_passed_challenge(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(login_id=TEST_LOGIN_ID),
        )

        with self.track_transaction(self.track_id) as track:
            track.auth_challenge_type = 'phone_confirmation'
            track.phone_confirmation_method = 'by_flash_call'

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called()
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;chlng=phone_confirmation;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.env.antifraud_logger.assert_has_written([
            self.env.antifraud_logger.entry(
                'base',
                status='OK',
                authid=EXPECTED_AUTH_ID,
                external_id='track-{}'.format(self.track_id),
                ip=TEST_USER_IP,
                channel='auth',
                sub_channel='login',
                request='auth',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT,
                yandexuid=TEST_YANDEXUID_COOKIE,
                lah_uids='',
                login_id=TEST_LOGIN_ID,
                service_id='login',
                cookie_auth='true',
                # вся соль теста ниже!
                challenge='flash_call',
            )
        ])
        self.assert_track_ok()

    def test_track_with_code_challenge__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(login_id=TEST_LOGIN_ID),
        )

        with self.track_transaction(self.track_id) as track:
            track.oauth_code_challenge = TEST_CODE_CHALLENGE
            track.oauth_code_challenge_method = 'S256'

        rv = self.make_request(
            self.query_params(code_verifier=TEST_CODE_VERIFIER),
            build_headers(),
        )

        self.assert_response_ok(rv)

    def test_track_with_code_challenge__verifier_not_passed(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(login_id=TEST_LOGIN_ID),
        )

        with self.track_transaction(self.track_id) as track:
            track.oauth_code_challenge = TEST_CODE_CHALLENGE
            track.oauth_code_challenge_method = 'S256'

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['code_verifier.not_matched'])

    def test_with_sessguard(self):
        """
        Просим создать сессию и пароль передавался.
        Куки должны быть выписаны.
        """
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(sessguard_hosts=['passport-test.yandex.ru']),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv, with_sessguard=True)
        self.assert_createsession_called()
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.assert_track_ok(with_sessguard=True)

    def test_with_login_id(self):
        """
        В треке сохранён login_id - должны выписать куку именно с таким login_id.
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login_id = TEST_LOGIN_ID

        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(login_id=TEST_LOGIN_ID),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called(login_id=TEST_LOGIN_ID)
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.env.antifraud_logger.assert_has_written([
            self.env.antifraud_logger.entry(
                'base',
                status='OK',
                authid=EXPECTED_AUTH_ID,
                external_id='track-{}'.format(self.track_id),
                ip=TEST_USER_IP,
                channel='auth',
                sub_channel='login',
                request='auth',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT,
                yandexuid=TEST_YANDEXUID_COOKIE,
                lah_uids='',
                service_id='login',
                cookie_auth='true',
                # вся соль теста ниже!
                login_id=TEST_LOGIN_ID,
            )
        ])
        self.assert_track_ok()

    def test_account_not_found_after_registration(self):
        """
        Аккаунт не найден, т.к. не успел доехать в реплику после регистрации
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called()
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.assert_track_ok()

    def test_create_session_with_captcha_passed(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )
        self.assert_response_ok(rv)
        self.assert_createsession_called()
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;cpt=1;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.assert_track_ok()

    def test_create_session_after_2fa_restore(self):
        """
        Создание сессии после 2ФА восстановления. В куке YP должны сбросить флаг 2ФА.
        """
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_otp_restore_passed = True

        build_cookie_yp_mock = mock.Mock(side_effect=lambda *args, **kwargs: build_cookie_yp(*args, **kwargs))
        with mock.patch(
                'passport.backend.api.common.authorization.build_cookie_yp',
                build_cookie_yp_mock,
        ):
            rv = self.make_request(
                self.query_params(),
                build_headers(),
            )

        # последний параметр - is_2fa_enabled_yp
        build_cookie_yp_mock.assert_called_with(mock.ANY, '', b'', '.yandex.ru', '/', False, False, Undefined)
        self.assert_response_ok(rv)
        self.assert_createsession_called()
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.assert_track_ok()

    def test_create_session_for_pdd_user(self):
        """Создание сессии для ПДД пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_PDD_UID

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )
        self.assert_response_ok(rv, uid=TEST_PDD_UID)
        self.assert_createsession_called(uid=TEST_PDD_UID)
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                uid=TEST_PDD_UID,
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.assert_track_ok()

    def test_yandexoid_and_betatester_passed(self):
        """
        Признаки сотрудника и бетатестера передаются в вызов ЧЯ
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={
                    'portal': 'login',
                    'yandexoid': 'yastaff_login',
                },
                subscribed_to=[668],
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called(is_betatester=True, is_yastaff=True)
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.assert_track_ok()

    def test_short_session_response(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.authorization_session_policy = AUTHORIZATION_SESSION_POLICY_SESSIONAL

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv, with_lah=False)
        self.assert_createsession_called(ttl=0)
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=0' % EXPECTED_AUTH_ID),
            ),
        )
        self.assert_track_ok()

    def test_ok_without_auth_method(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.auth_method = None

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )
        self.assert_response_ok(rv)

    def test_ok_with_magic_link_auth_method(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.auth_method = 'magic_link'

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )
        self.assert_response_ok(rv)

    def test_ok_with_magic_x_token_auth_method(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.auth_method = 'magic_x_token'

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )
        self.assert_response_ok(rv)

    def test_wrong_host_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.auth_method = 'magic_x_token'

        rv = self.make_request(
            self.query_params(),
            build_headers(host='wrong.host'),
        )
        self.assert_error_response(rv, ['host.invalid'])

    def test_phonish_account_invalid_type(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login='phne-123',
                aliases={
                    'phonish': 'phne-123',
                },
            ),
        )

        rv = self.make_request(self.query_params(), build_headers())
        self.assert_error_response(rv, ['account.invalid_type'])

    def test_kinopoisk_account_invalid_type(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login='kp-123',
                aliases={
                    'kinopoisk': 'kp-123',
                },
            ),
        )

        rv = self.make_request(self.query_params(), build_headers())
        self.assert_error_response(rv, ['account.invalid_type'])

    def test_with_service_guard_container(self):
        """ Проверка service_guard_container """
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(
                sessguard_hosts=['passport-test.yandex.ru', TEST_RETPATH_HOST],
            ),
        )
        self.env.blackbox.set_blackbox_response_value('sign', blackbox_sign_response())
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv, with_sessguard=True, retpath=TEST_RETPATH, with_service_guard_container=True)
        self.assert_createsession_called(guard_hosts=['passport-test.yandex.ru', TEST_RETPATH_HOST])
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.assert_track_ok(with_sessguard=True)

    def test_passport_service_guard_not_put_into_container(self):
        test_retpath_host = 'magic.passport-test.yandex.ru'
        test_retpath = 'https://%s/' % test_retpath_host

        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(
                sessguard_hosts=['passport-test.yandex.ru', test_retpath_host],
            ),
        )
        self.env.blackbox.set_blackbox_response_value('sign', blackbox_sign_response())
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = test_retpath

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv, with_sessguard=True, with_service_guard_container=False, retpath=test_retpath)
        self.assert_createsession_called(guard_hosts=['passport-test.yandex.ru', test_retpath_host])
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.assert_track_ok(with_sessguard=True)

    def test_intranet_yandex_ip(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(login_id=TEST_LOGIN_ID),
        )
        self.env.blackbox.set_blackbox_response_value(
            'checkip',
            blackbox_check_ip_response(True),
        )

        with settings_context(IS_INTRANET=True, inherit_all_existing=True):
            rv = self.make_request(
                self.query_params(),
                build_headers(),
            )

        self.assert_response_ok(rv)
        self.assert_check_ip_called()
        self.assert_createsession_called(call_index=2, yateam_auth=True)
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.env.antifraud_logger.assert_has_written([
            self.env.antifraud_logger.entry(
                'base',
                status='OK',
                authid=EXPECTED_AUTH_ID,
                external_id='track-{}'.format(self.track_id),
                ip=TEST_USER_IP,
                channel='auth',
                login_id=TEST_LOGIN_ID,
                request='auth',
                sub_channel='login',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT,
                yandexuid=TEST_YANDEXUID_COOKIE,
                lah_uids='',
                service_id='login',
                cookie_auth='true',
            )
        ])
        self.assert_track_ok()

    def test_intranet_external_ip(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(login_id=TEST_LOGIN_ID),
        )
        self.env.blackbox.set_blackbox_response_value(
            'checkip',
            blackbox_check_ip_response(False),
        )

        with settings_context(IS_INTRANET=True, inherit_all_existing=True):
            rv = self.make_request(
                self.query_params(),
                build_headers(),
            )

        self.assert_response_ok(rv)
        self.assert_check_ip_called()
        self.assert_createsession_called(call_index=2, yateam_auth=False)
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;ttl=5' % EXPECTED_AUTH_ID),
            ),
        )
        self.env.antifraud_logger.assert_has_written([
            self.env.antifraud_logger.entry(
                'base',
                status='OK',
                authid=EXPECTED_AUTH_ID,
                external_id='track-{}'.format(self.track_id),
                ip=TEST_USER_IP,
                channel='auth',
                login_id=TEST_LOGIN_ID,
                request='auth',
                sub_channel='login',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT,
                yandexuid=TEST_YANDEXUID_COOKIE,
                lah_uids='',
                service_id='login',
                cookie_auth='true',
            )
        ])
        self.assert_track_ok()


@with_settings_hosts(
    SESSIONAL_COOKIE_TTL=0,
    PERMANENT_COOKIE_TTL=5,
    UFO_API_URL='http://localhost/',
    PASSPORT_SUBDOMAIN='passport-test',
    YDB_PERCENTAGE=0,
)
class TestMultiSessionCreate(BaseTestSessionCreate):
    def setUp(self):
        super(TestMultiSessionCreate, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(login_id=TEST_LOGIN_ID),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=EXPECTED_AUTH_ID,
                ip=TEST_USER_IP,
            ),
        )

    def assert_auth_log_ok(self, *args):
        eq_(self.env.auth_handle_mock.call_count, len(args))
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            args,
        )

    def assert_sessionid_called(self, sessguard=None):
        expected_params = {
            'allow_scholar': 'yes',
            'method': 'sessionid',
            'multisession': 'yes',
            'sessionid': TEST_SESSIONID,
        }
        if sessguard is not None:
            expected_params['sessguard'] = sessguard

        self.env.blackbox.requests[0].assert_query_contains(expected_params)

    def assert_editsession_called(
        self,
        call_index=1,
        uid=TEST_UID,
        new_default=TEST_UID,
        password_check_time_is_sent=True,
        sessguard=None,
        guard_hosts=None,
        sslsessionid='0:old-sslsession',
        is_scholar=None,
    ):
        if guard_hosts is None:
            guard_hosts = ['passport-test.yandex.ru']
        expected_params = {
            'create_time': TimeNow(),
            'format': 'json',
            'guard_hosts': ','.join(guard_hosts),
            'have_password': '1',
            'host': '.yandex.ru',
            'keyspace': u'yandex.ru',
            'lang': '1',
            'method': 'editsession',
            'op': 'add',
            'request_id': mock.ANY,
            'sessionid': TEST_SESSIONID,
            'uid': str(uid),
            'userip': TEST_USER_IP,
            'get_login_id': 'yes',
        }
        if is_scholar:
            expected_params['is_scholar'] = '1'
        if new_default is not None:
            expected_params['new_default'] = str(new_default)
        if password_check_time_is_sent:
            expected_params['password_check_time'] = TimeNow()
        if sessguard is not None:
            expected_params['sessguard'] = sessguard
        if sslsessionid:
            expected_params['sslsessionid'] = sslsessionid

        self.env.blackbox.requests[call_index].assert_query_contains(expected_params)

    def test_ok_without_cookie(self):
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called()

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_create',
                uid=TEST_UID,
                login='test',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('cookie_set'),
        ])
        self.assert_track_ok()

    def test_ok_with_auth_source_and_source_authid_in_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.auth_source = 'test_src'
            track.source_authid = TEST_OLD_AUTH_ID

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called()

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_create',
                uid=TEST_UID,
                login='test',
                comment='aid=%s;asrc=test_src;said=%s;ttl=5' % (EXPECTED_AUTH_ID, TEST_OLD_AUTH_ID),
            ),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'cookie_set',
                auth_source='test_src',
                source_authid=TEST_OLD_AUTH_ID,
            ),
        ])
        self.assert_track_ok()
        eq_(self.env.auth_challenge_handle_mock.call_count, 0)

    def test_auth_challenge_log_written_with_auth_source__xtoken(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.auth_source = authtypes.AUTH_SOURCE_XTOKEN

        rv = self.make_request(
            self.query_params(),
            build_headers(user_agent=TEST_RICH_USER_AGENT),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called()

        self.assert_ufo_api_called()
        profile = self.make_user_profile(raw_env=TEST_RAW_ENV_FOR_PROFILE)
        self.assert_profile_written_to_auth_challenge_log(profile)
        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_create',
                uid=TEST_UID,
                login='test',
                comment='aid=%s;asrc=%s;ttl=5' % (EXPECTED_AUTH_ID, authtypes.AUTH_SOURCE_XTOKEN),
                user_agent=TEST_RICH_USER_AGENT,
            ),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'cookie_set',
                auth_source=authtypes.AUTH_SOURCE_XTOKEN,
                user_agent=TEST_RICH_USER_AGENT,
            ),
        ])
        self.assert_track_ok()

    def test_account_not_found_after_registration__auth_challenge_log_not_written(self):
        """Аккаунт не найден, записи в auth_challenge.log не должно быть
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.auth_source = authtypes.AUTH_SOURCE_XTOKEN
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called()
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                extra_entry=('comment', 'aid=%s;asrc=%s;ttl=5' % (EXPECTED_AUTH_ID, authtypes.AUTH_SOURCE_XTOKEN)),
            ),
        )
        self.assert_track_ok()
        eq_(self.env.auth_challenge_handle_mock.call_count, 0)

    def test_with_cookies__overflow_error(self):
        """
        Пришли с мультикукой, на которую
        ЧЯ говорит, что в куку больше нельзя дописать пользователей
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                ttl=5,
                allow_more_users=False,
            ),
        )
        resp = self.make_request(
            self.query_params(),
            build_headers(cookie=TEST_USER_COOKIES_WITH_SESSION),
        )
        self.assert_error_response_with_track_id(resp, ['sessionid.overflow'])
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [self.env.statbox.entry('check_cookies', host='.yandex.ru')],
        )

    def test_with_cookies__no_overflow_for_same_uid(self):
        """
        Пришли с мультикукой, на которую
        ЧЯ говорит, что в куку больше нельзя дописать пользователей,
        но мы пришли с пользователем, который уже есть в куке,
        значит ошибки нет.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login='test',
                ttl=5,
                allow_more_users=False,
            ),
        )
        resp = self.make_request(
            self.query_params(),
            build_headers(
                cookie='%s;sessionid2=%s' % (TEST_USER_COOKIES_WITH_SESSION, '0:old-sslsession'),
            ),
        )
        self.assert_response_ok(resp)
        self.assert_sessionid_called()
        self.assert_editsession_called(call_index=2)

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_update',
                uid=TEST_UID,
                login='test',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='.yandex.ru'),
            self.env.statbox.entry(
                'cookie_set',
                session_method='edit',
                old_session_uids='1',
            ),
        ])
        self.assert_track_ok()

    def test_ok_with_invalid_cookie(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(cookie=TEST_USER_COOKIES_WITH_SESSION),
        )

        self.assert_response_ok(rv)
        self.assert_sessionid_called()
        self.assert_createsession_called(call_index=2)

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_create',
                uid=TEST_UID,
                login='test',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='.yandex.ru'),
            self.env.statbox.entry('cookie_set'),
        ])
        self.assert_track_ok()

    def test_ok_with_valid_short_cookie(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(
                cookie='%s;sessionid2=%s' % (TEST_USER_COOKIES_WITH_SESSION, '0:old-sslsession'),
            ),
        )

        self.assert_response_ok(rv, with_lah=False)
        self.assert_sessionid_called()
        self.assert_editsession_called(call_index=2)

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_update',
                uid='1234',
                login='other_login',
                comment='aid=%s;ttl=0' % EXPECTED_AUTH_ID,
            ),
            self.build_auth_log_entry(
                status='ses_create',
                uid=TEST_UID,
                login='test',
                comment='aid=%s;ttl=0' % EXPECTED_AUTH_ID,
            ),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='.yandex.ru'),
            self.env.statbox.entry(
                'cookie_set',
                session_method='edit',
                old_session_uids='1234',
                uids_count='2',
                ttl='0',
            ),
        ])
        self.assert_track_ok()

    def test_ok_with_sessguard(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                ttl=5,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=EXPECTED_AUTH_ID,
                ip=TEST_USER_IP,
                sessguard_hosts=['passport-test.yandex.ru'],
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(
                cookie='%s;sessionid2=%s;sessguard=%s' % (
                    TEST_USER_COOKIES_WITH_SESSION,
                    '0:old-sslsession',
                    '1.old_sessguard',
                ),
            ),
        )

        self.assert_response_ok(rv, with_sessguard=True)
        self.assert_sessionid_called(sessguard='1.old_sessguard')
        self.assert_editsession_called(call_index=2, sessguard='1.old_sessguard')

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_update',
                uid='1234',
                login='other_login',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
            self.build_auth_log_entry(
                status='ses_create',
                uid=TEST_UID,
                login='test',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='.yandex.ru', have_sessguard='1'),
            self.env.statbox.entry(
                'cookie_set',
                session_method='edit',
                old_session_uids='1234',
                uids_count='2',
                ttl='5',
            ),
        ])
        self.assert_track_ok(with_sessguard=True)

    def test_ok_without_changing_default(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                ttl=5,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=EXPECTED_AUTH_ID,
                ip=TEST_USER_IP,
            ),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.dont_change_default_uid = True

        rv = self.make_request(
            self.query_params(),
            build_headers(
                cookie='%s;sessionid2=%s;sessguard=%s' % (
                    TEST_USER_COOKIES_WITH_SESSION,
                    '0:old-sslsession',
                    '1.old_sessguard',
                ),
            ),
        )

        self.assert_response_ok(rv)
        self.assert_sessionid_called()
        self.assert_editsession_called(call_index=2, new_default=None)

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_update',
                uid='1234',
                login='other_login',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
            self.build_auth_log_entry(
                status='ses_create',
                uid=TEST_UID,
                login='test',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1', host='.yandex.ru'),
            self.env.statbox.entry(
                'cookie_set',
                session_method='edit',
                old_session_uids='1234',
                uids_count='2',
                ttl='5',
            ),
        ])
        self.assert_track_ok()

    def test_editsession_raises_blackbox_invalid_params__error(self):
        """
        При проверке куки по методу sessionid не возникло ошибок, но
        при вызове метода editsession возникла ошибка ЧЯ из-за того, что сессия недействительна
        """
        other_login, other_uid = 'other_login', 1234
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login='login',
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=other_uid,
                login=other_login,
            ),
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'editsession',
            blackbox.BlackboxInvalidParamsError(blackbox.BLACKBOX_ERROR_SESSION_LOGGED_OUT),
        )

        resp = self.make_request(
            self.query_params(),
            build_headers(
                cookie='Session_id=0:old-session; sessionid2=0:old-sslsession; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            ),
        )

        self.assert_error_response(
            resp,
            ['sessionid.expired'],
        )

        self.assert_sessionid_called()
        self.assert_editsession_called(2)
        self.assert_events_are_empty(self.env.auth_handle_mock)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_editsession_raises_blackbox_invalid_ip__error(self):
        """
        При проверке куки по методу sessionid не возникло ошибок, но
        при вызове метода editsession возникла ошибка ЧЯ из-за того, что ip неправильный
        """
        other_login, other_uid = 'other_login', 1234
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login='login',
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=other_uid,
                login=other_login,
            ),
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'editsession',
            blackbox.BlackboxInvalidParamsError(blackbox.BLACKBOX_ERROR_IP_NOT_YANDEX),
        )

        resp = self.make_request(
            self.query_params(),
            build_headers(
                cookie='Session_id=0:old-session; sessionid2=0:old-sslsession; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            ),
        )

        self.assert_error_response(
            resp,
            ['ip.invalid'],
        )

        self.assert_sessionid_called()
        self.assert_editsession_called(2)
        self.assert_events_are_empty(self.env.auth_handle_mock)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_createsession_raises_blackbox_invalid_ip__error(self):
        """
        при вызове метода createsession возникла ошибка ЧЯ из-за того, что ip неправильный
        """
        self.env.blackbox.set_blackbox_response_side_effect(
            'createsession',
            blackbox.BlackboxInvalidParamsError(blackbox.BLACKBOX_ERROR_IP_NOT_YANDEX),
        )

        resp = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response(
            resp,
            ['ip.invalid'],
        )

        self.assert_createsession_called()
        self.assert_events_are_empty(self.env.auth_handle_mock)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_with_service_guard_container(self):
        """ Проверка service_guard_container """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                ttl=5,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=EXPECTED_AUTH_ID,
                ip=TEST_USER_IP,
                sessguard_hosts=['passport-test.yandex.ru', TEST_RETPATH_HOST],
            ),
        )
        self.env.blackbox.set_blackbox_response_value('sign', blackbox_sign_response())

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        rv = self.make_request(
            self.query_params(),
            build_headers(
                cookie='%s;sessionid2=%s;sessguard=%s' % (
                    TEST_USER_COOKIES_WITH_SESSION,
                    '0:old-sslsession',
                    '1.old_sessguard',
                ),
            ),
        )

        self.assert_response_ok(rv, with_sessguard=True, retpath=TEST_RETPATH, with_service_guard_container=True)
        self.assert_sessionid_called(sessguard='1.old_sessguard')
        self.assert_editsession_called(call_index=2, sessguard='1.old_sessguard', guard_hosts=['passport-test.yandex.ru', TEST_RETPATH_HOST])

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_update',
                uid='1234',
                login='other_login',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
            self.build_auth_log_entry(
                status='ses_create',
                uid=TEST_UID,
                login='test',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='.yandex.ru', have_sessguard='1'),
            self.env.statbox.entry(
                'cookie_set',
                session_method='edit',
                old_session_uids='1234',
                uids_count='2',
                ttl='5',
                retpath=TEST_RETPATH,
            ),
        ])
        self.assert_track_ok(with_sessguard=True)

    def test_create_scholar_scope_session(self):
        with self.track_transaction() as track:
            track.session_scope = str(SessionScope.scholar)

        rv = self.make_request()

        self.assert_response_ok(rv)
        self.assert_createsession_called(is_scholar=True)
        self.assert_track_ok()

    def test_add_scholar_scope_session(self):
        with self.track_transaction() as track:
            track.session_scope = str(SessionScope.scholar)

        self.env.blackbox.set_response_side_effect('sessionid', [blackbox_sessionid_multi_response(uid=100)])

        headers = dict(self.headers())
        headers.update({'Ya-Client-Cookie': TEST_USER_COOKIES_WITH_SESSION})
        rv = self.make_request(headers=headers)

        self.assert_response_ok(rv, with_lah=False)
        self.assert_sessionid_called()
        self.assert_editsession_called(
            call_index=2,
            is_scholar=True,
            sslsessionid=None,
        )
        self.assert_track_ok()


@with_settings_hosts(
    PASSPORT_SUBDOMAIN='passport-test',
)
class TestRegistrationSessionCreate(BaseTestSessionCreate):
    def setUp(self):
        super(TestRegistrationSessionCreate, self).setUp(track_type='register')
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

    def test_ok(self):
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )
        self.assert_response_ok(rv)
