# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import (
    COOKIE_LAH_VALUE,
    EXPECTED_LAH_COOKIE,
    EXPECTED_MDA2_BEACON_COOKIE,
    MDA2_BEACON_VALUE,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_SESSIONID_EXPIRED_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_response,
    blackbox_sign_response,
)
from passport.backend.core.cookies import cookie_lah
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_UID = 1
TEST_LOGIN = 'test-user'
TEST_IP = '3.3.3.3'
TEST_OLD_AUTH_ID = '123:0000000:555'
TEST_COOKIE_AGE = 123456
TEST_COOKIE_TIMESTAMP = 1383144488
TEST_HOST = 'passport-test.yandex.ru'
TEST_USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; LG-H818 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.95 Mobile Safari/537.36'
TEST_YANDEXUID_COOKIE = '1046714081386936400'
TEST_REFERER = 'http://test.yandex.com/referer'
TEST_RETPATH = 'https://mail.yandex.ru'
TEST_RETPATH_HOST = 'mail.yandex.ru'
TEST_COOKIE = 'Session_id=0:old-session; yandexuid=%s' % TEST_YANDEXUID_COOKIE
TEST_COOKIE_WITH_SESSGUARD = '%s; sessguard=1.old_sessguard' % TEST_COOKIE
TEST_COOKIE_WITH_DUPLICATES = '%s; Session_id=foo' % TEST_COOKIE
TEST_COOKIE_WITH_SESSGUARD_AND_DUPLICATES = '%s; Session_id=foo' % TEST_COOKIE_WITH_SESSGUARD


@with_settings_hosts(
    BLACKBOX_FIELDS=(),
    BLACKBOX_ATTRIBUTES=(),
    PASSPORT_SUBDOMAIN='passport-test',
)
class UpdateSessionTestcase(BaseBundleTestViews):
    url = '/1/bundle/session/update/?consumer=dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'session': ['update']}))
        self.setup_statbox_templates()
        self.mda2_beacon_patch = mock.patch(
            'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
            return_value=MDA2_BEACON_VALUE,
        )
        self.mda2_beacon_patch.start()

    def tearDown(self):
        self.mda2_beacon_patch.stop()
        self.env.stop()
        del self.mda2_beacon_patch
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'updated',
            mode='any_auth',
            action='updated',
            consumer='dev',
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_COOKIE,
            referer=TEST_REFERER,
            auth_id=TEST_OLD_AUTH_ID,
            session_cookie_count='1',
            is_session_valid='1',
        )

    def get_headers(self, host=None, user_ip=None, cookie=None, user_agent=None):
        return mock_headers(
            host=host or TEST_HOST,
            user_agent=user_agent or TEST_USER_AGENT,
            cookie=cookie or TEST_COOKIE,
            user_ip=user_ip or TEST_IP,
            referer=TEST_REFERER,
        )

    def make_request(self, headers=None, **kwargs):
        return self.env.client.post(
            self.url,
            headers=headers or self.get_headers(),
            data=kwargs,
        )

    def check_blackbox_call(
        self,
        force_resign=False,
        sessguard=None,
        extra_guard_host=TEST_RETPATH_HOST,
        sign_container=False,
    ):
        eq_(len(self.env.blackbox.requests), 1 + sign_container)
        guard_hosts = ['passport-test.yandex.ru']
        if extra_guard_host:
            guard_hosts.append(extra_guard_host)
        expected_query = {
            'aliases': 'all_with_hidden',
            'allow_scholar': 'yes',
            'authid': 'yes',
            'format': 'json',
            'full_info': 'yes',
            'get_login_id': 'yes',
            'get_public_name': 'yes',
            'guard_hosts': ','.join(guard_hosts),
            'host': TEST_HOST,
            'is_display_name_empty': 'yes',
            'method': 'sessionid',
            'multisession': 'yes',
            'regname': 'yes',
            'request_id': mock.ANY,
            'resign': 'yes',
            'sessionid': '0:old-session',
            'userip': TEST_IP,
        }
        if force_resign:
            expected_query.update(force_resign='yes')
        if sessguard:
            expected_query.update(sessguard=sessguard)
        self.env.blackbox.requests[0].assert_query_equals(expected_query)
        if sign_container:
            sessguard_cookie = 'sessguard=1.sessguard; Domain=.%s; Secure; HttpOnly; Path=/' % TEST_RETPATH_HOST
            expected_sign_query = {
                'method': 'sign',
                'format': 'json',
                'sign_space': 'sessguard_container',
                'ttl': '60',
                'value': json.dumps({
                    'cookies': [sessguard_cookie],
                    'retpath': TEST_RETPATH,
                }),
            }
            self.env.blackbox.requests[1].assert_query_equals(expected_sign_query)

    def test_invalid_host_error(self):
        resp = self.make_request(
            headers=self.get_headers(host='google.com'),
        )
        self.assert_error_response(resp, ['host.invalid'])

    def test_invalid_cookie_error(self):
        """Пришла сессионная кука, которая оказалась невалидной"""
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_EXPIRED_STATUS,
            ),
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['sessionid.invalid'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_update_not_required(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                ip=TEST_IP,
                crypt_password='1:pwd',
                ttl=0,
            ),
        )
        resp = self.make_request(retpath=TEST_RETPATH)
        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
        )
        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_update_cookies(self):
        self.env.blackbox.set_response_value(
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
                prolong_cookies=True,
            ),
        )
        resp = self.make_request(retpath=TEST_RETPATH)
        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
            cookies=[
                'Session_id=3:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'sessionid2=3:sslsession; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'yandex_login=test-user; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/',
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
        )
        self.check_blackbox_call()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('updated', uid=str(TEST_UID)),
        ])

    def test_update_cookies_with_sessguard(self):
        self.env.blackbox.set_response_value(
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
                prolong_cookies=True,
                sessguard_hosts=['passport-test.yandex.ru'],
            ),
        )
        resp = self.make_request(
            retpath=TEST_RETPATH,
            headers=self.get_headers(cookie=TEST_COOKIE_WITH_SESSGUARD),
        )
        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
            cookies=[
                'Session_id=3:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'sessionid2=3:sslsession; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'sessguard=1.sessguard; Domain=.passport-test.yandex.ru; Secure; HttpOnly; Path=/',
                'yandex_login=test-user; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/',
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
        )
        self.check_blackbox_call(sessguard='1.old_sessguard')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('updated', uid=str(TEST_UID)),
        ])

    def test_update_cookies_sessguard_not_updated(self):
        """
        По какой-то причине ЧЯ решил не подновлять паспортный сесгард
        """
        self.env.blackbox.set_response_value(
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
                prolong_cookies=True,
                sessguard_hosts=[],
            ),
        )
        resp = self.make_request(
            retpath=TEST_RETPATH,
            headers=self.get_headers(cookie=TEST_COOKIE_WITH_SESSGUARD),
        )
        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
            cookies=[
                'Session_id=3:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'sessionid2=3:sslsession; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'yandex_login=test-user; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/',
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
        )
        self.check_blackbox_call(sessguard='1.old_sessguard')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('updated', uid=str(TEST_UID)),
        ])

    def test_update_sessguard_cookies_not_updated(self):
        """
        ЧЯ решил не подновлять сессионную куку (а только сесгард)
        """
        self.env.blackbox.set_response_value(
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
                prolong_cookies=False,
                sessguard_hosts=['passport-test.yandex.ru'],
            ),
        )
        resp = self.make_request(
            retpath=TEST_RETPATH,
            headers=self.get_headers(cookie=TEST_COOKIE_WITH_SESSGUARD),
        )
        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
            cookies=[
                'sessguard=1.sessguard; Domain=.passport-test.yandex.ru; Secure; HttpOnly; Path=/',
            ],
        )
        self.check_blackbox_call(sessguard='1.old_sessguard')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('updated'),
        ])

    def test_update_multicookie_with_invalid_user_session(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                default_user_status=BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                ip=TEST_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                crypt_password='1:pwd',
                ttl=0,
                prolong_cookies=True,
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            cookies=[
                'Session_id=3:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'sessionid2=3:sslsession; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
            ],
        )
        self.check_blackbox_call(extra_guard_host=None)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('updated'),
        ])

    def test_update_with_cookie_lah(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                ip=TEST_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                crypt_password='1:pwd',
                ttl=5,
                prolong_cookies=True,
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        with mock.patch.object(
            cookie_lah.CookieLAH,
            'pack',
            mock.Mock(return_value=COOKIE_LAH_VALUE),
        ):
            resp = self.make_request(retpath=TEST_RETPATH)

        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
            cookies=[
                'Session_id=3:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'sessionid2=3:sslsession; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'yandex_login=test-user; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/',
                EXPECTED_MDA2_BEACON_COOKIE,
                EXPECTED_LAH_COOKIE,
            ],
        )
        self.check_blackbox_call()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('updated', uid=str(TEST_UID)),
        ])

    def test_force_update_cookie_valid(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                ip=TEST_IP,
                crypt_password='1:pwd',
                ttl=0,
                prolong_cookies=True,
            ),
        )
        resp = self.make_request(
            retpath=TEST_RETPATH,
            headers=self.get_headers(cookie=TEST_COOKIE_WITH_DUPLICATES),
        )
        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
            cookies=[
                'Session_id=3:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'sessionid2=3:sslsession; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'yandex_login=test-user; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/',
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
        )
        self.check_blackbox_call(force_resign=True)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('updated', uid=str(TEST_UID), session_cookie_count='2'),
        ])

    def test_force_update_cookie_invalid(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_EXPIRED_STATUS,
            ),
        )
        resp = self.make_request(
            retpath=TEST_RETPATH,
            headers=self.get_headers(cookie=TEST_COOKIE_WITH_SESSGUARD_AND_DUPLICATES),
        )
        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
            cookies=[
                'Session_id=; Domain=.yandex.ru; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure; HttpOnly; Path=/',
                'sessionid2=; Domain=.yandex.ru; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure; HttpOnly; Path=/',
                'sessguard=; Domain=.passport-test.yandex.ru; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure; HttpOnly; Path=/',
            ],
        )
        self.check_blackbox_call(force_resign=True, sessguard='1.old_sessguard')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry(
                'updated',
                _exclude=['auth_id'],
                session_cookie_count='2',
                is_session_valid='0',
            ),
        ])

    def test_update_cookies_with_extra_sessguard_container(self):
        self.env.blackbox.set_response_value(
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
                prolong_cookies=True,
                sessguard_hosts=['passport-test.yandex.ru', TEST_RETPATH_HOST],
            ),
        )
        self.env.blackbox.set_response_value('sign', blackbox_sign_response())
        resp = self.make_request(
            retpath=TEST_RETPATH,
            headers=self.get_headers(cookie=TEST_COOKIE_WITH_SESSGUARD),
        )
        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
            cookies=[
                'Session_id=3:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'sessionid2=3:sslsession; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'sessguard=1.sessguard; Domain=.passport-test.yandex.ru; Secure; HttpOnly; Path=/',
                'yandex_login=test-user; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/',
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
            service_guard_container='123.abc',
        )
        self.check_blackbox_call(sessguard='1.old_sessguard', sign_container=True)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('updated', uid=str(TEST_UID)),
        ])

    def test_update_cookie_force_prolong(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                ip=TEST_IP,
                crypt_password='1:pwd',
                ttl=0,
                prolong_cookies=True,
            ),
        )
        resp = self.make_request(retpath=TEST_RETPATH, force_prolong='yes')
        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
            cookies=[
                'Session_id=3:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'sessionid2=3:sslsession; Domain=.yandex.ru; Secure; HttpOnly; Path=/',
                'yandex_login=test-user; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/',
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
        )
        self.check_blackbox_call(force_resign=True)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('updated', uid=str(TEST_UID)),
        ])

    def test_blackbox_sessionid_wrong_guard_error(self):
        """ЧЯ вернул WRONG_GUARD - ошибка обрабатывается"""
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
            ),
        )
        resp = self.make_request(retpath=TEST_RETPATH)
        self.assert_error_response(resp, retpath=TEST_RETPATH, error_codes=['sessguard.invalid'])
