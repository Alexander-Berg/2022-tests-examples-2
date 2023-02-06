# -*- coding: utf-8 -*-

from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.core.models.password import PASSWORD_ENCODING_VERSION_MD5_CRYPT  # noqa
from passport.backend.core.models.password import PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON  # noqa
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD  # noqa
from passport.backend.core.types.account.account import KINOPOISK_UID_BOUNDARY
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_UID = 1
TEST_UID_2 = 2
TEST_SUID = 1
TEST_HOST = 'yandex.ru'
TEST_USER_IP = '37.9.101.188'
TEST_USER_AGENT = 'curl'
TEST_RETPATH = 'http://ya.ru'
TEST_USER_COOKIES = ''
TEST_REFERER = 'http://passportdev-python.yandex.ru/passport?mode=passport'
TEST_USER_COUNTRY = 'ru'
TEST_PASSWORD_QUALITY = '80'

TEST_OTHER_LOGIN = 'other_login'
TEST_KARMA = 100
TEST_DEFAULT_TIMEZONE = 'Europe/Moscow'
TEST_USER_LOGIN = 'test.login'
TEST_USER_LOGIN_NORMALIZED = 'test-login'
TEST_USER_PASSWORD = 'aaa1bbbccc'
TEST_USER_PASSWORD_QUALITY = 80
TEST_USER_FIRSTNAME = 'firstname'
TEST_USER_LASTNAME = 'lastname'
TEST_HINT_CUSTOM_QUESTION_ID = 99
TEST_HINT_QUESTION = 'test-question-text'
TEST_HINT_ANSWER = 'test-answer-text'
TEST_HINT_PREDEFINED_QUESTION_ID = 1
TEST_HINT_PREDEFINED_QUESTION = u'Девичья фамилия матери'
TEST_ACCEPT_LANGUAGE = 'ru'
TEST_PHONE_NUMBER = PhoneNumber.parse('+79161234567')
TEST_PHONE_NUMBER_MASKED = '79160004567'
TEST_INVALID_PHONE = '79161'
TEST_INVALID_EMAIL = '!1abc'
TEST_PHONE_NUMBER_HASH = '7cf8d09b75e39a0c215b2c7cdcacadde'
TEST_DECODED_CYRILLIC_EMAIL = u'vasia@почта.рф'
TEST_EMAIL = 'email@yandex.ru'
TEST_NON_NATIVE_EMAIL = 'email@gmail.com'
TEST_ANOTHER_NON_NATIVE_EMAIL = 'another-email@gmail.com'
TEST_PERSISTENT_TRACK_ID = '52bf429537106213b295c3efa00ce236'

TEST_SHORT_CODE = '12345'

TEST_KP_ID = 1234
TEST_KP_UID = KINOPOISK_UID_BOUNDARY + TEST_KP_ID
TEST_PASSWORD_HASH_NORMALIZED = 'c4ca4238a0b923820dcc509a6f75849b'
TEST_PASSWORD_HASH = TEST_PASSWORD_HASH_NORMALIZED.upper()

TEST_CLIENT_ID = 'foo'
TEST_CLIENT_SECRET = 'bar'
TEST_DEVICE_ID = 'c3po'
TEST_DEVICE_NAME = 'IFridge'
TEST_TOKEN = 'a68d97976a66444496148b694802b009'
TEST_TOKEN_TYPE = 'bearer'


def build_headers(host=None, user_ip=None, cookie=None):
    return mock_headers(
        host=host or TEST_HOST,
        user_ip=user_ip or TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        referer=TEST_REFERER,
        accept_language=TEST_ACCEPT_LANGUAGE,
        cookie=cookie,
    )
