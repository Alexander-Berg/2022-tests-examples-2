# -*- coding: utf-8 -*-

from passport.backend.api.tests.views.bundle.auth.base_test_data import (
    COOKIE_LAH_VALUE,
    EXPECTED_LAH_COOKIE,
    TEST_DOMAIN,
    TEST_IP,
    TEST_LOGIN,
    TEST_SOCIAL_ALIAS,
    TEST_YANDEXUID_COOKIE,
)


TEST_USER_ENTERED_LOGIN = 'test.login'
TEST_PERSISTENT_TRACK_ID = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
TEST_UID = '1'
TEST_PERSISTENT_TRACK_KEY = TEST_PERSISTENT_TRACK_ID + TEST_UID
TEST_AUTH_BY_KEY_LINK_CREATE_TIMESTAMP = '2222'
TEST_HOST = 'passport.yandex.ru'
TEST_USER_AGENT = 'curl'

TEST_YANDEX_GID_COOKIE = 'yandex_gid'
TEST_FUID01_COOKIE = 'fuid'
TEST_COOKIE_MY = 'YycCAAYA'

TEST_COOKIE_TIMESTAMP = 1383141488
TEST_COOKIE_L = ('VFUrAHh8fkhQfHhXW117aH4GB2F6UlZxWmUHQmEBdxwEHhZBDyYxVUYCIxEcJEYfFTpdBF9dGRMuJHU4HwdSNQ=='
                 '.%s.1002323.298169.6af3100a8920a270bd9a933bbcd48181') % TEST_COOKIE_TIMESTAMP
TEST_USER_COOKIES = 'yandexuid=%s; yandex_gid=%s; fuid01=%s; my=%s; L=%s;' % (
    TEST_YANDEXUID_COOKIE,
    TEST_YANDEX_GID_COOKIE,
    TEST_FUID01_COOKIE,
    TEST_COOKIE_MY,
    TEST_COOKIE_L,
)

SESSION = {
    'session': {
        'domain': '.yandex.ru',
        'expires': 0,
        'value': '2:session',
    },
    'sslsession': {
        'domain': '.yandex.ru',
        'expires': 1370874827,
        'value': '2:sslsession',
    },
}

EXPECTED_SESSIONID_COOKIE = (
    'Session_id=%(value)s; Domain=%(domain)s; Secure; HttpOnly; Path=/'
    % SESSION['session']
)
EXPECTED_SESSIONID_SECURE_COOKIE = (
    'sessionid2=%(value)s; Domain=%(domain)s; '
    'Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'
    % SESSION['sslsession']
)


COOKIE_YP_VALUE = '1692607429.udn.bG9naW4%3D%0A'
EXPECTED_YP_COOKIE = 'yp=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % COOKIE_YP_VALUE

COOKIE_YS_VALUE = 'udn.bG9naW4%3D%0A'
EXPECTED_YS_COOKIE = 'ys=%s; Domain=.yandex.ru; Secure; Path=/' % COOKIE_YS_VALUE

COOKIE_L_VALUE = TEST_COOKIE_L
EXPECTED_L_COOKIE = 'L=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/' % COOKIE_L_VALUE

COOKIE_ED_VALUE = 'T:1381494432'
EXPECTED_ED_COOKIE = 'ed.%s=%s; path=/for; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Domain=.yandex.ru' % (
    TEST_DOMAIN,
    COOKIE_ED_VALUE,
)

EXPECTED_YANDEX_LOGIN_COOKIE = 'yandex_login=%s; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/' % TEST_LOGIN

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE
