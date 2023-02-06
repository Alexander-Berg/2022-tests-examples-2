# -*- coding: utf-8 -*-
import datetime as _datetime

from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.phone_number.phone_number import (
    mask_phone_number,
    PhoneNumber,
)


TEST_UID = 1
TEST_OTHER_UID = 123
TEST_LOGIN = 'user1'
TEST_PDD_DOMAIN = 'okna.ru'
TEST_PDD_LOGIN = 'user1@okna.ru'
TEST_OTHER_LOGIN = 'other_login'
TEST_IP = '127.0.0.1'
TEST_HOST = 'passport.yandex.ru'
TEST_ORIGIN = 'origin-2'
TEST_PDD_UID = 1130000000000001
TEST_GLOBAL_LOGOUT_DATETIME = DatetimeNow(
    convert_to_datetime=True,
    timestamp=_datetime.datetime.fromtimestamp(1),
)
TEST_PHONE_NUMBER = PhoneNumber.parse('+79161234567')
TEST_PHONE_NUMBER_DUMPED = {
    'e164': TEST_PHONE_NUMBER.e164,
    'original': TEST_PHONE_NUMBER.original,
    'international': TEST_PHONE_NUMBER.international,
    'masked_e164': mask_phone_number(TEST_PHONE_NUMBER.e164),
    'masked_original': mask_phone_number(TEST_PHONE_NUMBER.original),
    'masked_international': mask_phone_number(TEST_PHONE_NUMBER.international),
}
TEST_OTHER_PHONE_NUMBER = PhoneNumber.parse('+79161110000')
TEST_OTHER_PHONE_NUMBER_DUMPED = {
    'e164': TEST_OTHER_PHONE_NUMBER.e164,
    'original': TEST_OTHER_PHONE_NUMBER.original,
    'international': TEST_OTHER_PHONE_NUMBER.international,
    'masked_e164': mask_phone_number(TEST_OTHER_PHONE_NUMBER.e164),
    'masked_original': mask_phone_number(TEST_OTHER_PHONE_NUMBER.original),
    'masked_international': mask_phone_number(TEST_OTHER_PHONE_NUMBER.international),
}
TEST_CONFIRMATION_CODE = '123456'
TEST_APP_SECRET = 'AAAND6G4J2HJLNDGMVOYXBYXD4'
TEST_PIN = '0315'
TEST_PIN_LENGTH = len(TEST_PIN)
TEST_TOTP_SECRET = b'\x00\x00\xd1\xf8\xdcN\x8e\x95\xb4fe]\x8b\x87\x17\x1f'
TEST_APP_SECRET_CONTAINER = '2H4NYTUOSW2GMZK5RODROHYAAAAAAAAAAAATVIQ'
TEST_PUSH_SETUP_SECRET = '708ab6a91d336ba09b5aa1cec5bde098'
TEST_DEVICE_ID = 'e77adc1af438ef3f0cae97d9c24569497f'
TEST_OTP = 'abcd'
TEST_PASSWORD = '123'
TEST_RETPATH = 'http://yandex.ru'
TEST_RETPATH_HOST = 'yandex.ru'
TEST_TOTP_CHECK_TIME = 12589
TOTP_SECRET_ENCRYPTED = 'encrypted_secret'
TOTP_JUNK_SECRET_ENCRYPTED = 'junk_secret'


def get_headers(cookie=None):
    if cookie is None:
        cookie = 'Session_id=0:old-session;yandexuid=testyandexuid;sessionid2=0:old-sslsession'
    return mock_headers(
        host=TEST_HOST,
        cookie=cookie,
        user_ip=TEST_IP,
        user_agent='curl',
    )


def get_expected_account_response():
    return {
        'uid': int(TEST_UID),
        'login': TEST_LOGIN,
        'display_login': TEST_LOGIN,
        'person': {
            'firstname': u'\\u0414',
            'language': u'ru',
            'gender': 1,
            'birthday': u'1963-05-15',
            'lastname': u'\\u0424',
            'country': u'ru',
        },
        'display_name': {u'default_avatar': u'', u'name': u''},
    }
