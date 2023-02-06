# -*- coding: utf-8 -*-
import mock
from nose.tools import ok_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_LOGIN,
    TEST_OTHER_LOGIN,
    TEST_OTHER_UID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.faker import FakeTrackIdGenerator


TEST_OLD_HOST = 'passport-test.yandex.ru'
TEST_NEW_HOST = 'passport-test.yandex.ua'
TEST_RETPATH = 'http://yandex.ru'
TEST_OLD_DOMAIN = '.yandex.ru'
TEST_NEW_DOMAIN = '.yandex.ua'

SESSION = {
    'session': {
        'domain': TEST_OLD_DOMAIN,
        'expires': 0,
        'value': '2:session',
    },
    'sslsession': {
        'domain': TEST_OLD_DOMAIN,
        'expires': 1370874827,
        'value': '2:sslsession',
    },
}
TEST_SESSIONID = SESSION['session']['value']
TEST_SSL_SESSIONID = SESSION['sslsession']['value']

EXPECTED_SESSIONID_COOKIE = 'Session_id=%(value)s; Domain=%(domain)s; Secure; HttpOnly; Path=/' % SESSION['session']
EXPECTED_SESSIONID_SECURE_COOKIE = (
    'sessionid2=%(value)s; Domain=%(domain)s; '
    'Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/' % SESSION['sslsession']
)

TEST_COOKIE_YP = '1692607429.udn.bG9naW4%3D%0A'
EXPECTED_YP_COOKIE = 'yp=%s; Domain=%s; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % (
    TEST_COOKIE_YP,
    TEST_OLD_DOMAIN,
)

TEST_COOKIE_YS = 'udn.bG9naW4%3D%0A'
EXPECTED_YS_COOKIE = 'ys=%s; Domain=%s; Secure; Path=/' % (TEST_COOKIE_YS, TEST_OLD_DOMAIN)

TEST_COOKIE_TIMESTAMP = 1383144488
TEST_COOKIE_L = (
    'VFUrAHh8fkhQfHhXW117aH4GB2F6UlZxWmUHQmEBdxwEHhZBDyYxVUYCIxEcJEYfFTpdBF9dGRMuJHU4HwdSNQ=='
    '.%s.1002323.298169.6af3100a8920a270bd9a933bbcd48181' % TEST_COOKIE_TIMESTAMP
)
EXPECTED_L_COOKIE = 'L=%s; Domain=%s; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/' % (
    TEST_COOKIE_L,
    TEST_OLD_DOMAIN,
)

TEST_YANDEX_LOGIN = 'pdd@%D0%BE%D0%BA%D0%BD%D0%B0.%D1%80%D1%84'  # pdd@окна.рф
EXPECTED_YANDEX_LOGIN_COOKIE = 'yandex_login=%s; Domain=%s; Max-Age=31536000; Secure; Path=/' % (TEST_YANDEX_LOGIN, TEST_OLD_DOMAIN)

TEST_YANDEX_GID = 'yandex_gid'
EXPECTED_YANDEX_GID_COOKIE = 'yandex_gid=%s; Domain=%s; Expires=Fri, 12 May 2017 16:53:20 GMT; Secure; Path=/' % (
    TEST_YANDEX_GID,
    TEST_OLD_DOMAIN,
)

TEST_COOKIE_MY = 'YycCAAYA'
EXPECTED_MY_COOKIE = 'my=%s; Domain=%s; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % (
    TEST_COOKIE_MY,
    TEST_OLD_DOMAIN,
)

TEST_YANDEXUID = 'yandexuid'
TEST_OLD_SESSIONID = '0:old-session'
TEST_OLD_SSL_SESSIONID = '0:old-sslsession'

TEST_USER_COOKIES_WITHOUT_SSLSESSION = (
    'Session_id=%s; yandexuid=%s; yandex_gid=%s; yandex_login=%s; my=%s; L=%s; yp=%s; ys=%s;' % (
        TEST_SESSIONID,
        TEST_YANDEXUID,
        TEST_YANDEX_GID,
        TEST_YANDEX_LOGIN,
        TEST_COOKIE_MY,
        TEST_COOKIE_L,
        TEST_COOKIE_YP,
        TEST_COOKIE_YS,
    )
)
TEST_USER_COOKIES = '%s sessionid2=%s;' % (
    TEST_USER_COOKIES_WITHOUT_SSLSESSION,
    TEST_SSL_SESSIONID,
)

EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=1400000000000; Domain=.passportdev.yandex.ua; Secure; Path=/'


def build_headers(host=TEST_OLD_HOST, cookie=TEST_USER_COOKIES):
    return mock_headers(
        host=host,
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        cookie=cookie,
    )


@with_settings_hosts
class TestInfectionIntegrational(BaseBundleTestViews):
    submit_url = '/1/bundle/track/init_infected/?consumer=dev'
    commit_url = '/1/bundle/session/?consumer=dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['track.initialize_infected', 'session.create'])

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.time_patch = mock.patch('time.time', return_value=14 * 10 ** 8)
        self.time_patch.start()

        self.setup_blackbox_responses()
        self.setup_statbox_templates()

    def tearDown(self):
        self.time_patch.stop()
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.time_patch
        del self.track_id_generator

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            uid=str(TEST_UID),
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'initialize_infected_track',
            consumer='dev',
            mode='initialize_infected_track',
            yandexuid=TEST_YANDEXUID,
        )
        self.env.statbox.bind_entry(
            'cookie_set',
            cookie_version='3',
            ttl='5',
            mode='any_auth',
            captcha_passed='0',
            action='cookie_set',
            ip=TEST_USER_IP,
            input_login=TEST_LOGIN,
            user_agent=TEST_USER_AGENT,
            session_method='create',
            uids_count='1',
            retpath=TEST_RETPATH,
            ip_country='us',
            person_country='ru',
        )

    def setup_blackbox_responses(self):
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID, login=TEST_LOGIN),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    ttl='5',
                ),
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(domain=TEST_NEW_DOMAIN),
        )

    def make_request(self, url, data, headers):
        return self.env.client.post(
            url,
            data=data,
            headers=headers,
        )

    def get_expected_cookies(self):
        cookies = [
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_YANDEX_LOGIN_COOKIE,
            EXPECTED_YP_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_L_COOKIE,
            EXPECTED_YANDEX_GID_COOKIE,
            EXPECTED_MY_COOKIE,
            EXPECTED_SESSIONID_SECURE_COOKIE,
            EXPECTED_MDA2_BEACON_COOKIE,
        ]

        return [
            cookie.replace(TEST_OLD_DOMAIN, TEST_NEW_DOMAIN)
            for cookie in cookies
        ]

    def assert_auth_log_empty(self):
        ok_(not self.env.auth_handle_mock.called)

    def assert_statbox_ok(self):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('initialize_infected_track'),
            self.env.statbox.entry('cookie_set'),
        ])

    def test_ok(self):
        rv = self.make_request(
            url=self.submit_url,
            data={
                'retpath': TEST_RETPATH,
            },
            headers=build_headers(host=TEST_OLD_HOST),
        )
        self.assert_ok_response(rv, track_id=self.track_id)

        rv = self.make_request(
            url=self.commit_url,
            data={
                'track_id': self.track_id,
            },
            headers=build_headers(host=TEST_NEW_HOST, cookie='fuid=123'),
        )
        self.assert_ok_response(
            rv,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            retpath=TEST_RETPATH,
            cookies=self.get_expected_cookies(),
            default_uid=TEST_UID,
        )
        self.assert_auth_log_empty()
        self.assert_statbox_ok()
