# -*- coding: utf-8 -*-
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
)
from passport.backend.core.builders.blackbox.exceptions import (
    BlackboxInvalidParamsError,
    BlackboxTemporaryError,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_AVATAR_ID,
    TEST_DISPLAY_NAME,
    TEST_LOGIN,
    TEST_LOGIN_ID,
    TEST_NORMALIZED_LOGIN,
    TEST_OTHER_UID,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase
from passport.backend.utils.time import datetime_to_integer_unixtime


TEST_CYRILLIC_REDIRECT_URI = 'https://окна.рф'
TEST_IDNA_ENCODED_REDIRECT_URI = 'https://xn--80atjc.xn--p1ai'
TEST_PAYMENT_AUTH_RETPATH = 'https://oauth.yandex.com/money'
TEST_PAYMENT_AUTH_SCHEME = 'test_scheme'
TEST_AVATARS_BASE_URL = 'https://avatars.ru'
TEST_OLD_ICON_ID = 'gid/client_id-abc'
TEST_OLD_ICON_URL = TEST_AVATARS_BASE_URL + '/get-oauth/%s/normal' % TEST_OLD_ICON_ID

TEST_NEW_CLIENT_ICON_ID_PREFIX = '1234/%s-'  # сюда подставится client_id

TEST_HOST = 'oauth-internal.yandex.ru'
TEST_COOKIE = 'yandexuid=yu;Session_id=foo'
TEST_AUTHORIZATION = 'OAuth token'

TEST_IOS_APP_ID = '1234567890.ru.app'
TEST_IOS_APP_ID_OTHER = '1234567890.com.app'
TEST_IOS_APPSTORE_URL = 'https://ios.com'
TEST_ANDROID_PACKAGE_NAME = 'package_name.foo'
TEST_ANDROID_PACKAGE_NAME_OTHER = 'package_name.bar'
TEST_ANDROID_FINGERPRINT = 'a' * 95
TEST_ANDROID_APPSTORE_URL = 'https://android.com'
TEST_TURBOAPP_BASE_URL = 'https://ozon.ru'

TEST_DEVICE_ID = 'iFridge'
TEST_DEVICE_NAME = 'My refrigerator'

TEST_CODE_CHALLENGE = 'a' * 43


class BaseIfaceApiTestCase(BundleApiTestCase):
    def default_headers(self, user_ip=TEST_USER_IP, cookie=TEST_COOKIE, authorization=None):
        return {
            'HTTP_HOST': TEST_HOST,
            'HTTP_YA_CONSUMER_CLIENT_IP': user_ip,
            'HTTP_X_REAL_IP': user_ip,
            'HTTP_YA_CLIENT_USER_AGENT': 'curl',
            'HTTP_YA_CLIENT_COOKIE': cookie,
            'HTTP_YA_CONSUMER_AUTHORIZATION': authorization,
        }

    def setup_blackbox_response(
        self,
        attributes=None,
        age=0,
        have_password=True,
        karma=None,
        is_child=False
    ):
        attributes = attributes or {}
        attributes['account.normalized_login'] = TEST_NORMALIZED_LOGIN

        if have_password:
            attributes['account.have_password'] = '1'

        if is_child:
            attributes['account.is_child'] = '1'

        default_blackbox_kwargs = {
            'uid': TEST_UID,
            'login': TEST_LOGIN,
            'display_name': TEST_DISPLAY_NAME,
            'default_avatar_key': TEST_AVATAR_ID,
            'aliases': {
                'portal': TEST_NORMALIZED_LOGIN,
            },
            'age': age,
            'have_password': have_password,
            'karma': karma or 0,
        }
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    attributes=attributes,
                    login_id=TEST_LOGIN_ID,
                    **dict(default_blackbox_kwargs)
                ),
                **dict(default_blackbox_kwargs, uid=TEST_OTHER_UID)
            ),
        )


class CommonCookieTests(object):
    def test_no_session_cookie(self):
        rv = self.make_request(headers=self.default_headers(cookie='yandexuid=yu'))
        self.assert_status_error(rv, ['sessionid.empty'])

    def test_blackbox_sessionid_invalid_params(self):
        self.fake_blackbox.set_response_side_effect(
            'sessionid',
            BlackboxInvalidParamsError,
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['blackbox.invalid_params'])

    def test_blackbox_sessionid_failed(self):
        self.fake_blackbox.set_response_side_effect(
            'sessionid',
            BlackboxTemporaryError,
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['backend.failed'])

    def test_sessguard_invalid(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_WRONG_GUARD_STATUS),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['sessguard.invalid'])

    def test_session_cookie_invalid(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['sessionid.invalid'])

    def test_user_not_in_cookie(self):
        rv = self.make_request(uid=43)
        self.assert_status_error(rv, ['sessionid.no_uid'])

    def test_user_session_invalid(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(default_user_status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['sessionid.invalid'])


class CommonTokenTests(object):
    def test_malformed_authorization_header(self):
        rv = self.make_request(headers=self.default_headers(authorization='foo'))
        self.assert_status_error(rv, ['authorization.invalid'])

    def test_oauth_token_empty(self):
        rv = self.make_request(headers=self.default_headers(authorization='Oauth '))
        self.assert_status_error(rv, ['authorization.invalid'])

    def test_blackbox_oauth_invalid_params(self):
        self.fake_blackbox.set_response_side_effect(
            'oauth',
            BlackboxInvalidParamsError,
        )
        rv = self.make_request(headers=self.default_headers(authorization=TEST_AUTHORIZATION))
        self.assert_status_error(rv, ['backend.failed'])

    def test_blackbox_oauth_failed(self):
        self.fake_blackbox.set_response_side_effect(
            'oauth',
            BlackboxTemporaryError,
        )
        rv = self.make_request(headers=self.default_headers(authorization=TEST_AUTHORIZATION))
        self.assert_status_error(rv, ['backend.failed'])

    def test_oauth_token_invalid(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS),
        )
        rv = self.make_request(headers=self.default_headers(authorization=TEST_AUTHORIZATION))
        self.assert_status_error(rv, ['oauth_token.invalid'])

    def test_not_xtoken(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(scope='test:foo'),
        )
        rv = self.make_request(headers=self.default_headers(authorization=TEST_AUTHORIZATION))
        self.assert_status_error(rv, ['oauth_token.invalid'])


class BaseClientTestCase(BaseIfaceApiTestCase):
    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'client_id': self.test_client.display_id,
            'language': 'ru',
        }

    def base_client_info(self):
        return {
            'id': self.test_client.display_id,
            'title': 'Тестовое приложение',
            'description': 'Test client',
            'icon': 'http://icon',
            'icon_id': TEST_OLD_ICON_ID,
            'icon_url': TEST_OLD_ICON_URL,
            'homepage': 'http://homepage',
            'callback': 'https://callback',
            'redirect_uris': ['https://callback'],
            'scopes': {
                'Тестирование OAuth': {
                    'test:foo': {
                        'title': 'фу',
                        'requires_approval': False,
                        'ttl': None,
                        'is_ttl_refreshable': False,
                    },
                    'test:bar': {
                        'title': 'бар',
                        'requires_approval': False,
                        'ttl': None,
                        'is_ttl_refreshable': False,
                    },
                },
            },
            'platforms': {
                'web': {
                    'redirect_uris': ['https://callback'],
                },
            },
            'create_time': datetime_to_integer_unixtime(self.test_client.created),
            'is_yandex': False,
            'is_deleted': False,
        }


class BaseScopesTestCase(BaseIfaceApiTestCase):
    def visible_scopes(self, hide_tags=True):
        scope_groups = {
            'Тестирование OAuth': {
                'test:foo': {
                    'title': 'фу',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': ['test_tag'],
                },
                'test:bar': {
                    'title': 'бар',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
                'test:ttl': {
                    'title': 'протухать',
                    'requires_approval': False,
                    'ttl': 60,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
                'test:ttl_refreshable': {
                    'title': 'подновляться',
                    'requires_approval': False,
                    'ttl': 300,
                    'is_ttl_refreshable': True,
                    'tags': [],
                },
                'test:premoderate': {
                    'title': 'премодерироваться',
                    'requires_approval': True,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
                'test:hidden': {
                    'title': 'прятаться',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
                'test:xtoken': {
                    'title': 'выдавать',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
            },
            'Стрельбы по OAuth': {
                'lunapark:use': {
                    'title': 'стрелять',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
            },
            'Пароли приложений': {
                'app_password:calendar': {
                    'title': 'пользоваться календарём',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
            },
            'Деньги': {
                'money:all': {
                    'title': 'тратить деньги',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
            },
        }

        if hide_tags:
            for scope_group in scope_groups.values():
                for scope in scope_group.values():
                    del scope['tags']

        return scope_groups
