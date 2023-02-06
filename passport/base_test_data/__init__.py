# -*- coding: utf-8 -*-
import base64
import datetime as _datetime

from passport.backend.api.tests.views.bundle.test_base_data import *
from passport.backend.api.views.bundle.mixins.challenge import YANDEX_PROFILE_TEST_LOGIN_PREFIX
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_UID = 1
TEST_PDD_UID = 1130000000000001

TEST_LOGIN = 'test-user'
TEST_ANOTHER_LOGIN = 'james-bond'
TEST_ENTERED_LOGIN = 'TeSt.UsEr'
TEST_PDD_DOMAIN = 'testdomain.com'
TEST_PDD_LOGIN_PART = TEST_PDD_LOGIN = 'test-user@{}'.format(TEST_PDD_DOMAIN)
TEST_ENTERED_PDD_LOGIN = TEST_ENTERED_LOGIN
TEST_PDD_DOMAIN_INFO = {
    'punycode': TEST_PDD_DOMAIN,
    'unicode': TEST_PDD_DOMAIN,
}
TEST_LITE_LOGIN = 'test-user@okna.ru'
TEST_ENTERED_LITE_LOGIN = 'teST.useR@Okna.ru'
TEST_GALATASARAY_ALIAS = 'test-user@galatasaray.net'
TEST_SOCIAL_ALIAS = 'uid-100500'
TEST_PROFILE_USER_LOGIN = YANDEX_PROFILE_TEST_LOGIN_PREFIX + 'login'
TEST_LOGIN_ID = 'login-id'

TEST_DOMAIN = 'testdomain.com'
TEST_CYRILLIC_PDD_LOGIN = u'test_user@окна.рф'
TEST_PUNYCODE_DOMAIN = 'xn--80atjc.xn--p1ai'
TEST_IDNA_DOMAIN = u'окна.рф'
TEST_GLOBAL_LOGOUT_DATETIME = DatetimeNow(
    convert_to_datetime=True,
    timestamp=_datetime.datetime.fromtimestamp(1),
)

TEST_IP = '3.3.3.3'
TEST_ANOTHER_IP = '5.45.207.254'

TEST_PHONE_NUMBER_ID = 999
TEST_PHONE_NUMBER = PhoneNumber.parse('+79261234567')
TEST_PHONE_ID = 1
TEST_DIFFERENT_PHONE_NUMBER = PhoneNumber.parse('+79267654321')

SESSIONID_COOKIE = 'Session_id=2:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/'

TEST_YANDEXUID_COOKIE = '1046714081386936400'
TEST_YANDEXUID_TIMESTAMP = 1386936400
TEST_YANDEX_GID_COOKIE = 'yandex_gid'
TEST_FUID01_COOKIE = 'fuid'
TEST_COOKIE_MY = 'YycCAAYA'

TEST_COOKIE_AGE = 123456
TEST_COOKIE_TIMESTAMP = 1383144488
TEST_COOKIE_L = 'AlV8CX59e0ZbfXxQWVNzaHoEA2l5UlJ6QzdDTHsbNgtB.%s.1002322.357940.a8224a60eb1025896a31182f25d2a58a' % TEST_COOKIE_TIMESTAMP
TEST_USER_COOKIES = 'yandexuid=%s; yandex_gid=%s; fuid01=%s; my=%s; L=%s;' % (
    TEST_YANDEXUID_COOKIE, TEST_YANDEX_GID_COOKIE, TEST_FUID01_COOKIE, TEST_COOKIE_MY, TEST_COOKIE_L,
)

COOKIE_LAH_VALUE = 'OG5EOF8wU_bOAGhjXFp7YXkHAGB9UVFyB2IACGZedV4DWl8FWXF5BgJXYFVzYQVKV3kFVlpaU0p2f31iRkZRYQ.1473090908.1002323.1.2fe2104fff29aa69e867d7d1ea601470'
COOKIE_LAH_TEMPLATE = u'lah=%s; Domain=.passport-test.yandex.ru; Expires=%s; Secure; HttpOnly; Path=/'
EXPECTED_LAH_COOKIE = COOKIE_LAH_TEMPLATE % (COOKIE_LAH_VALUE, 'Tue, 19 Jan 2038 03:14:07 GMT')
EMPTY_COOKIE_LAH = COOKIE_LAH_TEMPLATE % ('', 'Thu, 01 Jan 1970 00:00:01 GMT')

COOKIE_ILAHU_VALUE = '1500000000'
COOKIE_ILAHU_TEMPLATE = u'ilahu=%s; Domain=.passport-test.yandex.ru; Expires=Mon, 13 Jun 2033 03:14:07 GMT; Secure; HttpOnly; Path=/'
EXPECTED_ILAHU_COOKIE = COOKIE_ILAHU_TEMPLATE % TEST_ILAHU_VALUE

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE

TEST_SERVICE = 'lenta'
TEST_SERVICE_SID = 23

FRODO_RESPONSE_OK = '<spamlist></spamlist>'
FRODO_RESPONSE_PROBABLY_SPAM_USER = '<spamlist><change_pass login="%s" weight="85" /></spamlist>' % TEST_LOGIN
FRODO_RESPONSE_SPAM_USER = '<spamlist><spam_user login="%s" weight="85" /></spamlist>' % TEST_LOGIN
FRODO_RESPONSE_BAD_USER = '<spamlist><spam_user login="%s" weight="100" /></spamlist>' % TEST_LOGIN

FRODO_RESPONSE_SPAM_PDD_USER = '<spamlist><spam_user login="%s" weight="85" /></spamlist>' % TEST_PDD_LOGIN_PART
FRODO_RESPONSE_BAD_PDD_USER = '<spamlist><spam_user login="%s" weight="100" /></spamlist>' % TEST_PDD_LOGIN_PART

# Эта история плохих сессий содержит одно синтетическое значение
# SessionKarma(timestamp=0, authid='test-authid')
TEST_BAD_SESSIONS = base64.b64encode(b'\x08\x01\x12\x13\x08\x01\x10\x00\x1a\x0btest-authid d')

TEST_AUTH_ID = '123:1422501443:126'
TEST_OLD_AUTH_ID = '123:0000000:555'

TEST_TRACK_ID = 'd2f90ceb577b9615b7de94b8f76516827f'

TEST_USER_AGENT = 'curl'

TEST_DEVICE_ID = '6532c47b-f04e-48c4-aaff-a49ffb9bcf9c'
TEST_OTHER_DEVICE_ID = '00169015-d53e-495e-bff7-65022f2aa341'
