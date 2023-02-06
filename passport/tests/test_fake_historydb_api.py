# -*- coding: utf-8 -*-

import json
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core import authtypes
from passport.backend.core.builders.historydb_api import HistoryDBApi
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_aggregated_browser_info,
    auth_aggregated_ip_info,
    auth_aggregated_item,
    auth_aggregated_item_old,
    auth_aggregated_oauth_info,
    auth_aggregated_os_info,
    auth_failed_item,
    auth_item,
    auth_successful_aggregated_browser_info,
    auth_successful_aggregated_ip_info,
    auth_successful_aggregated_oauth_info,
    auth_successful_aggregated_os_info,
    auth_successful_aggregated_runtime_auth_item,
    auth_successful_aggregated_runtime_auths_item,
    auth_successful_aggregated_runtime_ip_info,
    auths_aggregated_response,
    auths_aggregated_response_old,
    auths_failed_response,
    auths_response,
    auths_successful_aggregated_runtime_response,
    error_response,
    event_item,
    event_restore_item,
    events_passwords_response,
    events_response,
    events_restore_response,
    FakeHistoryDBApi,
    last_letter_response,
    lastauth_bulk_response,
    lastauth_response,
    mail_history_item,
    mail_history_response,
    push_history_response,
    push_history_response_item,
)
from passport.backend.core.test.test_utils import (
    iterdiff,
    with_settings,
)


eq_ = iterdiff(eq_)


@with_settings(HISTORYDB_API_URL='http://localhost/')
class FakeHistoryDBApiTestCase(unittest.TestCase):
    def setUp(self):
        self.history_db_api = HistoryDBApi()
        self.fake_historydb_api = FakeHistoryDBApi()
        self.fake_historydb_api.start()

    def tearDown(self):
        self.fake_historydb_api.stop()
        del self.fake_historydb_api

    def test_getattr(self):
        eq_(self.fake_historydb_api._mock.foo, self.fake_historydb_api.foo)

    def test_set_response_values(self):
        ok_(not self.fake_historydb_api._mock.request.called)
        self.fake_historydb_api.set_response_value(
            'events',
            events_response(),
        )

        ok_(self.history_db_api.events(123, '127.0.0.1', 1, 10))
        ok_(self.fake_historydb_api._mock.request.called)

    def test_set_response_side_effect(self):
        ok_(not self.fake_historydb_api._mock.request.called)
        self.fake_historydb_api.set_response_side_effect(
            'events',
            ValueError,
        )
        with assert_raises(ValueError):
            self.history_db_api.events(123, '127.0.0.1', 1, 10)

        ok_(self.fake_historydb_api._mock.request.called)

    def test_set_response_values_with_unknown_method(self):
        ok_(not self.fake_historydb_api._mock.request.called)
        with assert_raises(ValueError):
            self.fake_historydb_api.set_response_value(
                'test_method',
                events_response(),
            )

        ok_(not self.fake_historydb_api._mock.request.called)

    def test_set_response_side_effect_with_unknown_method(self):
        ok_(not self.fake_historydb_api._mock.request.called)

        with assert_raises(ValueError):
            self.fake_historydb_api.set_response_side_effect(
                'test_method',
                Exception,
            )

        ok_(not self.fake_historydb_api._mock.request.called)


class FakeResponsesTestCase(unittest.TestCase):
    def test_events_restore_response(self):
        eq_(
            json.loads(events_restore_response()),
            {
                u'uid': 123,
                u'status': u'ok',
                u'restore_events': [
                    {
                        u'action': u'restore_semi_auto_request',
                        u'data_json': u'{"field":"value"}',
                        u'restore_id': u'7E,13079,1408955588.53,3000453634,track_id',
                        u'timestamp': 1234,
                    },
                ],
            },
        )

    @raises(ValueError)
    def test_events_restore_response_incorrect_timestamp_order(self):
        events_restore_response(
            restore_events=[
                event_restore_item(timestamp=1),
                event_restore_item(timestamp=2),
            ],
        )

    def test_auth_successful_aggregated_browser_info(self):
        eq_(
            auth_successful_aggregated_browser_info(name='Foo', version=None),
            {
                'name': 'Foo',
            },
        )

        eq_(
            auth_successful_aggregated_browser_info(name='Bar', version='33.33'),
            {
                'name': 'Bar',
                'version': '33.33',
            },
        )

        eq_(
            auth_successful_aggregated_browser_info(),
            {
                'name': 'Firefox',
                'version': '33.0',
            },
        )

        eq_(
            auth_successful_aggregated_browser_info(yandexuid='1046714081386936400'),
            {
                'name': 'Firefox',
                'version': '33.0',
                'yandexuid': '1046714081386936400',
            },
        )

    def test_auth_successful_aggregated_os_info(self):
        eq_(
            auth_successful_aggregated_os_info(name='Foo', version=None),
            {
                'name': 'Foo',
            },
        )

        eq_(
            auth_successful_aggregated_os_info(name='Bar', version='33.33'),
            {
                'name': 'Bar',
                'version': '33.33',
            },
        )

        eq_(
            auth_successful_aggregated_os_info(),
            {
                'name': 'Windows 7',
                'version': '6.1',
            },
        )

    def test_auth_successful_aggregated_oauth_info(self):
        eq_(
            auth_successful_aggregated_oauth_info(
                client_id='id',
                scopes='foo:bar',
                token_id='yyyzzz',
                device_id='device-id',
                device_name=u'имя устройства',
                AP=True,
            ),
            {
                'client_id': 'id',
                'scopes': 'foo:bar',
                'token_id': 'yyyzzz',
                'device_id': 'device-id',
                'device_name': u'имя устройства',
                'AP': True,
            },
        )

        eq_(
            auth_successful_aggregated_oauth_info(
                client_id='id',
                scopes=None,
                token_id=None,
                device_id=None,
                device_name=None,
                AP=None,
            ),
            {
                'client_id': 'id',
            },
        )

        eq_(
            auth_successful_aggregated_oauth_info(),
            {
                'client_id': '7a54f58d4ebe431caaaa53895522bf2d',
                'scopes': 'cloud_api:disk.write,cloud_api:disk.app_folder',
                'token_id': '123',
                'device_id': 'device_id',
                'device_name': u'имя+девайса',
            },
        )

    def test_auth_successful_aggregated_ip_info(self):
        eq_(
            auth_successful_aggregated_ip_info(
                AS=1234,
                geoid=8888,
                ip='8.8.8.8',
            ),
            {
                'AS': 1234,
                'geoid': 8888,
                'value': '8.8.8.8',
            },
        )

        eq_(
            auth_successful_aggregated_ip_info(),
            {
                'AS': 13238,
                'geoid': 9999,
                'value': '2a02:6b8:0:101:19c3:e71d:2e1d:5017',
            },
        )

    def test_auth_aggregated_oauth_info(self):
        eq_(
            auth_aggregated_oauth_info(
                client_id='id',
                scopes='foo:bar',
                token_id='yyyzzz',
                device_id='device-id',
                device_name=u'имя устройства',
                AP=True,
            ),
            {
                'clientId': 'id',
                'scopes': 'foo:bar',
                'tokenId': 'yyyzzz',
                'deviceId': 'device-id',
                'deviceName': u'имя устройства',
                'AP': True,
            },
        )

        eq_(
            auth_aggregated_oauth_info(
                client_id='id',
                scopes=None,
                token_id=None,
                device_id=None,
                device_name=None,
                AP=None,
            ),
            {
                'clientId': 'id',
            },
        )

        eq_(
            auth_aggregated_oauth_info(),
            {
                'clientId': '7a54f58d4ebe431caaaa53895522bf2d',
                'scopes': 'cloud_api:disk.write,cloud_api:disk.app_folder',
                'tokenId': '123',
                'deviceId': 'device_id',
                'deviceName': u'имя+девайса',
            },
        )

    def test_auth_aggregated_ip_info(self):
        eq_(
            auth_aggregated_ip_info(
                AS=1234,
                geoid=8888,
                ip='8.8.8.8',
            ),
            {
                'AS': 1234,
                'geoid': 8888,
                'ip': '8.8.8.8',
            },
        )

        eq_(
            auth_aggregated_ip_info(),
            {
                'AS': 13238,
                'geoid': 9999,
                'ip': '2a02:6b8:0:101:19c3:e71d:2e1d:5017',
            },
        )

    def test_auth_aggregated_item_old(self):
        eq_(
            auth_aggregated_item_old(
                ts=123,
                authtype=authtypes.AUTH_TYPE_IMAP,
                ip_info=auth_aggregated_ip_info(),
                browser_info=auth_aggregated_browser_info(),
                os_info=auth_aggregated_os_info(),
                oauth_info=auth_aggregated_oauth_info(AP=True),
            ),
            {
                'timestamps': [123],
                'count': 1,
                'auth': {
                    'authtype': authtypes.AUTH_TYPE_IMAP,
                    'os': {
                        'version': '6.1',
                        'name': 'Windows 7',
                    },
                    'ip': {
                        'AS': 13238,
                        'geoid': 9999,
                        'ip': '2a02:6b8:0:101:19c3:e71d:2e1d:5017',
                    },
                    'token': {
                        'scopes': 'cloud_api:disk.write,cloud_api:disk.app_folder',
                        'deviceName': u'\u0438\u043c\u044f+\u0434\u0435\u0432\u0430\u0439\u0441\u0430',
                        'AP': True,
                        'clientId': '7a54f58d4ebe431caaaa53895522bf2d',
                        'tokenId': '123',
                        'deviceId': 'device_id',
                    },
                    'browser': {
                        'version': '33.0',
                        'name': 'Firefox',
                    },
                },
            },
        )

    def test_auth_aggregated_item(self):
        eq_(
            auth_aggregated_item(
                ts=123,
                authtype=authtypes.AUTH_TYPE_IMAP,
                ip_info=auth_aggregated_ip_info(),
                browser_info=auth_aggregated_browser_info(),
                os_info=auth_aggregated_os_info(),
                oauth_info=auth_aggregated_oauth_info(AP=True),
            ),
            {
                'authentications': [
                    {
                        'timestamp': 123,
                    },
                ],
                'count': 1,
                'auth': {
                    'authtype': authtypes.AUTH_TYPE_IMAP,
                    'os': {
                        'version': '6.1',
                        'name': 'Windows 7',
                    },
                    'ip': {
                        'AS': 13238,
                        'geoid': 9999,
                        'ip': '2a02:6b8:0:101:19c3:e71d:2e1d:5017',
                    },
                    'token': {
                        'scopes': 'cloud_api:disk.write,cloud_api:disk.app_folder',
                        'deviceName': u'\u0438\u043c\u044f+\u0434\u0435\u0432\u0430\u0439\u0441\u0430',
                        'AP': True,
                        'clientId': '7a54f58d4ebe431caaaa53895522bf2d',
                        'tokenId': '123',
                        'deviceId': 'device_id',
                    },
                    'browser': {
                        'version': '33.0',
                        'name': 'Firefox',
                    },
                },
            },
        )

    def test_aggregated_response_default_old(self):
        eq_(
            json.loads(auths_aggregated_response_old(uid=123, next='next')),
            {
                'status': 'ok',
                'uid': 123,
                'next': 'next',
                'auths': [
                    {
                        'timestamps': [3600],
                        'count': 1,
                        'auth': {
                            'authtype': authtypes.AUTH_TYPE_WEB,
                            'ip': {
                                'AS': 13238,
                                'geoid': 9999,
                                'ip': u'2a02:6b8:0:101:19c3:e71d:2e1d:5017',
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
                    },
                ],
            },
        )

    def test_aggregated_response_default(self):
        eq_(
            json.loads(auths_aggregated_response(uid=123, next='next')),
            {
                'status': 'ok',
                'uid': 123,
                'next': 'next',
                'auths': [
                    {
                        'authentications': [
                            {
                                'timestamp': 3600,
                            },
                        ],
                        'count': 1,
                        'auth': {
                            'authtype': authtypes.AUTH_TYPE_WEB,
                            'ip': {
                                'AS': 13238,
                                'geoid': 9999,
                                'ip': u'2a02:6b8:0:101:19c3:e71d:2e1d:5017',
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
                    },
                ],
            },
        )

    def test_aggregated_response_old(self):
        auths = [
            auth_aggregated_item_old(
                ts=9999,
                authtype=authtypes.AUTH_TYPE_WEB,
                ip_info=auth_successful_aggregated_ip_info(),
                browser_info=auth_successful_aggregated_browser_info(),
                os_info=auth_successful_aggregated_os_info(),
            ),
            auth_aggregated_item_old(ts=3600, authtype=authtypes.AUTH_TYPE_POP3),
        ]
        eq_(
            json.loads(auths_aggregated_response_old(uid=123, auths=auths, next='next')),
            {
                'status': 'ok',
                'uid': 123,
                'next': 'next',
                'auths': [
                    {
                        'timestamps': [9999],
                        'count': 1,
                        'auth': {
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
                    },
                    {
                        'timestamps': [3600],
                        'count': 1,
                        'auth': {
                            'authtype': 'pop3',
                        },
                    },
                ],
            },
        )

    def test_aggregated_response(self):
        auths = [
            auth_aggregated_item(
                ts=9999,
                authtype=authtypes.AUTH_TYPE_WEB,
                ip_info=auth_successful_aggregated_ip_info(),
                browser_info=auth_successful_aggregated_browser_info(),
                os_info=auth_successful_aggregated_os_info(),
            ),
            auth_aggregated_item(ts=3600, authtype=authtypes.AUTH_TYPE_POP3),
        ]
        eq_(
            json.loads(auths_aggregated_response(uid=123, auths=auths, next='next')),
            {
                'status': 'ok',
                'uid': 123,
                'next': 'next',
                'auths': [
                    {
                        'authentications': [
                            {
                                'timestamp': 9999,
                            },
                        ],
                        'count': 1,
                        'auth': {
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
                    },
                    {
                        'authentications': [
                            {
                                'timestamp': 3600,
                            },
                        ],
                        'count': 1,
                        'auth': {
                            'authtype': 'pop3',
                        },
                    },
                ],
            },
        )

    def test_successful_aggregated_runtime_response_default(self):
        eq_(
            json.loads(auths_successful_aggregated_runtime_response()),
            {
                'status': 'ok',
                'uid': 123,
                'history': [],
            },
        )

    @raises(ValueError)
    def test_successful_aggregated_runtime_response_incorrect_timestamp_order(self):
        auths_successful_aggregated_runtime_response(
            items=[
                auth_successful_aggregated_runtime_auths_item(timestamp=1),
                auth_successful_aggregated_runtime_auths_item(timestamp=2),
            ],
        )

    def test_successful_aggregated_runtime_response(self):
        eq_(
            json.loads(auths_successful_aggregated_runtime_response(
                items=[
                    auth_successful_aggregated_runtime_auths_item(
                        auth_items=[
                            auth_successful_aggregated_runtime_auth_item(
                                authtype=authtypes.AUTH_TYPE_IMAP,
                                status='successful',
                                os_info=auth_successful_aggregated_os_info(),
                            ),
                            auth_successful_aggregated_runtime_auth_item(
                                ip_info=auth_successful_aggregated_runtime_ip_info(),
                                browser_info=auth_successful_aggregated_browser_info(yandexuid='1'),
                                count=10,
                            ),
                        ],
                    ),
                    auth_successful_aggregated_runtime_auths_item(timestamp=0),
                ],
            )),
            {
                'status': 'ok',
                'uid': 123,
                'history': [
                    {
                        'auths': [
                            {
                                'auth': {
                                    'status': 'successful',
                                    'ip': {},
                                    'authtype': authtypes.AUTH_TYPE_IMAP,
                                    'os': {'version': '6.1', 'name': 'Windows 7'},
                                    'browser': {},
                                },
                                'count': 1,
                            },
                            {
                                'auth': {
                                    'status': 'ses_create',
                                    'ip': {
                                        'AS': 13238,
                                        'geoid': 9999,
                                        'ip': '2a02:6b8:0:101:19c3:e71d:2e1d:5017',
                                    },
                                    'authtype': authtypes.AUTH_TYPE_WEB,
                                    'os': {},
                                    'browser': {
                                        'version': '33.0',
                                        'name': 'Firefox',
                                        'yandexuid': '1',
                                    },
                                },
                                'count': 10,
                            },
                        ],
                        'timestamp': 1418256000,
                    },
                    {
                        'auths': [
                            {
                                'auth': {
                                    'status': 'ses_create',
                                    'ip': {},
                                    'authtype': authtypes.AUTH_TYPE_WEB,
                                    'os': {},
                                    'browser': {},
                                },
                                'count': 1,
                            },
                        ],
                        'timestamp': 0,
                    },
                ],
            },
        )

    def test_auths_response(self):
        auths = [
            auth_item(),
            auth_item(timestamp=7200, authtype=authtypes.AUTH_TYPE_POP3, status='unknown', comment='foo'),
        ]
        eq_(
            json.loads(auths_response(uid=123, auths=auths)),
            {
                'status': 'ok',
                'uid': 123,
                'auths': [
                    {
                        'client_name': 'passport',
                        'host_id': 15,
                        'timestamp': 7200,
                        'user_ip': '87.250.235.4',
                        'type': 'pop3',
                        'status': 'unknown',
                        'comment': 'foo',
                    },
                    {
                        'client_name': 'passport',
                        'host_id': 15,
                        'timestamp': 3600,
                        'user_ip': '87.250.235.4',
                        'type': 'web',
                        'status': 'successful',
                    },
                ],
            },
        )

    def test_auths_failed_response(self):
        auths = [
            auth_failed_item(),
            auth_failed_item(timestamp=7200, authtype=authtypes.AUTH_TYPE_POP3, status='unknown', comment='foo'),
        ]
        eq_(
            json.loads(auths_failed_response(uid=123, auths=auths)),
            {
                'status': 'ok',
                'uid': 123,
                'auths': [
                    {
                        'client_name': 'passport',
                        'host_id': 15,
                        'timestamp': 7200,
                        'user_ip': '87.250.235.4',
                        'type': 'pop3',
                        'status': 'unknown',
                        'comment': 'foo',
                    },
                    {
                        'client_name': 'passport',
                        'host_id': 15,
                        'timestamp': 3600,
                        'user_ip': '87.250.235.4',
                        'type': 'web',
                        'status': 'failed',
                    },
                ],
            },
        )

    def test_events_response(self):
        eq_(
            json.loads(events_response()),
            {
                'status': 'ok',
                'events': [{
                    'name': 'info.firstname',
                    'timestamp': 3600,
                    'yandexuid': '123',
                    'value': 'firstname',
                    'user_ip': '87.250.235.4',
                    'host_id': 15,
                    'client_name': 'passport',
                }],
                'uid': 123,
            },
        )

    @raises(ValueError)
    def test_events_response_incorrect_timestamp_order(self):
        events_response(
            events=[
                event_item(timestamp=1),
                event_item(timestamp=2),
            ],
            ascending=False,
        )

    def test_events_passwords_response(self):
        eq_(
            json.loads(events_passwords_response()),
            {
                'status': 'ok',
                'active_ranges': [],
                'password_found': False,
            },
        )

    def test_events_passwords_valid_range_response(self):
        eq_(
            json.loads(events_passwords_response(active_ranges=[[100, 200], [10, 50]])),
            {
                'status': 'ok',
                'active_ranges': [[100, 200], [10, 50]],
                'password_found': False,
            },
        )

    def test_events_passwords_valid_range_with_none_response(self):
        eq_(
            json.loads(events_passwords_response(active_ranges=[[1, None]])),
            {
                'status': 'ok',
                'active_ranges': [[1, None]],
                'password_found': False,
            },
        )

    def test_events_passwords_invalid_range_fails(self):
        invalid_ranges_values = [
            [
                [None, 1],
            ],
            [
                [2, 1],
            ],
            [
                [1, 2],
                [3, 4],
            ],
            [
                [1000, 2000],
                [500, 1001],
            ],
        ]
        for invalid_ranges in invalid_ranges_values:
            assert_raises(ValueError, events_passwords_response, active_ranges=invalid_ranges)

    def test_lastauth_defaults(self):
        eq_(
            json.loads(lastauth_response()),
            {
                'status': 'ok',
                'uid': 123,
                'lastauth': {
                    'type': authtypes.AUTH_TYPE_WEB,
                    'timestamp': 10000.5,
                },
            },
        )

    def test_lastauth_override_defaults(self):
        eq_(
            json.loads(
                lastauth_response(
                    uid=5,
                    _type=authtypes.AUTH_TYPE_OAUTH_CHECK,
                    timestamp=323.2,
                ),
            ),
            {
                'status': 'ok',
                'uid': 5,
                'lastauth': {
                    'type': authtypes.AUTH_TYPE_OAUTH_CHECK,
                    'timestamp': 323.2,
                },
            },
        )

    def test_lastauth_float_timestamp(self):
        response = json.loads(lastauth_response(timestamp=3232))
        eq_(response['lastauth']['timestamp'], 3232.0)

        response = json.loads(lastauth_response(timestamp=3232.3))
        eq_(response['lastauth']['timestamp'], 3232.3)

    def test_no_lastauth(self):
        eq_(
            json.loads(lastauth_response(_type=None)),
            {
                'status': 'ok',
                'uid': 123,
                'lastauth': {},
            },
        )

    def test_lastauth_bulk_response(self):
        eq_(
            json.loads(lastauth_bulk_response({1: 42, 2: None})),
            {
                'status': 'ok',
                'lastauth': {
                    '1': {'timestamp': 42.0},
                    '2': {},
                },
            },
        )

    def test_mail_history_response(self):
        items = [
            mail_history_item(),
            mail_history_item(date=42000, operation='read', state='123', user_ip='8.8.8.8'),
        ]
        eq_(
            json.loads(mail_history_response(uid=123, items=items)),
            {
                'status': 'ok',
                'uid': 123,
                'items': [
                    {
                        'affected': '1',
                        'connectionId': '2c84bc9e7c2bd478f3fa82de5f1bd0be',
                        'date': 1414666675947,
                        'hidden': '0',
                        'ip': '87.250.235.4',
                        'mdb': 'mdb302',
                        'module': 'mailbox_oper',
                        'operation': 'mark',
                        'regionId': '0',
                        'state': 'read;2160000000004499501',
                        'suid': '1120000000348711',
                        'target': 'message',
                        'yandexuidCookie': '7207633351394011299',
                    },
                    {
                        'affected': '1',
                        'connectionId': '2c84bc9e7c2bd478f3fa82de5f1bd0be',
                        'date': 42000,
                        'hidden': '0',
                        'ip': '8.8.8.8',
                        'mdb': 'mdb302',
                        'module': 'mailbox_oper',
                        'operation': 'read',
                        'regionId': '0',
                        'state': '123',
                        'suid': '1120000000348711',
                        'target': 'message',
                        'yandexuidCookie': '7207633351394011299',
                    },
                ],
            },
        )

    def test_last_letter_response(self):
        eq_(
            json.loads(last_letter_response(uid=123, list_id_to_ts={1: 42, 2: 43})),
            {
                'status': 'ok',
                'uid': 123,
                'items': {
                    '1': {
                        'email_sent_ts': 42,
                    },
                    '2': {
                        'email_sent_ts': 43,
                    },
                },
            },
        )

    def push_history_response(self):
        eq_(
            json.loads(push_history_response(
                push_history_response_item(
                    app_id='app1',
                    push_id='abcdef',
                    unixtime=123456,
                    device_id='fcdea',
                    details='Something',
                    status='ok',
                    push_event='push1',
                    push_service='service1',
                    context='123456abcdef',
                    subscription_id='ffccddee',
                ),
            )),
            {
                'status': 'ok',
                'items': [
                    {
                        'uid': 123,
                        'app_id': 'app1',
                        'push_id': 'abcdef',
                        'unixtime': 123456,
                        'device_id': 'fcdea',
                        'details': 'Something',
                        'status': 'ok',
                        'push_event': 'push1',
                        'push_service': 'service1',
                        'context': '123456abcdef',
                        'subscription_id': 'ffccddee',
                    },
                ],
            },
        )

    def test_default_error_response(self):
        eq_(
            json.loads(error_response()),
            {
                'status': 'error',
                'errors': ['internal'],
            },
        )

    def test_custom_error_response(self):
        eq_(
            json.loads(error_response(['custom1', 'custom2'])),
            {
                'status': 'error',
                'errors': ['custom1', 'custom2'],
            },
        )
