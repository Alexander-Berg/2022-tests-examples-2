# -*- coding: utf-8 -*-

from passport.backend.core.models.persistent_track import PERSISTENT_TRACK_ID_BYTES_COUNT
from passport.backend.utils.common import bytes_to_hex


TEST_EMAIL_ID = 1
TEST_LOGIN = 'test_login'
TEST_UID = 1
TEST_ANOTHER_UID = TEST_UID + 1
TEST_ADDRESS = u'test@another-yandex.ru'
TEST_ANOTHER_ADDRESS = 'test.' + TEST_ADDRESS
TEST_NATIVE_ADDRESS = u'test@yandex.ru'
TEST_IP = '3.3.3.3'
TEST_USER_AGENT = 'curl'
TEST_ACCEPT_LANGUAGE = 'ru'
TEST_HOST = 'passport-test.yandex.ru'
TEST_PERSISTENT_TRACK_ID = bytes_to_hex(b'a' * PERSISTENT_TRACK_ID_BYTES_COUNT)
TEST_BORN_DATE = '2014-12-26 16:11:15'
TEST_CODE = TEST_PERSISTENT_TRACK_ID
TEST_SESSIONID = 'sessionid'
TEST_TTL = 1
TEST_CONSUMER_IP = '127.0.0.1'
