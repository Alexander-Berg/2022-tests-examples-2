# -*- coding: utf-8 -*-
from passport.backend.core.builders.blackbox.constants import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
)

from .base import BaseMobileProxyTestCase
from .test_base_data import (
    TEST_AVATAR_URL_TEMPLATE,
    TEST_DISPLAY_NAME,
    TEST_OAUTH_TOKEN,
    TEST_UID,
)


TEST_LOGIN = 'test.login'
TEST_NORMALIZED_LOGIN = 'test-login'
TEST_AVATAR_KEY = 'avakey'
TEST_AVATAR_STUB_KEY = '0/0-0'

TEST_UNIXTIME = 946674001
TEST_DATETIME_STR = datetime_to_string(unixtime_to_datetime(TEST_UNIXTIME))

TEST_BLACKBOX_URL = 'http://bb.yandex.ru'


@with_settings_hosts(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    BLACKBOX_URL=TEST_BLACKBOX_URL,
)
class BlackboxViewsTestCase(BaseMobileProxyTestCase):
    def setUp(self):
        super(BlackboxViewsTestCase, self).setUp()
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_NORMALIZED_LOGIN,
                display_login=TEST_LOGIN,
                display_name={'name': TEST_DISPLAY_NAME},
                scope='oauth:grant_xtoken',
                default_avatar_key=TEST_AVATAR_KEY,
                oauth_token_info={'issue_time': TEST_DATETIME_STR},
            ),
        )

    def test_get_login_ok(self):
        rv = self.make_request(
            'mobileproxy/1/login/',
            data={
                'token': TEST_OAUTH_TOKEN,
            },
        )
        self.check_json_ok(rv, login=TEST_LOGIN)

    def test_get_login_without_trailing_slash_ok(self):
        rv = self.make_request(
            'mobileproxy/1/login',
            data={
                'token': TEST_OAUTH_TOKEN,
            },
        )
        self.check_json_ok(rv, login=TEST_LOGIN)

    def test_get_login_token_missing(self):
        rv = self.make_request(
            'mobileproxy/1/login/',
        )
        self.check_xml_error(rv, 'missing parameter \'token\'')

    def test_get_login_token_empty(self):
        rv = self.make_request(
            'mobileproxy/1/login/',
            data={
                'token': '',
            },
        )
        self.check_xml_error(rv, 'parameter \'token\' is empty')

    def test_get_login_token_invalid(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                status=BLACKBOX_OAUTH_INVALID_STATUS,
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/login/',
            data={
                'token': TEST_OAUTH_TOKEN,
            },
        )
        self.check_xml_error(rv, 'Oauth token invalid', status_code=401)

    def test_user_info_ok(self):
        rv = self.make_request(
            'mobileproxy/1/user_info/',
            data={
                'token': TEST_OAUTH_TOKEN,
            },
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            default_avatar=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
            is_avatar_empty=False,
            staff=False,
            betatester=False,
            has_plus=False,
            x_token_issued_at=TEST_UNIXTIME,
        )
        self.env.blackbox.requests[0].assert_url_starts_with(TEST_BLACKBOX_URL)

    def test_user_info_without_trailing_slash_ok(self):
        rv = self.make_request(
            'mobileproxy/1/user_info',
            data={
                'token': TEST_OAUTH_TOKEN,
            },
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            default_avatar=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
            is_avatar_empty=False,
            staff=False,
            betatester=False,
            has_plus=False,
            x_token_issued_at=TEST_UNIXTIME,
        )
        self.env.blackbox.requests[0].assert_url_starts_with(TEST_BLACKBOX_URL)

    def test_user_info_custom_ok(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_NORMALIZED_LOGIN,
                display_login=TEST_LOGIN,
                display_name={'name': TEST_DISPLAY_NAME},
                scope='oauth:grant_xtoken',
                default_avatar_key=TEST_AVATAR_KEY,
                aliases={
                    'yandexoid': 'volozh',
                },
                attributes={
                    'account.is_betatester': '1',
                    'account.have_plus': '1',
                },
                oauth_token_info={'ctime': TEST_DATETIME_STR},
            ),
        )

        rv = self.make_request(
            'mobileproxy/1/user_info/',
            data={
                'token': TEST_OAUTH_TOKEN,
                'size': 'xxl',
            },
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            default_avatar=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'xxl'),
            is_avatar_empty=False,
            staff=True,
            betatester=True,
            has_plus=True,
            x_token_issued_at=TEST_UNIXTIME,
        )

    def test_user_info_no_avatar_ok(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_NORMALIZED_LOGIN,
                display_login=TEST_LOGIN,
                display_name={'name': TEST_DISPLAY_NAME},
                scope='oauth:grant_xtoken',
                default_avatar_key=TEST_AVATAR_STUB_KEY,
                is_avatar_empty=True,
                oauth_token_info={},  # без ctime и issue_time
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/user_info/',
            data={
                'token': TEST_OAUTH_TOKEN,
            },
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            default_avatar=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_STUB_KEY, 'normal'),
            is_avatar_empty=True,
            staff=False,
            betatester=False,
            has_plus=False,
            x_token_issued_at=0,
        )
        self.env.blackbox.requests[0].assert_url_starts_with(TEST_BLACKBOX_URL)

    def test_user_info_token_missing(self):
        rv = self.make_request(
            'mobileproxy/1/user_info/',
        )
        self.check_xml_error(rv, 'missing parameter \'token\'')

    def test_user_info_token_empty(self):
        rv = self.make_request(
            'mobileproxy/1/user_info/',
            data={
                'token': '',
            },
        )
        self.check_xml_error(rv, 'parameter \'token\' is empty')

    def test_user_info_token_invalid(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                status=BLACKBOX_OAUTH_INVALID_STATUS,
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/user_info/',
            data={
                'token': TEST_OAUTH_TOKEN,
            },
        )
        self.check_xml_error(rv, 'Oauth token invalid', status_code=401)

    def test_user_info_not_xtoken(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope='oauth:test',
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/user_info/',
            data={
                'token': TEST_OAUTH_TOKEN,
            },
        )
        self.check_xml_error(rv, 'Invalid token: X-Token scope missing')
