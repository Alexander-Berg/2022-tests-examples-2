# -*- coding: utf-8 -*-
import json
import unittest

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.account.lastauth.controllers import (
    LASTAUTH_BASIC_GRANT,
    LASTAUTH_BY_UID_GRANT,
    LastauthView,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_aggregated_browser_info,
    auth_aggregated_ip_info,
    auth_aggregated_item,
    auth_aggregated_oauth_info,
    auth_aggregated_os_info,
    auths_aggregated_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.track_manager import create_track_id


TEST_UID = 123
TEST_SESSIONID = 'sessionid'
TEST_COOKIE = 'Session_id=%s' % TEST_SESSIONID
TEST_EDA_COOKIE = 'Eda_id=%s' % TEST_SESSIONID
TEST_HOST = 'passport-test.yandex.ru'
TEST_USER_IP = '3.3.3.3'
TEST_YANDEXUID = '1230'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HISTORYDB_API_URL='http://localhost/',
)
class TestLastauthView(BaseBundleTestViews):

    default_url = '/1/bundle/account/lastauth/'
    http_method = 'get'
    http_query_args = dict(
        consumer='dev',
    )
    http_headers = dict(
        user_ip=TEST_USER_IP,
        cookie=TEST_COOKIE,
        host=TEST_HOST,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.set_grants()

        self.env.statbox.bind_entry(
            'lastauth',
            mode='lastauth',
            user_ip=TEST_USER_IP,
            uid=str(TEST_UID),
            consumer='dev',
            authtypes='imap,pop3',
            useragent='curl',
            yandexuid=TEST_YANDEXUID,
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def set_grants(self, by_uid=False):
        grants = {}
        for grant in (LASTAUTH_BASIC_GRANT,):
            prefix, suffix = grant.split('.')
            grants.setdefault(prefix, []).append(suffix)
        if by_uid:
            prefix, suffix = LASTAUTH_BY_UID_GRANT.split('.')
            grants.setdefault(prefix, []).append(suffix)
        self.env.grants.set_grants_return_value(mock_grants(grants=grants))

    def default_userinfo_response(self, uid=TEST_UID, enabled=True, attributes=None):
        return blackbox_userinfo_response(
            uid=uid,
            enabled=enabled,
            attributes=attributes,
        )

    def default_sessionid_response(self, uid=TEST_UID):
        return blackbox_sessionid_multi_response(uid=uid)

    def simple_lastauth_response(self):
        return {
            'tokens': {},
            'password': {
                'web': [
                    {
                        'timestamp': 3600,
                        'authtype': authtypes.AUTH_TYPE_WEB,
                        'ip': {
                            'AS': 13238,
                            'geoid': 9999,
                            'value': '2a02:6b8:0:101:19c3:e71d:2e1d:5017',
                        },
                        'os': {
                            'version': '6.1',
                            'name': 'Windows 7',
                        },
                        'browser': {
                            'version': '33.0',
                            'name': 'Firefox',
                        },
                    },
                ],
                'apps': [],
            },
            'application_passwords': {},
        }

    def set_historydb_api_auths_aggregated(self, uid=TEST_UID, auths=None):
        self.env.historydb_api.set_response_value(
            'auths_aggregated',
            auths_aggregated_response(uid=uid, auths=auths),
        )

    def test_no_uid_and_session_fails(self):
        """
        Если не передан uid и Session_id, то отвечаем
        ошибкой request.uid_or_session_expected
        """
        resp = self.make_request(exclude_headers=['cookie'])
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['request.credentials_all_missing'])

    def test_both_uid_sessionid_fails(self):
        """
        Если передан uid и Session_id, то отвечаем
        ошибкой request.uid_session_both_present
        """
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            headers=dict(cookie='Session_id='),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['request.credentials_several_present'])

    def test_unknown_uid_fails(self):
        """
        Если передали неизвестный uid, то отвечаем
        ошибкой account.not_found
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['account.not_found'])

    def test_by_uid_no_grant_fails(self):
        """
        Для запроса по uid необходимо иметь дополнительный грант
        """
        self.set_grants(by_uid=False)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        eq_(resp.status_code, 403)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['access.denied'])

    def test_disabled_uid_account_fails(self):
        """
        Запрос по uid.
        Если пользователь заблокирован, то отвечаем
        ошибкой account.disabled
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(enabled=False),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['account.disabled'])

    def test_disabled_on_deletion_uid_account_fails(self):
        """
        Запрос по uid.
        Если пользователь заблокирован, то отвечаем
        ошибкой account.disabled
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['account.disabled_on_deletion'])

    def test_invalid_sessionid_fails(self):
        """
        Если сессия невалидная, то отвечаем
        ошибкой sessionid.invalid
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=TEST_UID,
            ),
        )
        resp = self.make_request(headers=dict(cookie='Session_id='))
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['sessionid.invalid'])

    def test_invalid_sessionid_fails_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=TEST_UID,
            ),
        )
        resp = self.make_request(headers=dict(cookie='Session_id='))
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['sessionid.invalid'])

    def test_disabled_sessionid_account_fails(self):
        """
        Запрос по Session_id.
        Если пользователь заблокирован, то отвечаем
        ошибкой account.disabled
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                uid=TEST_UID,
            ),
        )
        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['account.disabled'])

    def test_disabled_on_deletion_sessionid_account_fails(self):
        """
        Запрос по Session_id.
        Если пользователь заблокирован, то отвечаем
        ошибкой account.disabled
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                uid=TEST_UID,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['account.disabled_on_deletion'])

    def test_disabled_sessionid_account_fails_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                uid=TEST_UID,
            ),
        )
        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['account.disabled'])

    def test_disabled_on_deletion_sessionid_account_fails_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                uid=TEST_UID,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['account.disabled_on_deletion'])

    def test_by_uid_ok(self):
        """
        Запрос по uid.
        В ответе в поле lastauth последние аутентификации пользователя
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_grants(by_uid=True)
        self.set_historydb_api_auths_aggregated()
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(
            resp['lastauth'],
            self.simple_lastauth_response(),
        )

    def test_by_sessionid_ok(self):
        """
        Запрос по Session_id.
        В ответе в поле lastauth последние аутентификации пользователя
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        self.set_historydb_api_auths_aggregated()
        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(
            resp['lastauth'],
            self.simple_lastauth_response(),
        )

    def test_by_sessionid_with_apps_ok(self):
        """
        Проверим, что записываем в статбокс данные, если
        в последних сессиях были сессии "приложений".
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        self.set_historydb_api_auths_aggregated(
            auths=[
                auth_aggregated_item(
                    ts=7,
                    authtype=authtypes.AUTH_TYPE_POP3,
                    ip_info=auth_aggregated_ip_info(
                        AS=99,
                        ip='10.10.10.10',
                    ),
                ),
                auth_aggregated_item(
                    ts=8,
                    authtype=authtypes.AUTH_TYPE_POP3,
                    ip_info=auth_aggregated_ip_info(
                        AS=9999,
                        ip='10.10.10.10',
                    ),
                ),
                # imap
                auth_aggregated_item(
                    ts=9,
                    authtype=authtypes.AUTH_TYPE_IMAP,
                    ip_info=auth_aggregated_ip_info(
                        AS=999,
                        ip='10.10.10.10',
                    ),
                ),
            ],
        )
        track_id = create_track_id()
        resp = self.make_request(
            query_args=dict(enabled_2fa_track_id=track_id),
            headers=dict(
                user_agent='curl',
                cookie=TEST_COOKIE + ';yandexuid=1230',
            ),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(
            resp['lastauth'],
            {
                'tokens': {},
                'password': {
                    'web': [],
                    'apps': [
                        {
                            'timestamp': 9,
                            'authtype': authtypes.AUTH_TYPE_IMAP,
                            'ip': {
                                'AS': 999,
                                'geoid': 9999,
                                'value': '10.10.10.10',
                            },
                        },
                        {
                            'timestamp': 8,
                            'authtype': authtypes.AUTH_TYPE_POP3,
                            'ip': {
                                'AS': 9999,
                                'geoid': 9999,
                                'value': u'10.10.10.10',
                            },
                        },
                        {
                            'timestamp': 7,
                            'authtype': authtypes.AUTH_TYPE_POP3,
                            'ip': {
                                'AS': 99,
                                'geoid': 9999,
                                'value': u'10.10.10.10',
                            },
                        },
                    ],
                },
                'application_passwords': {},
            },
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'lastauth',
                unixtime=TimeNow(),
                enabled_2fa_track_id=track_id,
            ),
        ])


class TestBuildLastauth(unittest.TestCase):
    def setUp(self):
        self.view = LastauthView()

    def build_lastauth(self, auths):
        return self.view.build_auths_aggregated(auths)

    def test_empty(self):
        """
        У пользователя пустая агрегированная история
        """
        eq_(
            self.build_lastauth([]),
            {
                'tokens': {},
                'password': {'web': [], 'apps': []},
                'application_passwords': {},
            },
        )

    def test_complete(self):
        """
        Проверка формирования lastauth для всех типов авторизаций
        """
        auths = [
            # web аутентификации склеятся по AS
            auth_aggregated_item(
                ts=1,
                authtype=authtypes.AUTH_TYPE_WEB,
                os_info=auth_aggregated_os_info('Windows', '222'),
                browser_info=auth_aggregated_browser_info(),
                ip_info=auth_aggregated_ip_info(
                    AS=8888,
                    geoid=9999,
                    ip='8.8.8.7',
                ),
            ),
            auth_aggregated_item(
                ts=3,
                authtype=authtypes.AUTH_TYPE_WEB,
                os_info=auth_aggregated_os_info('Ubuntu', '333'),
                browser_info=auth_aggregated_browser_info('Chrome', '555'),
                ip_info=auth_aggregated_ip_info(
                    AS=8888,
                    geoid=9999,
                    ip='8.8.8.8',
                ),
            ),
            # web аутентификация с другой AS
            auth_aggregated_item(
                ts=5,
                authtype=authtypes.AUTH_TYPE_WEB,
                os_info=auth_aggregated_os_info('Ubuntu', '333'),
                ip_info=auth_aggregated_ip_info(
                    AS=9999,
                    ip='9.9.9.8',
                ),
            ),
            # web аутентификация без определенной AS
            auth_aggregated_item(
                ts=10,
                authtype=authtypes.AUTH_TYPE_OAUTH_CREATE,
                os_info=auth_aggregated_os_info('Ubuntu', '333'),
                ip_info=auth_aggregated_ip_info(
                    AS=None,
                    ip='10.10.10.10',
                ),
            ),
            # Создание токена по логину-паролю
            auth_aggregated_item(
                ts=14,
                authtype=authtypes.AGGREGATED_AUTH_TYPE_TOKEN_BY_PASSWORD,
                os_info=auth_aggregated_os_info('Ubuntu', '333'),
                ip_info=auth_aggregated_ip_info(
                    geoid=8888,
                    AS=9999,
                    ip='10.10.10.10',
                ),
                oauth_info=auth_aggregated_oauth_info(
                    token_id='abc',
                    scopes='a:b',
                    device_name='name1',
                    device_id='device_id',
                    client_id='123',
                ),
            ),
            # pop3 аутентификация
            auth_aggregated_item(
                ts=8,
                authtype=authtypes.AUTH_TYPE_POP3,
                ip_info=auth_aggregated_ip_info(
                    AS=9999,
                    ip='10.10.10.10',
                ),
            ),
            # imap
            auth_aggregated_item(
                ts=9,
                authtype=authtypes.AUTH_TYPE_IMAP,
                ip_info=auth_aggregated_ip_info(
                    AS=999,
                    ip='10.10.10.10',
                ),
            ),
            # пароли приложений
            auth_aggregated_item(
                ts=9,
                authtype=authtypes.AUTH_TYPE_IMAP,
                ip_info=auth_aggregated_ip_info(
                    AS=999,
                    ip='10.10.10.10',
                ),
                oauth_info=auth_aggregated_oauth_info(
                    token_id='abc',
                    scopes='a:b',
                    device_name='name1',
                    AP=True,
                ),
            ),
            auth_aggregated_item(
                ts=9,
                authtype=authtypes.AUTH_TYPE_IMAP,
                ip_info=auth_aggregated_ip_info(
                    AS=999,
                    ip='10.10.10.10',
                ),
                oauth_info=auth_aggregated_oauth_info(
                    token_id='def',
                    scopes='a:c',
                    device_name='name2',
                    AP=True,
                ),
            ),
            # oauth токены
            auth_aggregated_item(
                ts=9,
                authtype=authtypes.AUTH_TYPE_OAUTH_CHECK,
                ip_info=auth_aggregated_ip_info(
                    AS=999,
                    ip='10.10.10.10',
                ),
                oauth_info=auth_aggregated_oauth_info(
                    token_id='abc',
                    scopes='a:b',
                    device_name='name1',
                ),
            ),
            auth_aggregated_item(
                ts=12,
                authtype=authtypes.AUTH_TYPE_OAUTH_CHECK,
                ip_info=auth_aggregated_ip_info(
                    AS=998,
                    ip='10.10.10.10',
                ),
                oauth_info=auth_aggregated_oauth_info(
                    token_id='abc',
                    scopes='a:b',
                    device_name='name1',
                ),
            ),
            auth_aggregated_item(
                ts=9,
                authtype=authtypes.AUTH_TYPE_OAUTH_CHECK,
                ip_info=auth_aggregated_ip_info(
                    AS=999,
                    ip='10.10.10.10',
                ),
                oauth_info=auth_aggregated_oauth_info(
                    token_id='def',
                    scopes='a:c',
                    device_name='name2',
                ),
            ),
            auth_aggregated_item(
                ts=12,
                authtype=authtypes.AUTH_TYPE_OAUTH_CHECK,
                ip_info=auth_aggregated_ip_info(
                    AS=998,
                    ip='10.10.10.10',
                ),
                oauth_info=auth_aggregated_oauth_info(
                    token_id=None,
                ),
            ),
        ]
        eq_(
            self.build_lastauth(auths),
            {
                'tokens': {
                    'abc': [
                        {
                            'oauth': {
                                'scopes': 'a:b',
                                'device_name': 'name1',
                                'client_id': '7a54f58d4ebe431caaaa53895522bf2d',
                                'token_id': 'abc',
                                'device_id': 'device_id',
                            },
                            'timestamp': 12,
                            'authtype': authtypes.AUTH_TYPE_OAUTH_CHECK,
                            'ip': {
                                'AS': 998,
                                'geoid': 9999,
                                'value': '10.10.10.10',
                            },
                        },
                        {
                            'oauth': {
                                'scopes': 'a:b',
                                'device_name': 'name1',
                                'client_id': '7a54f58d4ebe431caaaa53895522bf2d',
                                'token_id': 'abc',
                                'device_id': 'device_id',
                            },
                            'timestamp': 9,
                            'authtype': authtypes.AUTH_TYPE_OAUTH_CHECK,
                            'ip': {
                                'AS': 999,
                                'geoid': 9999,
                                'value': '10.10.10.10',
                            },
                        },
                    ],
                    'def': [
                        {
                            'oauth': {
                                'scopes': 'a:c',
                                'device_name': 'name2',
                                'client_id': '7a54f58d4ebe431caaaa53895522bf2d',
                                'token_id': 'def',
                                'device_id': 'device_id',
                            },
                            'timestamp': 9,
                            'authtype': authtypes.AUTH_TYPE_OAUTH_CHECK,
                            'ip': {
                                'AS': 999,
                                'geoid': 9999,
                                'value': '10.10.10.10',
                            },
                        },
                    ],
                },
                'password': {
                    'web': [
                        {
                            'timestamp': 14,
                            'authtype': authtypes.AGGREGATED_AUTH_TYPE_TOKEN_BY_PASSWORD,
                            'os': {
                                'version': '333',
                                'name': 'Ubuntu',
                            },
                            'ip': {
                                'AS': 9999,
                                'geoid': 8888,
                                'value': '10.10.10.10',
                            },
                            'oauth': {
                                'scopes': 'a:b',
                                'device_id': 'device_id',
                                'token_id': 'abc',
                                'client_id': '123',
                                'device_name': 'name1',
                            },
                        },
                        {
                            'timestamp': 10,
                            'authtype': authtypes.AUTH_TYPE_OAUTH_CREATE,
                            'os': {
                                'version': '333',
                                'name': 'Ubuntu',
                            },
                            'ip': {
                                'geoid': 9999,
                                'value': '10.10.10.10',
                            },
                        },
                        {
                            'timestamp': 5,
                            'authtype': authtypes.AUTH_TYPE_WEB,
                            'os': {
                                'version': '333',
                                'name': 'Ubuntu',
                            },
                            'ip': {
                                'AS': 9999,
                                'geoid': 9999,
                                'value': '9.9.9.8',
                            },
                        },
                        {
                            'timestamp': 3,
                            'authtype': authtypes.AUTH_TYPE_WEB,
                            'browser': {
                                'version': '555',
                                'name': 'Chrome',
                            },
                            'os': {
                                'version': '333',
                                'name': 'Ubuntu',
                            },
                            'ip': {
                                'AS': 8888,
                                'geoid': 9999,
                                'value': '8.8.8.8',
                            },
                        },
                    ],
                    'apps': [
                        {
                            'timestamp': 9,
                            'authtype': authtypes.AUTH_TYPE_IMAP,
                            'ip': {
                                'AS': 999,
                                'geoid': 9999,
                                'value': '10.10.10.10',
                            },
                        },
                        {
                            'timestamp': 8,
                            'authtype': authtypes.AUTH_TYPE_POP3,
                            'ip': {
                                'AS': 9999,
                                'geoid': 9999,
                                'value': '10.10.10.10',
                            },
                        },
                    ],
                },
                'application_passwords': {
                    'abc': [
                        {
                            'oauth': {
                                'scopes': 'a:b',
                                'device_name': 'name1',
                                'AP': True,
                                'client_id': '7a54f58d4ebe431caaaa53895522bf2d',
                                'token_id': 'abc',
                                'device_id': 'device_id',
                            },
                            'timestamp': 9,
                            'authtype': authtypes.AUTH_TYPE_IMAP,
                            'ip': {
                                'AS': 999,
                                'geoid': 9999,
                                'value': '10.10.10.10',
                            },
                        },
                    ],
                    'def': [
                        {
                            'oauth': {
                                'scopes': 'a:c',
                                'device_name': 'name2',
                                'AP': True,
                                'client_id': '7a54f58d4ebe431caaaa53895522bf2d',
                                'token_id': 'def',
                                'device_id': 'device_id',
                            },
                            'timestamp': 9,
                            'authtype': authtypes.AUTH_TYPE_IMAP,
                            'ip': {
                                'AS': 999,
                                'geoid': 9999,
                                'value': '10.10.10.10',
                            },
                        },
                    ],
                },
            },
        )
