# -*- coding: utf-8 -*-

TEST_UID = 1
TEST_LOGIN = 'testlogin'
TEST_IP = '3.3.3.3'
TEST_USER_AGENT = 'curl'
TEST_USER_LANGUAGE = 'ru'
TEST_ACCEPT_LANGUAGE = 'ru'
TEST_HOST = 'passport-test.yandex.ru'
TEST_AUTH_ID = '123:1422501443:126'
TEST_OLD_AUTH_ID = '123:0000000:555'

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

TEST_COOKIE_AGE = 123456
TEST_COOKIE_TIMESTAMP = 1383144488
TEST_COOKIE_L = ('VFUrAHh8fkhQfHhXW117aH4GB2F6UlZxWmUHQmEBdxwEHhZBDyYxVUYCIxEcJEYfFTpdBF9dGRMuJHU4HwdSNQ=='
                 '.%s.1002323.298169.6af3100a8920a270bd9a933bbcd48181') % TEST_COOKIE_TIMESTAMP
TEST_YANDEXUID_COOKIE = 'yandexuid'
TEST_YANDEX_GID_COOKIE = 'yandex_gid'
TEST_FUID01_COOKIE = 'fuid'
TEST_COOKIE_MY = 'YycCAAYA'
TEST_SESSIONID = '0:old-session'
TEST_SSL_SESSIONID = '0:old-sslsession'
TEST_SESSIONID_COOKIE = 'Session_id=%s;' % TEST_SESSIONID

TEST_USER_COOKIES = 'Session_id=%s; Session_id2=%s; yandexuid=%s; yandex_gid=%s; fuid01=%s; my=%s; L=%s;' % (
    TEST_SESSIONID, TEST_SSL_SESSIONID, TEST_YANDEXUID_COOKIE, TEST_YANDEX_GID_COOKIE, TEST_FUID01_COOKIE,
    TEST_COOKIE_MY, TEST_COOKIE_L,
)
