# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import *
from passport.backend.api.views.bundle.constants import X_TOKEN_OAUTH_SCOPE
from passport.backend.core import authtypes
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_lrandoms_response,
    blackbox_oauth_response,
    blackbox_userinfo_response,
)
from passport.backend.core.cookies import (
    cookie_l,
    cookie_lah,
    cookie_y,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator


TEST_LOGIN = 'test'
TEST_HOST = '.yandex.ru'
TEST_USER_IP = '127.0.0.1'
TEST_USER_AGENT = 'curl'
TEST_YANDEXUID_COOKIE = 'cookie_yandexuid'
TEST_USER_COOKIES = 'yandexuid=%s' % TEST_YANDEXUID_COOKIE
TEST_REFERER = 'http://passportdev-python.yandex.ru/passport?mode=passport'
TEST_RETPATH = 'http://yandex.ru'
TEST_OAUTH_TOKEN = 'test-x-token'
TEST_OAUTH_HEADER = 'OAuth %s' % TEST_OAUTH_TOKEN
TEST_OAUTH_SCOPE = X_TOKEN_OAUTH_SCOPE

EXPECTED_SESSIONID_COOKIE = u'Session_id=2:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/'
EXPECTED_SESSIONID_SECURE_COOKIE = u'sessionid2=2:sslsession; Domain=.yandex.ru; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'
EXPECTED_AUTH_ID = '123:1422501443:126'
COOKIE_L_VALUE = 'VFV5DX94f0RRfXFTXVl5YH8GB2F6VlJ7XzNUTyYaIB1HBlpZBSd6QFkfOAJ7OgEACi5QFlIEGUM+KjlhRgRXZw==.1376993918.1002323.298859.ee75287c1d\
fd8b073375aee93158eb5b'
EXPECTED_L_COOKIE = u'L=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/' % COOKIE_L_VALUE

COOKIE_YP_VALUE = '1692607429.udn.bG9naW4%3D%0A'
EXPECTED_YP_COOKIE = u'yp=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % COOKIE_YP_VALUE

COOKIE_YS_VALUE = 'udn.bG9naW4%3D%0A'
EXPECTED_YS_COOKIE = u'ys=%s; Domain=.yandex.ru; Secure; Path=/' % COOKIE_YS_VALUE

EXPECTED_YANDEX_LOGIN_COOKIE = u'yandex_login=test; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/'

TEST_SESSIONID = '0:old-session'
TEST_USER_COOKIES_WITH_SESSION = TEST_USER_COOKIES + ';Session_id=%s' % TEST_SESSIONID

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE


class BaseXTokenIntegrationalTestcase(BaseBundleTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(grants={
                'auth_by_token': ['base'],
                'session': ['create'],
            }),
        )
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)

        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(login=TEST_LOGIN),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(login=TEST_LOGIN, scope=TEST_OAUTH_SCOPE, login_id=TEST_LOGIN_ID),
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        self._cookie_l_pack = mock.Mock(return_value=COOKIE_L_VALUE)
        self._cookie_lah_pack = mock.Mock(return_value=COOKIE_LAH_VALUE)

        self._cookie_ys_pack = mock.Mock(return_value=COOKIE_YS_VALUE)
        self._cookie_yp_pack = mock.Mock(return_value=COOKIE_YP_VALUE)

        self.patches = [
            mock.patch.object(
                cookie_l.CookieL,
                'pack',
                self._cookie_l_pack,
            ),
            mock.patch.object(
                cookie_lah.CookieLAH,
                'pack',
                self._cookie_lah_pack,
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
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
            self.track_id_generator,
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches
        del self._cookie_l_pack
        del self._cookie_lah_pack
        del self._cookie_yp_pack
        del self._cookie_ys_pack

    def make_create_session_request(self):
        return self.env.client.post(
            '/1/bundle/session/?consumer=dev',
            data={
                'track_id': self.track_id,
            },
            headers=mock_headers(
                host=TEST_HOST,
                user_ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
                cookie=TEST_USER_COOKIES,
                referer=TEST_REFERER,
            ),
        )

    def make_x_token_request(self):
        return self.env.client.post(
            '/1/bundle/auth/token/?consumer=dev',
            data={
                'type': 'x-token',
                'retpath': TEST_RETPATH,
            },
            headers=mock_headers(
                user_ip=TEST_USER_IP,
                authorization=TEST_OAUTH_HEADER,
            ),
        )

    def assert_antifraud_called(self):
        self.env.antifraud_logger.assert_equals([
            self.env.antifraud_logger.entry(
                '',  # noop, не объявлен шаблон, поэтому ничего и не передал
                auth_source=authtypes.AUTH_SOURCE_XTOKEN,  # ассерты здесь на антифрод в основном из-за этого параметра
                authid=TEST_AUTH_ID,
                channel='auth',
                external_id='track-{}'.format(self.track_id),
                ip=TEST_USER_IP,
                lah_uids='',
                login_id=TEST_AUTH_ID,
                request='auth',
                retpath=TEST_RETPATH,
                service_id='login',
                status='OK',
                sub_channel='login',
                t=TimeNow(as_milliseconds=True),
                tskv_format='antifraud',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT,
                yandexuid=TEST_YANDEXUID_COOKIE,
                cookie_auth='true',
            )
        ])

    def assert_createsession_called(self, call_index=2):
        self.env.blackbox.requests[call_index].assert_query_equals({
            'method': 'createsession',
            'lang': '1',
            'have_password': '0',
            'ver': '3',
            'uid': '1',
            'format': 'json',
            'keyspace': 'yandex.ru',
            'is_lite': '0',
            'ttl': '5',
            'userip': TEST_USER_IP,
            'host_id': '7f',
            'create_time': TimeNow(),
            'auth_time': TimeNow(as_milliseconds=True),
            'guard_hosts': 'passport-test.yandex.ru,yandex.ru',
            'request_id': mock.ANY,
            'login_id': TEST_LOGIN_ID,
            'get_login_id': 'yes',
        })

    def get_expected_cookies(self):
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
            EXPECTED_LAH_COOKIE,
        ]
        return sorted(specific + cookies)


@with_settings_hosts(
    PERMANENT_COOKIE_TTL=5,
    PASSPORT_BASE_URL_TEMPLATE='https://passport-test.yandex.%(tld)s',
    PASSPORT_SUBDOMAIN='passport-test',
    IS_INTRANET=False,
)
class TestBaseXTokenIntegrational(BaseXTokenIntegrationalTestcase):

    def test_ok(self):
        resp = self.make_x_token_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            passport_host='https://passport-test.yandex.ru',
        )

        resp = self.make_create_session_request()
        eq_(resp.status_code, 200)
        rv = json.loads(resp.data)
        eq_(rv['status'], 'ok')
        eq_(sorted(rv['cookies']), self.get_expected_cookies())
        self.assert_createsession_called()
        self.assert_antifraud_called()
