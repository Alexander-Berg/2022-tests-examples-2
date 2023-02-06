# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from passport.backend.api.tests.views.bundle.test_base_data import TEST_UID
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.time import datetime_to_integer_unixtime


TEST_UID2 = 2

TEST_CONFIRMATION_CODE = '123456'
TEST_OTHER_CONFIRMATION_CODE = '630712'

TEST_COOKIE_TIMESTAMP = 1383144488
TEST_COOKIE_L = ('VFUrAHh8fkhQfHhXW117aH4GB2F6UlZxWmUHQmEBdxwEHhZBDyYxVUYCIxEcJEYfFTpdBF9dGRMuJHU4HwdSNQ=='
                 '.%s.1002323.298169.6af3100a8920a270bd9a933bbcd48181') % TEST_COOKIE_TIMESTAMP

TEST_YANDEXUID_COOKIE = 'yandexuid'
TEST_YANDEX_GID_COOKIE = 'yandex_gid'
TEST_FUID01_COOKIE = 'fuid'
TEST_COOKIE_MY = 'YycCAAYA'
COOKIE_MY_VALUE_WITH_AUTH_SESSION_POLICY_PERMANENT = 'YycCAAY2AQEA'
TEST_SESSIONID = '0:old-session'
TEST_SSL_SESSIONID = '0:old-sslsession'

TEST_SESSIONID_COOKIE = 'Session_id=%s;' % TEST_SESSIONID

TEST_USER_COOKIES = 'Session_id=%s; yandexuid=%s; yandex_gid=%s; fuid01=%s; my=%s; L=%s; sessionid2=%s;' % (
    TEST_SESSIONID, TEST_YANDEXUID_COOKIE, TEST_YANDEX_GID_COOKIE, TEST_FUID01_COOKIE, TEST_COOKIE_MY, TEST_COOKIE_L, TEST_SSL_SESSIONID,
)

TEST_PHONE_CREATED_DT = datetime(2000, 1, 2, 12, 34, 56)
TEST_PHONE_CREATED_TS = datetime_to_integer_unixtime(TEST_PHONE_CREATED_DT)
TEST_PHONE_BOUND_DT = datetime(2001, 2, 3, 1, 2, 0)
TEST_PHONE_BOUND_TS = datetime_to_integer_unixtime(TEST_PHONE_BOUND_DT)
TEST_PHONE_CONFIRMED_DT = datetime(2005, 2, 3, 1, 2, 1)
TEST_PHONE_CONFIRMED_TS = datetime_to_integer_unixtime(TEST_PHONE_CONFIRMED_DT)
TEST_PHONE_ADMITTED_DT = datetime(2003, 2, 3, 1, 2, 2)
TEST_PHONE_ADMITTED_TS = datetime_to_integer_unixtime(TEST_PHONE_ADMITTED_DT)
TEST_PHONE_SECURED_DT = datetime(2004, 2, 3, 1, 2, 3)
TEST_PHONE_SECURED_TS = datetime_to_integer_unixtime(TEST_PHONE_SECURED_DT)

TEST_OPERATION_STARTED_DT = datetime(2001, 5, 6, 7, 8, 9)
TEST_OPERATION_STARTED_TS = datetime_to_integer_unixtime(TEST_OPERATION_STARTED_DT)
TEST_OP_FINISHED_DT = datetime(2005, 2, 3, 1, 2, 3)
TEST_OP_FINISHED_TS = datetime_to_integer_unixtime(TEST_OP_FINISHED_DT)
TEST_OP_PASSWORD_VERIFIED_DT = datetime(2002, 3, 3, 1, 2, 3)
TEST_OP_PASSWORD_VERIFIED_TS = datetime_to_integer_unixtime(TEST_OP_PASSWORD_VERIFIED_DT)
TEST_OP_CODE_CONFIRMED_DT = datetime(2000, 1, 2, 13, 34, 56)
TEST_OP_CODE_CONFIRMED_TS = datetime_to_integer_unixtime(TEST_OP_CODE_CONFIRMED_DT)

TEST_OP_CODE_LAST_SENT_DT = datetime(1999, 1, 2, 12, 34, 56)
TEST_OP_CODE_LAST_SENT_TS = datetime_to_integer_unixtime(TEST_OP_CODE_LAST_SENT_DT)

TEST_OPERATION_TTL = timedelta(hours=1)
TEST_OPERATION_ID_EXTRA = 124

TEST_PASSWORD = 'abcde12345'

TEST_LOGIN = 'testuser'
TEST_EMAIL = TEST_LOGIN + '@yandex-team.ru'
TEST_PHONE_ID = 1
TEST_PHONE_ID_EXTRA = 2
TEST_FIRSTNAME = u'Василий'

TEST_SOCIAL_LOGIN = 'uid-%d' % TEST_UID

TEST_LOGIN2 = 'testuser2'
TEST_EMAIL2 = TEST_LOGIN2 + '@yandex-team.ru'
TEST_FIRSTNAME2 = u'Мария'

TEST_REPLACEMENT_PHONE_NUMBER = PhoneNumber.parse(u'+79010000001')
TEST_REPLACEMENT_PHONE_ID = 13
LOCAL_TEST_REPLACEMENT_PHONE_NUMBER = PhoneNumber.parse(u'89010000001', country=u'RU')

TEST_SECURE_PHONE_NUMBER = PhoneNumber.parse(u'+79020000002')
TEST_SECURE_PHONE_ID = 17
TEST_MARK_OPERATION_TTL = 2

TEST_NON_EXISTENT_TRACK_ID = u'0' * 34
