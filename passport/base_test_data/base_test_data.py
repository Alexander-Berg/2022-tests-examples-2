# -*- coding: utf-8 -*-
from datetime import datetime

from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_LOGIN,
    TEST_UID,
)
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import bytes_to_hex


TEST_MASKED_LOGIN = '%s***%s' % (TEST_LOGIN[0], TEST_LOGIN[-1])
TEST_USER_IP = '3.3.3.3'
TEST_YANDEX_IP = '37.9.101.188'

TEST_TRACK_ID = 'd2f90ceb577b9615b7de94b8f76516827f'
TEST_DEVICE_APP = 'ru.yandex.foo'
TEST_DEVICE_ID = 'A3B35F7E-09CE-4A8D-A53B-4C8A87CE73C9'
TEST_DEVICE_NAME = 'My iPhone %<b>'
TEST_ESCAPED_DEVICE_NAME = 'My iPhone &amp;#37;&lt;b&gt;'
TEST_LOCATION = u'Фэрфилд'
TEST_CLOUD_TOKEN = 'cl-xxx'

TEST_AVATAR_SIZE = 'islands_xxl'
TEST_CAPTCHA_SCALE_FACTOR = 2

TEST_X_TOKEN_CLIENT_ID = 'x-token-client-id'
TEST_X_TOKEN_CLIENT_SECRET = 'x-token-client-secret'
TEST_CLIENT_ID = 'client-id'
TEST_CLIENT_SECRET = 'client-secret'

TEST_OAUTH_X_TOKEN = 'x-token'
TEST_OAUTH_X_TOKEN_TTL = 3600 * 24
TEST_OAUTH_TOKEN_TTL = 3600

TEST_OTP = '123456'
TEST_OTP_CHECK_TIME = 100500

TEST_PHONE = '+79993456789'
TEST_PHONE_OBJECT = PhoneNumber.parse(TEST_PHONE)
TEST_PHONE_LOCAL_FORMAT = '8-(999)-345-6789'

TEST_PHONE_BOUND = datetime.fromtimestamp(12345)
TEST_PHONE_SECURED = datetime.fromtimestamp(123456)
TEST_PHONE_CONFIRMED = datetime.fromtimestamp(1234567)

TEST_PUBLIC_ID = 'elon-musk'

TEST_AUTH_MAGIC_LINK_TEMPLATE = 'http://passport.{tld}/magic-link-confirm-auth/?{query_string}'
TEST_REGISTER_MAGIC_LINK_TEMPLATE = 'http://passport.{tld}/magic-link-confirm-register/?{query_string}'
TEST_MAGIC_LINK_RANDOM_BYTES = b'1' * 10
TEST_MAGIC_LINK_SECRET = bytes_to_hex(TEST_MAGIC_LINK_RANDOM_BYTES)
TEST_MAGIC_LINK_SECRET_WITH_UID = '%s%x' % (TEST_MAGIC_LINK_SECRET, TEST_UID)

TEST_NATIVE_EMAIL = '%s@yandex.ru' % TEST_LOGIN
TEST_EXTERNAL_EMAIL = '%s@gmail.com' % TEST_LOGIN


TEST_MAIL_SUBSCRIPTION_SERVICES = [
    {
        'id': 1,
        'origin_prefixes': [],
        'app_ids': [TEST_DEVICE_APP],
        'slug': None,
        'external_list_ids': [],
    },
    {
        'id': 2,
        'origin_prefixes': [],
        'app_ids': ['ru.yandex.smth_other'],
        'slug': None,
        'external_list_ids': [],
    },
]


class TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE(object):
    platform = 'iPhone'
    version = '8.0.0'
