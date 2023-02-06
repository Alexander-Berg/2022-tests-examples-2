# -*- coding: utf-8 -*-
import datetime as _datetime

from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_UID = 1
TEST_OTHER_UID = 123
TEST_LOGIN = 'user1'
TEST_PDD_LOGIN = 'user1@okna.ru'
TEST_OTHER_LOGIN = 'other_login'
TEST_IP = '127.0.0.1'
TEST_HOST = 'passport.yandex.ru'
TEST_PDD_UID = 1130000000000001
TEST_PHONE_NUMBER = PhoneNumber.parse('+79161234567')
TEST_PHONE_NUMBER_DUMPED = {
    'e164': TEST_PHONE_NUMBER.e164,
    'original': TEST_PHONE_NUMBER.original,
    'international': TEST_PHONE_NUMBER.international,
}
TEST_OTHER_PHONE_NUMBER = PhoneNumber.parse('+79161110000')
TEST_OTP = 'abcd'
TEST_PASSWORD = 'simpe123456-secure'
TEST_RETPATH = 'http://yandex.ru'
TEST_RETPATH_HOST = 'yandex.ru'
TEST_GLOBAL_LOGOUT_DATETIME = DatetimeNow(
    convert_to_datetime=True,
    timestamp=_datetime.datetime.fromtimestamp(1),
)
TEST_ORIGIN = 'origin-3'


def get_headers(cookie=None):
    if cookie is None:
        cookie = 'Session_id=0:old-session;yandexuid=testyandexuid;sessionid2=0:old-sslsession'
    return mock_headers(
        host=TEST_HOST,
        cookie=cookie,
        user_ip=TEST_IP,
        user_agent='curl',
    )
