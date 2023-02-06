# -*- coding: utf-8 -*-

import uuid

from passport.backend.api.tests.views.bundle.auth.base_test_data import *


TEST_USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; LG-H818 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.95 Mobile Safari/537.36'

TEST_USER_AGENT_INFO = {
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
    'historySupport': True,
    'localStorageSupport': True,
    'postMessageSupport': True,
    'CSP1Support': True,
    'CSP2Support': True,
    'SVGSupport': True,
    'WebPSupport': True,
}

TEST_RAW_ENV_FOR_PROFILE = {
    'ip': TEST_IP,
    'yandexuid': TEST_YANDEXUID_COOKIE,
    'user_agent_info': TEST_USER_AGENT_INFO,
}

TEST_ENCODED_ENV_FOR_PROFILE = {
    'region_id': '102630',
    'user_agent_info': {
        'BrowserName': '83',
        'OSFamily': '433',
    },
}

TEST_USER_LANGUAGE = 'ru'
TEST_ACCEPT_LANGUAGE = 'ru'
TEST_REFERER = 'http://test.yandex.com/referer'
TEST_SERVICE = 'test'
TEST_SERVICE_SID = '672'
TEST_ORIGIN = 'test-origin'
TEST_RETPATH = 'http://test.yandex.ru'
TEST_RETPATH_HOST = 'test.yandex.ru'
TEST_PDD_RETPATH = u'%s/for/%s/' % (TEST_RETPATH, TEST_DOMAIN)
TEST_CLEANED_PDD_RETPATH = 'http://test.yandex.ru/'
TEST_FRETPATH = 'http://test.yandex.com'
TEST_HOST = 'passport-test.yandex.ru'
TEST_USER_MESSAGES = [6666, 6667, 6668]

TEST_ALLOWED_PDD_HOSTS = ['a.yandex.ru', 'b.yandex.ru', 'a.yandex.com']

TEST_INVALID_PASSWORD = 'wrong_password'
TEST_PASSWORD = 'aaa1bbbccc'
TEST_PASSWORD_QUALITY = 80
TEST_PASSWORD_HASH = '1:$1$4GcNYVh5$4bdwYxUKcvcYHUXbnGFOA1'

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

TEST_USER_PHONE = '+79261234567'

TEST_SOCIAL_LOGIN = 'uid-bla'

TEST_OTP = '12345'
TEST_TOTP_CHECK_TIME = 123

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

PDD_SESSION_VALUE = ('2:1381494432.0.0.1130000000001038.8:1381494432362:1476061956:127.0.1.1.0.pochta:'
                     '39205.4469.8977724a7611fb9c4875b992abf8b9d1')

PDD_SESSION = {
    'session': {
        'domain': '.yandex.ru',
        'expires': 0,
        'value': PDD_SESSION_VALUE,
    },
    'sslsession': {
        'domain': '.yandex.ru',
        'expires': 1370874827,
        'value': PDD_SESSION_VALUE,
    },
}

EXPECTED_SESSGUARD_COOKIE = 'sessguard=1.sessguard; Domain=.passport-test.yandex.ru; Secure; HttpOnly; Path=/'
EXPECTED_SESSIONID_COOKIE = 'Session_id=%(value)s; Domain=%(domain)s; Secure; HttpOnly; Path=/' % SESSION['session']
EXPECTED_SESSIONID_SECURE_COOKIE = ('sessionid2=%(value)s; Domain=%(domain)s; '
                                    'Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'
                                    % SESSION['sslsession'])

EXPECTED_PDD_SESSIONID_COOKIE = ('Eda_id=%s; Domain=%s; Path=/for/%s; Secure; HttpOnly'
                                 % (PDD_SESSION['session']['value'],
                                    PDD_SESSION['session']['domain'],
                                    TEST_DOMAIN))
EXPECTED_PDD_SESSIONID_SECURE_COOKIE = ('edaid2=%s; Domain=%s; '
                                        'Expires=Mon, 10 Jun 2013 14:33:47 GMT; '
                                        'Secure; HttpOnly; Path=/for/%s'
                                        % (PDD_SESSION['sslsession']['value'],
                                           PDD_SESSION['sslsession']['domain'],
                                           TEST_DOMAIN))

COOKIE_YP_VALUE = '1692607429.udn.bG9naW4%3D%0A'
EXPECTED_YP_COOKIE = u'yp=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % COOKIE_YP_VALUE

COOKIE_YS_VALUE = 'udn.bG9naW4%3D%0A'
EXPECTED_YS_COOKIE = u'ys=%s; Domain=.yandex.ru; Secure; Path=/' % COOKIE_YS_VALUE

COOKIE_L_VALUE = TEST_COOKIE_L
EXPECTED_L_COOKIE = u'L=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/' % COOKIE_L_VALUE

COOKIE_ED_VALUE = 'T:1381494432'
EXPECTED_ED_COOKIE = u'ed.%s=%s; path=/for; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Domain=.yandex.ru' % (
                     TEST_DOMAIN,
                     COOKIE_ED_VALUE,
)

EXPECTED_YANDEX_LOGIN_COOKIE_TEMPLATE = 'yandex_login=%s; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/'
EXPECTED_YANDEX_LOGIN_COOKIE = EXPECTED_YANDEX_LOGIN_COOKIE_TEMPLATE % TEST_LOGIN

EXPECTED_PDD_YANDEX_LOGIN_COOKIE = 'yandex_login=%s; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/' % TEST_PDD_LOGIN

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE

TEST_PHONE_NUMBER_DUMP = {
    'original': TEST_PHONE_NUMBER.e164,
    'international': TEST_PHONE_NUMBER.international,
    'e164': TEST_PHONE_NUMBER.e164,
    'masked_original': mask_phone_number(TEST_PHONE_NUMBER.e164),
    'masked_international': mask_phone_number(TEST_PHONE_NUMBER.international),
    'masked_e164': mask_phone_number(TEST_PHONE_NUMBER.e164),
}

TEST_UFO_TIMEUUID = uuid.UUID('cb78b616-000b-11e5-b8cc-fc7bfc3c8e01')

TEST_PROFILE_MODEL = ('profile', 'test')

TEST_FEATURES_DESCRIPTION = [
    ('hour', 'num'),
    ('is_mobile', 'num'),
    ('ip_prob_1d', 'num'),
    ('ip_prob_1w', 'num'),
    ('ip_prob_1m', 'num'),
    ('is_weekend', 'num'),
]

TEST_THRESHOLD = 0.6

TEST_PROFILE_GOOD_ESTIMATE = 0.1
TEST_PROFILE_BAD_ESTIMATE = TEST_THRESHOLD + 0.1

TEST_MODEL_CONFIGS = {
    TEST_PROFILE_MODEL: {
        'timeout': 0.1,
        'retries': 1,
        'features_description': TEST_FEATURES_DESCRIPTION,
        'denominator': 1,
        'threshold': TEST_THRESHOLD,
        'features_builder_version': 2,
    },
}

TEST_CSRF_TOKEN = 'csrf'
