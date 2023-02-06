# -*- coding: utf-8 -*-
import mock
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
import six


TEST_UID = 1
TEST_LOGIN = 'test-user'
TEST_IP = '3.3.3.3'
TEST_USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; LG-H818 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.95 Mobile Safari/537.36'
TEST_UUID = 'uuid-abcd-efgh-ijkl'

TEST_PACKED_CONTAINER = 'c-o-n-t-a-i-n-e-r'

TEST_TIME_NOW = 1538000000

TEST_MASTER_DOMAIN = 'yandex.ru'
TEST_SLAVE_DOMAIN = 'kinopoisk.ru'
TEST_HOST = 'passport-test.yandex.ru'
TEST_TARGET_HOST = 'beta.kinopoisk.ru'
TEST_RETPATH = 'https://my.kinopoisk.ru'
TEST_COOKIE_CHECK_VALUE = 1234567890
TEST_SCRIPT_NONCE = 'abcdeffdeadbeef'

TEST_SESSIONID_COOKIE_TEMPLATE = 'Session_id=3:session; Domain=.%s; Secure; HttpOnly; Path=/'
TEST_EXPECTED_SESSIONID_COOKIE_MASTER = TEST_SESSIONID_COOKIE_TEMPLATE % TEST_MASTER_DOMAIN
TEST_EXPECTED_SESSIONID_COOKIE_SLAVE = TEST_SESSIONID_COOKIE_TEMPLATE % TEST_SLAVE_DOMAIN
TEST_EXPECTED_NOAUTH_SESSIONID_COOKIE_SLAVE = 'Session_id=noauth:%s; Domain=.%s; Max-Age=7200; Secure; HttpOnly; Path=/' % (TEST_TIME_NOW, TEST_SLAVE_DOMAIN)

TEST_SESSIONID_SECURE_COOKIE_TEMPLATE = 'sessionid2=3:sslsession; Domain=.%s; Secure; HttpOnly; Path=/'
TEST_EXPECTED_SESSIONID_SECURE_COOKIE_MASTER = TEST_SESSIONID_SECURE_COOKIE_TEMPLATE % TEST_MASTER_DOMAIN

TEST_YANDEX_LOGIN_COOKIE_TEMPLATE = 'yandex_login=test; Domain=.%s; Max-Age=31536000; Secure; Path=/'
TEST_EXPECTED_YANDEX_LOGIN_COOKIE_MASTER = TEST_YANDEX_LOGIN_COOKIE_TEMPLATE % TEST_MASTER_DOMAIN
TEST_EXPECTED_YANDEX_LOGIN_COOKIE_SLAVE = TEST_YANDEX_LOGIN_COOKIE_TEMPLATE % TEST_SLAVE_DOMAIN
TEST_EXPECTED_NOAUTH_YANDEX_LOGIN_SLAVE = 'yandex_login=; Domain=.%s; Max-Age=31536000; Secure; Path=/' % TEST_SLAVE_DOMAIN

TEST_COOKIE_LAH_VALUE = 'OG5EOF8wU_bOAGhjXFp7YXkHAGB9UVFyB2IACGZedV4DWl8FWXF5BgJXYFVzYQVKV3kFVlpaU0p2f31iRkZRYQ.1473090908.1002323.1.2fe2104fff29aa69e867d7d1ea601470'
TEST_EXPECTED_LAH_COOKIE_MASTER = 'lah=%s; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; HttpOnly; Path=/' % TEST_COOKIE_LAH_VALUE

TEST_MDA2_DOMAINS_TEMPLATE = 'mda2_domains=%s; Domain=.passport-test.%s; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/'
TEST_MDA2_DOMAINS_VALUE = ','.join(['edadeal.ru', TEST_SLAVE_DOMAIN])
TEST_EXPECTED_MDA2_DOMAINS_MASTER = TEST_MDA2_DOMAINS_TEMPLATE % (TEST_MDA2_DOMAINS_VALUE, TEST_MASTER_DOMAIN)

TEST_YANDEXUID_VALUE = '1046714081386936400'
TEST_YANDEXUID_TEMPLATE = 'yandexuid=%s; Domain=.%s; Expires=Sat, 23 Sep 2028 22:13:20 GMT; Secure; Path=/'
TEST_EXPECTED_YANDEXUID_SLAVE = TEST_YANDEXUID_TEMPLATE % (TEST_YANDEXUID_VALUE, TEST_SLAVE_DOMAIN)

TEST_I_VALUE = 'some-cool-stuff'
TEST_I_TEMPLATE = 'i=%s; Domain=.%s; Expires=Sat, 23 Sep 2028 22:13:20 GMT; Secure; HttpOnly; Path=/'
TEST_EXPECTED_I_SLAVE = TEST_I_TEMPLATE % (TEST_I_VALUE, TEST_SLAVE_DOMAIN)

TEST_YS_COOKIE_TEMPLATE = 'ys=%s; Domain=.%s; Secure; Path=/'
TEST_COOKIE_YS_VALUE = 'udn.bG9naW4%3D%0A'
TEST_EXPECTED_YS_COOKIE_MASTER = TEST_YS_COOKIE_TEMPLATE % (TEST_COOKIE_YS_VALUE, TEST_MASTER_DOMAIN)
TEST_EXPECTED_YS_COOKIE_SLAVE = TEST_YS_COOKIE_TEMPLATE % (TEST_COOKIE_YS_VALUE, TEST_SLAVE_DOMAIN)

TEST_CUSTOM_YS_COOKIE_VALUE = 'ac.0#bdst.0#udn.unknown'
TEST_CUSTOM_YS_COOKIE = TEST_YS_COOKIE_TEMPLATE % (TEST_CUSTOM_YS_COOKIE_VALUE, TEST_SLAVE_DOMAIN)
TEST_MERGED_COOKIE_YS_VALUE = 'ac.0#bdst.0#udn.bG9naW4%3D%0A'

TEST_MY_COOKIE_TEMPLATE = 'my=%s; Domain=.%s; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/'
TEST_COOKIE_MY_VALUE = 'YwA='
TEST_EXPECTED_MY_COOKIE_SLAVE = TEST_MY_COOKIE_TEMPLATE % (TEST_COOKIE_MY_VALUE, TEST_SLAVE_DOMAIN)
TEST_EXPECTED_ERASER_MY_COOKIE_SLAVE = TEST_MY_COOKIE_TEMPLATE % ('', TEST_SLAVE_DOMAIN)

TEST_YANDEX_GID_COOKIE_TEMPLATE = 'yandex_gid=%s; Domain=.%s; Expires=Sat, 25 Sep 2021 22:13:20 GMT; Secure; Path=/'
TEST_COOKIE_YANDEX_GID_VALUE = '213'
TEST_EXPECTED_YANDEX_GID_COOKIE_SLAVE = TEST_YANDEX_GID_COOKIE_TEMPLATE % (TEST_COOKIE_YANDEX_GID_VALUE, TEST_SLAVE_DOMAIN)

TEST_YP_COOKIE_TEMPLATE = 'yp=%s; Domain=.%s; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/'
TEST_COOKIE_YP_VALUE = '1853360000.udn.'
TEST_CUSTOM_COOKIE_YP_VALUE = '1853360001.udn.'
TEST_EXPECTED_YP_COOKIE_SLAVE = TEST_YP_COOKIE_TEMPLATE % (TEST_COOKIE_YP_VALUE, TEST_SLAVE_DOMAIN)

TEST_MERGED_YS_COOKIE = 'ys=%s; Domain=.%s; Path=/; Secure' % (TEST_MERGED_COOKIE_YS_VALUE, TEST_SLAVE_DOMAIN)
TEST_USER_COOKIES = '; '.join([
    'yandexuid=' + TEST_YANDEXUID_VALUE,
    'i=' + TEST_I_VALUE,
    'mda2_domains=edadeal.ru',
    'Session_id=0:old-session',
    'my=' + TEST_COOKIE_MY_VALUE,
    'yandex_gid=' + TEST_COOKIE_YANDEX_GID_VALUE,
])
TEST_SLAVE_DOMAIN_USER_COOKIES = 'yandexuid=%s; i=%s; ya_sess_id=0:old-session' % (TEST_YANDEXUID_VALUE, TEST_I_VALUE)
TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_MY = 'yandexuid=%s; i=%s; ya_sess_id=0:old-session; my=%s' % (TEST_YANDEXUID_VALUE, TEST_I_VALUE, TEST_COOKIE_MY_VALUE)
TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_YANDEX_GID = 'yandexuid=%s; i=%s; ya_sess_id=0:old-session; yandex_gid=%s' % (TEST_YANDEXUID_VALUE, TEST_I_VALUE, TEST_COOKIE_YANDEX_GID_VALUE)
TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_YP = 'yandexuid=%s; i=%s; ya_sess_id=0:old-session; yp=%s' % (TEST_YANDEXUID_VALUE, TEST_I_VALUE, TEST_CUSTOM_COOKIE_YP_VALUE)
TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_YS = 'yandexuid=%s; i=%s; ya_sess_id=0:old-session; ys=%s' % (TEST_YANDEXUID_VALUE, TEST_I_VALUE, TEST_CUSTOM_YS_COOKIE_VALUE)

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = 'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE
EXPECTED_SLAVE_MDA2_BEACON_COOKIE = 'mda2_beacon=%s; Domain=.kinopoisk.ru; Secure; Path=/' % MDA2_BEACON_VALUE
EXPECTED_MDA2_BEACON_COOKIE_WITH_EXPIRES = 'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % MDA2_BEACON_VALUE
EXPECTED_SLAVE_MDA2_BEACON_COOKIE_WITH_EXPIRES = 'mda2_beacon=%s; Domain=.kinopoisk.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % MDA2_BEACON_VALUE

TEST_USER_AGENT_WITH_SAMESITE_SUPPORT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'


@with_settings_hosts(
    BLACKBOX_FIELDS=(),
    BLACKBOX_ATTRIBUTES=(),
    PASSPORT_SUBDOMAIN='passport-test',
    MDA_EXPERIMENTAL_COOKIE_DENOMINATOR=1,
    MDA2_SLAVE_DOMAINS=['kinopoisk.ru'],
    CUSTOM_MDA_DOMAIN_CONFIGS={
        'kinopoisk.ru': {
            'cookies': {
                'yandexuid': 'yandexuid',
                'i': 'i',
            },
        },
    },
)
class BaseMda2Testcase(BaseBundleTestViews):
    consumer = 'dev'
    http_method = 'POST'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIES,
        user_ip=TEST_IP,
    )
    rebuilt_cookies_for_slave = False

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'mda2': ['*']}))
        self.setup_statbox_templates()

        self._uuid4_mock = mock.Mock()
        self._uuid4_mock.get_hex.return_value = TEST_SCRIPT_NONCE
        self._patches = [
            mock.patch('passport.backend.api.views.bundle.mda2.controllers.uuid.uuid4', mock.Mock(return_value=self._uuid4_mock)),
        ]
        for patch in self._patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self._patches):
            patch.stop()
        self.env.stop()

        del self._patches
        del self._uuid4_mock
        del self.env

    def setup_statbox_templates(self):
        raise NotImplementedError()

    def get_expected_cookies_for_master(self):
        return [
            TEST_EXPECTED_SESSIONID_COOKIE_MASTER,
            TEST_EXPECTED_SESSIONID_SECURE_COOKIE_MASTER,
            TEST_EXPECTED_YANDEX_LOGIN_COOKIE_MASTER,
            TEST_EXPECTED_LAH_COOKIE_MASTER,
            TEST_EXPECTED_YS_COOKIE_MASTER,
            TEST_EXPECTED_MDA2_DOMAINS_MASTER,
            EXPECTED_MDA2_BEACON_COOKIE,
        ]

    def get_expected_cookies_for_slave(
        self,
        ys_cookie=None,
        yp_cookie=None,
        my_cookie=None,
        yandex_gid_cookie=None,
    ):
        cookies = [
            TEST_EXPECTED_SESSIONID_COOKIE_SLAVE,
            TEST_EXPECTED_YANDEX_LOGIN_COOKIE_SLAVE,
            ys_cookie or TEST_EXPECTED_YS_COOKIE_SLAVE,
            TEST_EXPECTED_YANDEXUID_SLAVE,
            TEST_EXPECTED_I_SLAVE,
            EXPECTED_SLAVE_MDA2_BEACON_COOKIE,
        ]
        if yp_cookie is not None:
            cookies.append(yp_cookie)
        if my_cookie is not None:
            cookies.append(my_cookie)
        if yandex_gid_cookie is not None:
            cookies.append(yandex_gid_cookie)

        if self.rebuilt_cookies_for_slave:
            cookies = [self.rebuild_cookie(c) for c in cookies]

        return cookies

    def rebuild_cookie(self, cookie):
        bits = cookie.split('; ')
        try:
            del bits[bits.index('Secure')]
            bits.append('Secure')
        except ValueError:
            pass

        words = [
            #             PY3         PY2
            ('Expires=',  'expires=',  'expires='),
            ('HttpOnly',  'HttpOnly',  'httponly'),
            ('Secure',    'Secure',    'secure'),
        ]

        for bi, bit in enumerate(bits):
            for wi, word in enumerate(list(words)):
                if bit.startswith(word[0]):
                    bits[bi] = bit.replace(word[0], word[2 if six.PY2 else 1], 1)
                    del words[wi]
                    break

        return '; '.join(bits)
