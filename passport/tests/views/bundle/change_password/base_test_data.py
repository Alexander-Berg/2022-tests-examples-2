# -*- coding: utf-8 -*-
import base64
import datetime as _datetime

from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.account.account import (
    KINOPOISK_UID_BOUNDARY,
    PDD_UID_BOUNDARY,
)
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_UID = 1
TEST_USER_IP = '3.3.3.3'
TEST_PDD_UID = PDD_UID_BOUNDARY + 1
TEST_DOMAIN = 'okna.ru'
TEST_KINOPOISK_UID = KINOPOISK_UID_BOUNDARY + 1

TEST_LOGIN = 'test_user'
TEST_PDD_LOGIN = 'test_user@okna.ru'
TEST_PDD_LOGIN_PART = TEST_LOGIN
TEST_LITE_LOGIN = 'test_user@okna.ru'
TEST_PHONISH_LOGIN = 'phne-123'
TEST_SOCIAL_LOGIN = 'uid-123'
TEST_KINOPOISK_ALIAS = '100500'
TEST_PASSWORD = 'aaa1bbbccc'
TEST_PASSWORD_QUALITY = 30
TEST_PASSWORD_QUALITY_VERSION = 3
TEST_OLD_SERIALIZED_PASSWORD = '1:$1$4GcNYVh5$4bdwYxUKcvcYHUXbnGFOA1'
TEST_WEAK_PASSWORD = 'qwerty'  # password quality = 15
TEST_NOT_STRONG_PASSWORD = 'asdfglkjha'  # password quality = 50
TEST_NEW_PASSWORD = 'secret-password'  # password quality = 100
TEST_NEW_PASSWORD_QUALITY = 100
TEST_PHONE_NUMBER = PhoneNumber.parse('+79261234567')
TEST_DIFFERENT_PHONE_NUMBER = PhoneNumber.parse('+79267654321')
TEST_GLOBAL_LOGOUT_DATETIME = DatetimeNow(
    convert_to_datetime=True,
    timestamp=_datetime.datetime.fromtimestamp(1),
)

TEST_HOST = 'passport-test.yandex.ru'
TEST_SESSIONID = 'sessionid'
TEST_SSL_SESSIONID = 'sslsessionid'
TEST_NONSECURE_COOKIE = 'Session_id=%s' % TEST_SESSIONID
TEST_COOKIE = 'Session_id=%s;sessionid2=%s' % (TEST_SESSIONID, TEST_SSL_SESSIONID)
TEST_COOKIE_TIMESTAMP = 1234
TEST_COOKIE_AGE = 123456
TEST_YANDEXUID_COOKIE = 'yandexuid'
TEST_FUID01_COOKIE = 'fuid'
TEST_RETPATH = 'http://test.yandex.ru'
TEST_RETPATH_HOST = 'test.yandex.ru'
TEST_PDD_RETPATH = u'%s/for/%s/' % (TEST_RETPATH, TEST_DOMAIN)
TEST_PUNYCODE_DOMAIN = 'xn--80atjc.xn--p1ai'
TEST_IDNA_DOMAIN = u'окна.рф'
TEST_CYRILLIC_PDD_LOGIN = u'test_user@окна.рф'
TEST_CLEANED_PDD_RETPATH = u'http://test.yandex.ru/'

TEST_USER_AGENT = 'curl'
TEST_USER_COUNTRY = 'ru'
TEST_USER_LANGUAGE = 'ru'
TEST_USER_TIMEZONE = 'Europe/Moscow'
TEST_ACCEPT_LANGUAGE = 'ru'

FRODO_RESPONSE_OK = '<spamlist></spamlist>'
FRODO_RESPONSE_FORBIDDEN_CHANGE_PASSWORD = '<spamlist><change_pass login="%s" weight="85" /></spamlist>' % TEST_LOGIN

# Эта история плохих сессий содержит одно синтетическое значение
# SessionKarma(timestamp=0, authid='test-authid')
TEST_BAD_SESSIONS = base64.b64encode('\x08\x01\x12\x13\x08\x01\x10\x00\x1a\x0btest-authid d')

TEST_CONSUMER = 'dev'

TEST_AUTH_ID = 'auth_id'
TEST_OLD_AUTH_ID = '123:1422501443:126'

TEST_ORIGIN = 'origin-1'
