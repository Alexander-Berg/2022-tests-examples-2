# -*- coding: utf-8 -*-

import datetime as _datetime

from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_UID = 1
TEST_ANOTHER_UID = 999
TEST_LOGIN = 'testlogin'
TEST_USER_LOGIN = 'TestLogin'
TEST_SOCIAL_LOGIN = 'uid-blah'
TEST_LITE_LOGIN = 'user@domain.com'
TEST_NEOPHONISH_LOGIN = 'nphne-xxx'
TEST_IP = '3.3.3.3'
TEST_USER_AGENT = 'curl'
TEST_USER_LANGUAGE = 'ru'
TEST_ACCEPT_LANGUAGE = 'ru'
TEST_REFERER = 'http://test.yandex.com/referer'
TEST_SERVICE = 'test'
TEST_SERVICE_SID = '672'
TEST_ORIGIN = 'test-origin'
TEST_RETPATH = 'http://test.yandex.ru'
TEST_FRETPATH = 'http://test.yandex.com'
TEST_HOST = 'passport-test.yandex.ru'
TEST_USER_MESSAGES = [6666, 6667, 6668]
TEST_PHONE_NUMBER = '+79261234567'
TEST_PHONE_NUMBER_OBJECT = PhoneNumber.parse(TEST_PHONE_NUMBER)
TEST_FIRSTNAME = 'testfirstname'
TEST_LASTNAME = 'testlastname'
TEST_GLOBAL_LOGOUT_DATETIME = DatetimeNow(
    convert_to_datetime=True,
    timestamp=_datetime.datetime.fromtimestamp(1),
)


TEST_INVALID_PASSWORD = 'wrong_password'
TEST_PASSWORD = 'aaa1bbbccc'
TEST_PASSWORD_QUALITY = 80
TEST_PASSWORD_HASH = '1:$1$4GcNYVh5$4bdwYxUKcvcYHUXbnGFOA1'
TEST_PASSWORD_LIKE_NORMALIZED_LOGIN = 'my-login'
TEST_PASSWORD_LIKE_NORMALIZED_LOGIN_HASH = '1:$1$4GcNYVh5$87dzvdLxQ6z3jODMTWUhK.'
TEST_LOGIN_FOR_NORMALIZATION = 'my.login'

# Пароль сложности 50
TEST_NOT_STRONG_PASSWORD = 'asdfglkjha'
TEST_NOT_STRONG_PASSWORD_QUALITY = 50
TEST_NOT_STRONG_PASSWORD_LENGTH = len(TEST_NOT_STRONG_PASSWORD)
TEST_NOT_STRONG_PASSWORD_CLASSES_NUMBER = 1
TEST_NOT_STRONG_PASSWORD_SEQUENCES_NUMBER = 2
TEST_NOT_STRONG_PASSWORD_IS_SEQUENCE = False
TEST_NOT_STRONG_PASSWORD_IS_WORD = False

# Пароль сложности 0
TEST_WEAK_PASSWORD = 'qwerty'
TEST_WEAK_PASSWORD_QUALITY = 0
TEST_WEAK_PASSWORD_HASH = '1:$1$y0aXFE9w$JqrpPZ74WT1Hi/Mb53cTe.'
TEST_WEAK_PASSWORD_LENGTH = len(TEST_WEAK_PASSWORD)
TEST_WEAK_PASSWORD_CLASSES_NUMBER = 1
TEST_WEAK_PASSWORD_SEQUENCES_NUMBER = 1
TEST_WEAK_PASSWORD_IS_SEQUENCE = True
TEST_WEAK_PASSWORD_IS_WORD = True

TEST_AUTH_ID = '123:1422501443:126'
TEST_OLD_AUTH_ID = '123:0000000:555'

TEST_PROVIDER = {'code': 'fb', 'name': 'facebook', 'id': 2}
TEST_SOCIAL_DISPLAY_NAME = {
    'name': 'Some User',
    'social': {
        'provider': TEST_PROVIDER['code'],
        'profile_id': 123456,
    },
    'default_avatar': '',
}
TEST_SOCIAL_DISPLAY_NAME_AFTER_COMPLETION = {
    'name': 'Some User',
    'default_avatar': '',
}

TEST_LITE_DISPLAY_NAME = {
    'name': '',
    'default_avatar': '',
}

TEST_NEOPHONISH_DISPLAY_NAME = {
    'name': 'Firstname Lastname',
    'default_avatar': '',
}

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


EXPECTED_SESSIONID_COOKIE = 'Session_id=%(value)s; Domain=%(domain)s; Secure; HttpOnly; Path=/' % SESSION['session']
EXPECTED_SESSIONID_SECURE_COOKIE = ('sessionid2=%(value)s; Domain=%(domain)s; '
                                    'Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'
                                    % SESSION['sslsession'])

TEST_COOKIE_AGE = 123456
TEST_COOKIE_TIMESTAMP = 1383144488
TEST_COOKIE_L = ('VFUrAHh8fkhQfHhXW117aH4GB2F6UlZxWmUHQmEBdxwEHhZBDyYxVUYCIxEcJEYfFTpdBF9dGRMuJHU4HwdSNQ=='
                 '.%s.1002323.298169.6af3100a8920a270bd9a933bbcd48181') % TEST_COOKIE_TIMESTAMP

COOKIE_YP_VALUE = '1692607429.udn.bG9naW4%3D%0A'
EXPECTED_YP_COOKIE = u'yp=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % COOKIE_YP_VALUE

COOKIE_YS_VALUE = 'udn.bG9naW4%3D%0A'
EXPECTED_YS_COOKIE = u'ys=%s; Domain=.yandex.ru; Secure; Path=/' % COOKIE_YS_VALUE

COOKIE_L_VALUE = TEST_COOKIE_L
EXPECTED_L_COOKIE = u'L=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/' % COOKIE_L_VALUE

COOKIE_LAH_VALUE = 'OG5EOF8wU_bOAGhjXFp7YXkHAGB9UVFyB2IACGZedV4DWl8FWXF5BgJXYFVzYQVKV3kFVlpaU0p2f31iRkZRYQ.1473090908.1002323.1.2fe2104fff29aa69e867d7d1ea601470'
EXPECTED_LAH_COOKIE = u'lah=%s; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; HttpOnly; Path=/' % COOKIE_LAH_VALUE

EXPECTED_YANDEX_LOGIN_COOKIE = 'yandex_login=%s; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/'

TEST_YANDEXUID_COOKIE = 'yandexuid'
TEST_YANDEX_GID_COOKIE = 'yandex_gid'
TEST_FUID01_COOKIE = 'fuid'
TEST_COOKIE_MY = 'YycCAAYA'
COOKIE_MY_VALUE_WITH_AUTH_SESSION_POLICY_PERMANENT = 'YycCAAY2AQEA'
TEST_SESSIONID = '0:old-session'
TEST_SSL_SESSIONID = '0:old-sslsession'

TEST_SESSIONID_COOKIE = 'Session_id=%s;' % TEST_SESSIONID

TEST_USER_COOKIES_WITHOUT_SSLSESSION = 'Session_id=%s; yandexuid=%s; yandex_gid=%s; fuid01=%s; my=%s; L=%s;' % (
    TEST_SESSIONID, TEST_YANDEXUID_COOKIE, TEST_YANDEX_GID_COOKIE, TEST_FUID01_COOKIE, TEST_COOKIE_MY, TEST_COOKIE_L,
)

TEST_USER_COOKIES = 'Session_id=%s; sessionid2=%s; yandexuid=%s; yandex_gid=%s; fuid01=%s; my=%s; L=%s;' % (
    TEST_SESSIONID, TEST_SSL_SESSIONID, TEST_YANDEXUID_COOKIE, TEST_YANDEX_GID_COOKIE, TEST_FUID01_COOKIE, TEST_COOKIE_MY, TEST_COOKIE_L,
)

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE

FRODO_RESPONSE_OK = '<spamlist></spamlist>'
FRODO_RESPONSE_PROBABLY_SPAM_USER = '<spamlist><change_pass login="%s" weight="85" /></spamlist>' % TEST_LOGIN
FRODO_RESPONSE_SPAM_USER = '<spamlist><spam_user login="%s" weight="85" /></spamlist>' % TEST_LOGIN
FRODO_RESPONSE_BAD_USER = '<spamlist><spam_user login="%s" weight="100" /></spamlist>' % TEST_LOGIN

TEST_REQUEST_ID1 = 'test-request-id-1'

TEST_APP_ID = 'app-id'

TEST_OPERATION_TTL = _datetime.timedelta(seconds=360)
TEST_PHONE_OPERATION_ID1 = 1

TEST_ENCRYPTION_KEY_NUMBER = 1
TEST_ENCRYPTION_KEY = (u'0' * 32).encode('ascii')

TEST_CONSUMER_IP = '127.0.0.1'
TEST_CONSUMER = 'dev'

TEST_BILLING_TOKEN = 'billing_token'

TEST_DEFAULT_COMPLETION_URL = 'https:/passport.yandex.ru/profile/upgrade'
