# -*- coding: utf-8 -*-

from functools import partial
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    assert_raises_regexp,
    eq_,
    raises,
)
from passport.backend.core import authtypes
from passport.backend.core.builders.historydb_api import (
    HistoryDBApi,
    HistoryDBApiInvalidResponseError,
    HistoryDBApiPermanentError,
    HistoryDBApiTemporaryError,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_failed_item,
    auth_item,
    auths_failed_response,
    auths_response,
    FakeHistoryDBApi,
    last_letter_response,
    lastauth_bulk_response,
    lastauth_response,
    mail_history_item,
    mail_history_response,
    method_names as all_method_names,
    push_history_response,
    push_history_response_item,
)
from passport.backend.core.builders.historydb_api.parsers import (
    parse_auths_aggregated,
    parse_auths_aggregated_runtime,
    parse_historydb_api_events,
    parse_historydb_api_events_passwords,
    parse_historydb_api_events_restore,
    parse_historydb_api_json,
    parse_last_letter,
    parse_mail_history,
    parse_push_history,
)
from passport.backend.core.test.test_utils import (
    with_settings,
    with_settings_hosts,
)


TEST_SERVICE_TICKET = 'service-ticket'

NEXT_ROW_POINTER = 'next-row'
AUTHS_AGGREGATED_OLD_TEST_RESPONSE = '''{
    "auths": [
        {
            "timestamps": [
                1414408467.72
            ],
            "count": 1,
            "auth": {
                "browser": {
                    "name": "Firefox",
                    "version": "33.0"
                },
                "ip": {
                    "AS": 13238,
                    "geoid": 9999,
                    "value": "2a02:6b8:0:101:19c3:e71d:2e1d:5017"
                },
                "os": {
                    "name": "Ubuntu"
                },
                "authtype": "web"
            }
        }
    ],
    "next": "next-row",
    "status": "ok",
    "uid": 4000188396
}
'''

AUTHS_AGGREGATED_TEST_RESPONSE = '''{
    "auths": [
        {
            "auth": {
                "authtype": "web",
                "browser": {
                    "name": "Chrome",
                    "version": "50.0.2661"
                },
                "ip": {
                    "AS": 13238,
                    "geoid": 9999,
                    "ip": "141.8.176.210"
                },
                "os": {
                    "name": "Windows 7",
                    "version": "6.1"
                }
            },
            "authentications": [
                {
                    "accuracy": 15000,
                    "latitude": 10.0,
                    "longitude": 15.0,
                    "precision": "district",
                    "timestamp": 1464869691.42
                }
            ],
            "count": 1
        }
    ],
    "next": "next-row",
    "status": "ok",
    "uid": 4000144046
}
'''

AUTHS_AGGREGATED_RUNTIME_TEST_RESPONSE = '''{
   "history" : [
      {
         "auths" : [
            {
               "auth" : {
                  "ip" : {
                     "ip" : "213.180.216.66",
                     "AS" : 13238,
                     "geoid" : 9999
                  },
                  "status" : "ses_create",
                  "browser" : {
                     "version" : "36.0",
                     "name" : "Firefox"
                  },
                  "authtype" : "web",
                  "os" : {
                     "name" : "Ubuntu"
                  }
               },
               "count" : 1
            }
         ],
         "timestamp" : 1428624000
      }
   ],
   "next": "next-row",
   "uid" : 3000453634,
   "status" : "ok"
}

'''


@with_settings_hosts(HISTORYDB_API_URL='http://localhost/')
class TestHistoryDBApi(unittest.TestCase):
    def setUp(self):
        self.historydb_api = HistoryDBApi()
        self.faker = FakeHistoryDBApi()
        self.faker.start()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_request_builder(self):
        eq_(
            self.historydb_api._request_builder('/foo/bar/', {'a': 'b'}).url,
            'http://localhost/foo/bar/?a=b&consumer=passport',
        )
        eq_(
            self.historydb_api._request_builder('/foo/bar/', {}).url,
            'http://localhost/foo/bar/?consumer=passport',
        )

    def test_server_error(self):
        self._set_response(
            'last_letter',
            last_letter_response(list_id_to_ts={1: 100500}),
            status=500,
        )
        with assert_raises(HistoryDBApiTemporaryError):
            self.historydb_api.last_letter(None, None)

    def test_server_access_denied(self):
        self._set_response(
            'last_letter',
            last_letter_response(list_id_to_ts={1: 100500}),
            status=403,
        )
        with assert_raises_regexp(
            HistoryDBApiPermanentError, r'^Invalid auth$',
        ):
            self.historydb_api.last_letter(None, None)

    def test_unknown_code_error(self):
        self._set_response(
            'last_letter',
            last_letter_response(list_id_to_ts={1: 100500}),
            status=-1,
        )
        with assert_raises_regexp(
            HistoryDBApiPermanentError, r'^Bad response status code: -1$',
        ):
            self.historydb_api.last_letter(None, None)

    def test_events(self):
        self._set_response(
            'events',
            '{"events": [{"a": "b"}], "status": "ok", "uid": 123}',
        )

        events = self.historydb_api.events(123, 0, 100, 1000)

        requests = self._get_requests()
        eq_(len(requests), 1)
        events_url = self._build_url('/2/events/?consumer=passport&uid=123&from_ts=0&to_ts=100&limit=1000')
        requests[0].assert_properties_equal(method='GET', url=events_url)
        eq_(events, [{'a': 'b'}])

    def test_events_without_limit(self):
        self._set_response(
            'events',
            '{"events": [{"a": "b"}], "status": "ok", "uid": 123}',
        )

        events = self.historydb_api.events(123, 0, 100)

        requests = self._get_requests()
        eq_(len(requests), 1)
        events_url = self._build_url('/2/events/?consumer=passport&uid=123&from_ts=0&to_ts=100')
        requests[0].assert_properties_equal(method='GET', url=events_url)
        eq_(events, [{'a': 'b'}])

    def test_events_ascending(self):
        self._set_response(
            'events',
            '{"events": [{"a": "b"}], "status": "ok", "uid": 123}',
        )

        events = self.historydb_api.events(123, 0, 100, ascending=True)

        requests = self._get_requests()
        eq_(len(requests), 1)
        events_url = self._build_url('/2/events/?consumer=passport&uid=123&from_ts=0&to_ts=100&order_by=asc')
        requests[0].assert_properties_equal(method='GET', url=events_url)
        eq_(events, [{'a': 'b'}])

    def test_events_restore(self):
        self._set_response(
            'events_restore',
            '{"restore_events": [{"a": "b"}], "status": "ok", "uid": 123}',
        )

        events = self.historydb_api.events_restore(123, 0, 100)

        requests = self._get_requests()
        eq_(len(requests), 1)
        restore_url = self._build_url('/2/events/restore/?consumer=passport&uid=123&from_ts=0&to_ts=100')
        requests[0].assert_properties_equal(method='GET', url=restore_url)
        eq_(events, [{'a': 'b'}])

    def test_events_restore_ascending(self):
        self._set_response(
            'events_restore',
            '{"restore_events": [{"a": "b"}], "status": "ok", "uid": 123}',
        )

        events = self.historydb_api.events_restore(123, 0, 100, ascending=True)

        requests = self._get_requests()
        eq_(len(requests), 1)
        restore_url = self._build_url('/2/events/restore/?consumer=passport&uid=123&from_ts=0&to_ts=100&order_by=asc')
        requests[0].assert_properties_equal(method='GET', url=restore_url)
        eq_(events, [{'a': 'b'}])

    def test_events_passwords(self):
        self._set_response(
            'events_passwords',
            '{"password_found": false, "status": "ok", '
            '"active_ranges": []}',
        )

        password_found, ranges = self.historydb_api.events_passwords(
            123,
            'qwerty',
            0,
            9999999,
        )

        requests = self._get_requests()
        eq_(len(requests), 1)
        passwords_url = self._build_url('/2/events/passwords/?consumer=passport')
        requests[0].assert_properties_equal(
            method='POST',
            url=passwords_url,
            post_args={
                'uid': 123,
                'password': 'qwerty',
                'from_ts': 0,
                'to_ts': 9999999,
            },
        )
        eq_(password_found, False)
        eq_(ranges, [])

    def test_auths_aggregated_old(self):
        self._set_response('auths_aggregated_old', AUTHS_AGGREGATED_OLD_TEST_RESPONSE)

        data, next_row = self.historydb_api.auths_aggregated_old(123, 1000, 24, from_row='xyz', password_auths=True)

        requests = self._get_requests()
        eq_(len(requests), 1)
        auths_aggregated_url = self._build_url(
            '/2/auths/aggregated/?consumer=passport&uid=123&limit=1000&hours_limit=24&from=xyz&password_auths=true',
        )
        requests[0].assert_properties_equal(
            method='GET',
            url=auths_aggregated_url,
        )
        eq_(data, json.loads(AUTHS_AGGREGATED_OLD_TEST_RESPONSE)['auths'])
        eq_(next_row, NEXT_ROW_POINTER)

    def test_auths_aggregated_old_password_auths_false(self):
        self._set_response('auths_aggregated_old', AUTHS_AGGREGATED_OLD_TEST_RESPONSE)

        data, next_row = self.historydb_api.auths_aggregated_old(123, 1000, 24, from_row='xyz', password_auths=False)

        requests = self._get_requests()
        eq_(len(requests), 1)
        auths_aggregated_url = self._build_url(
            '/2/auths/aggregated/?consumer=passport&uid=123&limit=1000&hours_limit=24&from=xyz&password_auths=false',
        )
        requests[0].assert_properties_equal(
            method='GET',
            url=auths_aggregated_url,
        )
        eq_(data, json.loads(AUTHS_AGGREGATED_OLD_TEST_RESPONSE)['auths'])
        eq_(next_row, NEXT_ROW_POINTER)

    def test_auths_aggregated_old_without_optional_params(self):
        self._set_response('auths_aggregated_old', AUTHS_AGGREGATED_OLD_TEST_RESPONSE)

        data, next_row = self.historydb_api.auths_aggregated_old(123)

        requests = self._get_requests()
        eq_(len(requests), 1)
        auths_aggregated_url = self._build_url('/2/auths/aggregated/?consumer=passport&uid=123')
        requests[0].assert_properties_equal(
            method='GET',
            url=auths_aggregated_url,
        )
        eq_(data, json.loads(AUTHS_AGGREGATED_OLD_TEST_RESPONSE)['auths'])
        eq_(next_row, NEXT_ROW_POINTER)

    def test_auths_aggregated(self):
        self._set_response('auths_aggregated', AUTHS_AGGREGATED_TEST_RESPONSE)

        data, next_row = self.historydb_api.auths_aggregated(123, 1000, 24, from_row='xyz', password_auths=True)

        requests = self._get_requests()
        eq_(len(requests), 1)
        auths_aggregated_url = self._build_url(
            '/3/auths/aggregated/?consumer=passport&uid=123&limit=1000&hours_limit=24&from=xyz&password_auths=true',
        )
        requests[0].assert_properties_equal(
            method='GET',
            url=auths_aggregated_url,
        )
        eq_(data, json.loads(AUTHS_AGGREGATED_TEST_RESPONSE)['auths'])
        eq_(next_row, NEXT_ROW_POINTER)

    def test_auths_aggregated_password_auths_false(self):
        self._set_response('auths_aggregated', AUTHS_AGGREGATED_TEST_RESPONSE)

        data, next_row = self.historydb_api.auths_aggregated(123, 1000, 24, from_row='xyz', password_auths=False)

        requests = self._get_requests()
        eq_(len(requests), 1)
        auths_aggregated_url = self._build_url(
            '/3/auths/aggregated/?consumer=passport&uid=123&limit=1000&hours_limit=24&from=xyz&password_auths=false',
        )
        requests[0].assert_properties_equal(
            method='GET',
            url=auths_aggregated_url,
        )
        eq_(data, json.loads(AUTHS_AGGREGATED_TEST_RESPONSE)['auths'])
        eq_(next_row, NEXT_ROW_POINTER)

    def test_auths_aggregated_without_optional_params(self):
        self._set_response('auths_aggregated', AUTHS_AGGREGATED_TEST_RESPONSE)

        data, next_row = self.historydb_api.auths_aggregated(123)

        requests = self._get_requests()
        eq_(len(requests), 1)
        auths_aggregated_url = self._build_url('/3/auths/aggregated/?consumer=passport&uid=123')
        requests[0].assert_properties_equal(
            method='GET',
            url=auths_aggregated_url,
        )
        eq_(data, json.loads(AUTHS_AGGREGATED_TEST_RESPONSE)['auths'])
        eq_(next_row, NEXT_ROW_POINTER)

    def test_auths_aggregated_runtime(self):
        self._set_response('auths_aggregated_runtime', AUTHS_AGGREGATED_RUNTIME_TEST_RESPONSE)

        data = self.historydb_api.auths_aggregated_runtime(123, 0, 1000, 10000)

        requests = self._get_requests()
        eq_(len(requests), 1)
        auths_aggregated_runtime_url = self._build_url('/2/auths/aggregated/runtime/?consumer=passport&uid=123&to_ts=1000&from_ts=0&limit=10000')
        requests[0].assert_properties_equal(
            method='GET',
            url=auths_aggregated_runtime_url,
        )
        eq_(data, json.loads(AUTHS_AGGREGATED_RUNTIME_TEST_RESPONSE))

    def test_auths_aggregated_runtime_without_limit(self):
        self._set_response('auths_aggregated_runtime', AUTHS_AGGREGATED_RUNTIME_TEST_RESPONSE)

        data = self.historydb_api.auths_aggregated_runtime(123, 0, 1000)

        requests = self._get_requests()
        eq_(len(requests), 1)
        auths_aggregated_runtime_url = self._build_url('/2/auths/aggregated/runtime/?consumer=passport&uid=123&to_ts=1000&from_ts=0')
        requests[0].assert_properties_equal(
            method='GET',
            url=auths_aggregated_runtime_url,
        )
        eq_(data, json.loads(AUTHS_AGGREGATED_RUNTIME_TEST_RESPONSE))

    def test_auths(self):
        self._set_response('auths', auths_response())

        data = self.historydb_api.auths(123, 0, 1000)

        requests = self._get_requests()
        eq_(len(requests), 1)
        auths_url = self._build_url('/2/auths/?consumer=passport&uid=123&to_ts=1000&from_ts=0')
        requests[0].assert_properties_equal(
            method='GET',
            url=auths_url,
        )
        eq_(data, [auth_item()])

    def test_auths__custom_params(self):
        self._set_response('auths', auths_response())

        data = self.historydb_api.auths(
            uid=123,
            from_ts=0,
            to_ts=1000,
            limit=10,
            ascending=True,
            statuses=['successful', 'unknown'],
            auth_types=['imap', 'smtp'],
            client_names=['passport', 'bb'],
        )

        requests = self._get_requests()
        eq_(len(requests), 1)
        auths_url = self._build_url('/2/auths/?consumer=passport&uid=123&to_ts=1000&from_ts=0&limit=10&order_by=asc&status=successful,unknown&type=imap,smtp&client_name=passport,bb')
        requests[0].assert_properties_equal(
            method='GET',
            url=auths_url,
        )
        eq_(data, [auth_item()])

    def test_auths_failed(self):
        self._set_response('auths_failed', auths_failed_response())

        data = self.historydb_api.auths_failed(123, 0, 1000, limit=10, status='failed')

        requests = self._get_requests()
        eq_(len(requests), 1)
        auths_failed_url = self._build_url('/2/auths/failed/?consumer=passport&uid=123&to_ts=1000&from_ts=0&limit=10&status=failed')
        requests[0].assert_properties_equal(
            method='GET',
            url=auths_failed_url,
        )
        eq_(data, [auth_failed_item()])

    def test_lastauth__ok(self):
        self._set_response('lastauth', lastauth_response())

        response = self.historydb_api.lastauth(123)

        eq_(len(self.faker.requests), 1)
        self.faker.requests[0].assert_properties_equal(
            method='GET',
            url=self._build_url('/2/lastauth/?consumer=passport&uid=123'),
        )

        eq_(
            response,
            {
                'type': authtypes.AUTH_TYPE_WEB,
                'timestamp': 10000.5,
            },
        )

    def test_lastauth_bulk__ok(self):
        self._set_response('lastauth_bulk', lastauth_bulk_response({1: 42, 2: None}))

        response = self.historydb_api.lastauth_bulk([1, 2])

        eq_(len(self.faker.requests), 1)
        self.faker.requests[0].assert_properties_equal(
            method='GET',
            url=self._build_url('/2/lastauth/bulk/?consumer=passport&uids=1,2'),
        )

        eq_(
            response,
            {
                1: 42.0,
                2: None,
            },
        )

    def test_mail_history(self):
        self._set_response('mail_history', mail_history_response())

        data = self.historydb_api.mail_history(123, 0, 1000)

        requests = self._get_requests()
        eq_(len(requests), 1)
        url = self._build_url('/mail/2/user_history/?consumer=passport&uid=123&to_ts=1000&from_ts=0')
        requests[0].assert_properties_equal(
            method='GET',
            url=url,
        )
        eq_(data, [mail_history_item()])

    def test_mail_history__custom_params(self):
        self._set_response('mail_history', mail_history_response())

        data = self.historydb_api.mail_history(
            uid=123,
            from_ts=0,
            to_ts=1000,
            limit=10,
            is_corp=True,
            operations=['mark', 'read'],
            modules=['husky', 'mulca'],
        )

        requests = self._get_requests()
        eq_(len(requests), 1)
        url = self._build_url('/mail/2/user_history/?consumer=passport&uid=123&to_ts=1000&from_ts=0&limit=10&corp=true&operation=mark,read&module=husky,mulca')
        requests[0].assert_properties_equal(
            method='GET',
            url=url,
        )
        eq_(data, [mail_history_item()])

    def test_last_letter(self):
        self._set_response('last_letter', last_letter_response(list_id_to_ts={1: 100500}))

        data = self.historydb_api.last_letter('test_ticket', 3600)

        requests = self._get_requests()
        eq_(len(requests), 1)
        url = self._build_url('/sender/2/last_letter/?consumer=passport&max_age=3600')
        requests[0].assert_properties_equal(
            method='GET',
            url=url,
            headers={'X-Ya-User-Ticket': 'test_ticket'},
        )
        eq_(data, {1: 100500})

    def test_push_history_by_fields(self):
        self._set_response(
            'push_history_by_fields',
            push_history_response([
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
            ]),
        )

        data = self.historydb_api.push_history_by_fields(
            from_ts=123,
            to_ts=456,
            uid=789,
        )

        requests = self._get_requests()
        eq_(len(requests), 1)
        requests[0].assert_query_equals(dict(
            consumer='passport',
            from_ts='123',
            to_ts='456',
            uid='789',
        ))
        requests[0].assert_properties_equal(method='GET')
        requests[0].assert_url_starts_with('http://localhost/push/2/by_fields/')
        eq_(data, [
            dict(
                uid=123,
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
        ])

    def test_push_history_by_fields_extended(self):
        self._set_response(
            'push_history_by_fields',
            push_history_response([
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
            ]),
        )

        data = self.historydb_api.push_history_by_fields(
            from_ts=123,
            to_ts=456,
            uid=789,
            device='abcdef',
            app='app1',
            subscription='fcde',
            limit=100,
        )

        requests = self._get_requests()
        eq_(len(requests), 1)
        requests[0].assert_query_equals(dict(
            consumer='passport',
            from_ts='123',
            to_ts='456',
            uid='789',
            device='abcdef',
            app='app1',
            subscription='fcde',
            limit='100',
        ))
        requests[0].assert_properties_equal(method='GET')
        requests[0].assert_url_starts_with('http://localhost/push/2/by_fields/')
        eq_(data, [
            dict(
                uid=123,
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
        ])

    def test_push_history_by_push_id(self):
        self._set_response(
            'push_history_by_push_id',
            push_history_response([
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
            ]),
        )

        data = self.historydb_api.push_history_by_push_id(push='aabbccdd',)

        requests = self._get_requests()
        eq_(len(requests), 1)
        requests[0].assert_query_equals(dict(
            push='aabbccdd',
            consumer='passport',
        ))
        requests[0].assert_properties_equal(method='GET')
        requests[0].assert_url_starts_with('http://localhost/push/2/by_push_id/')
        eq_(data, [
            dict(
                uid=123,
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
        ])

    def test_push_history_by_push_id_extended(self):
        self._set_response(
            'push_history_by_push_id',
            push_history_response([
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
            ]),
        )

        data = self.historydb_api.push_history_by_push_id(
            push='aabbccdd',
            uid=789,
            device='abcdef',
            app='app1',
            subscription='fcde',
        )

        requests = self._get_requests()
        eq_(len(requests), 1)
        requests[0].assert_query_equals(dict(
            push='aabbccdd',
            consumer='passport',
            uid='789',
            device='abcdef',
            app='app1',
            subscription='fcde',
        ))
        requests[0].assert_properties_equal(method='GET')
        requests[0].assert_url_starts_with('http://localhost/push/2/by_push_id/')
        eq_(data, [
            dict(
                uid=123,
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
        ])

    def test_with_tvm_ok(self):
        tvm_mock = mock.Mock()
        tvm_mock.get_ticket_by_alias.return_value = TEST_SERVICE_TICKET
        historydb_api = HistoryDBApi(use_tvm=True, tvm_credentials_manager=tvm_mock)

        self._set_response('last_letter', last_letter_response(list_id_to_ts={1: 100500}))

        historydb_api.last_letter('test_ticket', 3600)

        requests = self._get_requests()
        eq_(len(requests), 1)
        url = self._build_url('/sender/2/last_letter/?consumer=passport&max_age=3600')
        requests[0].assert_properties_equal(
            method='GET',
            url=url,
            headers={
                'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
                'X-Ya-User-Ticket': 'test_ticket',
            },
        )

    def test_historydb_api_retries_error(self):
        self.historydb_api.retries = 10
        self._set_response_for_all('{"status": "error", "errors": "Boom!"}')

        calls = self._get_all_handle_calls()
        for call in calls:
            with assert_raises(HistoryDBApiTemporaryError):
                call()
        requests = self._get_requests()
        eq_(len(requests), 10 * len(calls))

    def test_invalid_json(self):
        self.historydb_api.retries = 10
        self._set_response_for_all(b'Exception')

        calls = self._get_all_handle_calls()
        for call in calls:
            with assert_raises(HistoryDBApiInvalidResponseError):
                call()
        requests = self._get_requests()
        eq_(len(requests), len(calls))

    @raises(ValueError)
    def test_user_agent_and_timeout_are_incompatible(self):
        HistoryDBApi(useragent=mock.Mock(name=u'user_agent'), timeout=10)

    def _get_all_handle_calls(self):
        return [
            partial(
                self.historydb_api.events,
                123, 0, 100, 1000,
            ),
            partial(
                self.historydb_api.events_restore,
                123, 0, 100,
            ),
            partial(
                self.historydb_api.events_passwords,
                123, 'qwerty', 100, 1000,
            ),
            partial(
                self.historydb_api.auths_aggregated,
                123, 1000, 24,
            ),
            partial(
                self.historydb_api.auths_aggregated_old,
                123, 1000, 24,
            ),
            partial(
                self.historydb_api.auths_aggregated_runtime,
                123, 0, 1000, 10000,
            ),
            partial(
                self.historydb_api.lastauth,
                123,
            ),
        ]

    def _set_response_for_all(self, response):
        for method in all_method_names:
            self._set_response(method, response)

    def _set_response(self, method, response, status=200):
        self.faker.set_response_value(method, response, status)

    def _get_requests(self):
        return self.faker.requests

    def _build_url(self, url_tail):
        return 'http://localhost{url_tail}'.format(url_tail=url_tail)


@with_settings(HISTORYDB_API_URL='http://localhost/')
class TestHistoryDBApiHelpers(unittest.TestCase):
    def test_parse_historydb_api_json(self):
        json = parse_historydb_api_json('{"123": "456"}')
        eq_(json, {'123': '456'})

    @raises(HistoryDBApiInvalidResponseError)
    def test_parse_historydb_api_json_invalid(self):
        parse_historydb_api_json('invalid')

    def test_parse_historydb_api_events(self):
        eq_(
            parse_historydb_api_events('{"status": "ok", "uid": "123", "events": [{"a": "b"}]}'),
            [{"a": "b"}],
        )

    @raises(HistoryDBApiInvalidResponseError)
    def test_parse_historydb_api_events_invalid(self):
        parse_historydb_api_events('{')

    @raises(HistoryDBApiInvalidResponseError)
    def test_parse_historydb_api_events_no_status(self):
        parse_historydb_api_events('{}')

    @raises(HistoryDBApiTemporaryError)
    def test_parse_historydb_api_events_error(self):
        parse_historydb_api_events('{"status": "error", "errors": ["dberrors"]}')

    def test_parse_historydb_api_events_restore(self):
        eq_(
            parse_historydb_api_events_restore('{"status": "ok", "uid": "123", "restore_events": [{"a": "b"}]}'),
            [{"a": "b"}],
        )

    @raises(HistoryDBApiInvalidResponseError)
    def test_parse_historydb_api_events_restore_invalid(self):
        parse_historydb_api_events_restore('{')

    @raises(HistoryDBApiTemporaryError)
    def test_parse_historydb_api_events_restore_error(self):
        parse_historydb_api_events_restore('{"status": "error", "errors": ["dberrors"]}')

    def test_parse_historydb_api_events_passwords(self):
        eq_(
            parse_historydb_api_events_passwords(
                '{"status": "ok", "password_found": true, "active_ranges": [[0, 1], [100, null]]}',
            ),
            (True, [[0, 1], [100, None]]),
        )

    @raises(HistoryDBApiInvalidResponseError)
    def test_parse_historydb_api_events_passwords_invalid(self):
        parse_historydb_api_events_passwords('{')

    @raises(HistoryDBApiTemporaryError)
    def test_parse_historydb_api_events_passwords_error(self):
        parse_historydb_api_events_passwords('{"status": "error", "errors": ["internal"]}')

    def test_parse_auths_aggregated_runtime(self):
        eq_(
            parse_auths_aggregated_runtime(AUTHS_AGGREGATED_RUNTIME_TEST_RESPONSE),
            json.loads(AUTHS_AGGREGATED_RUNTIME_TEST_RESPONSE),
        )

    @raises(HistoryDBApiInvalidResponseError)
    def test_parse_auths_aggregated_runtime_invalid(self):
        parse_auths_aggregated_runtime('{')

    @raises(HistoryDBApiTemporaryError)
    def test_parse_auths_aggregated_runtime_error(self):
        parse_auths_aggregated_runtime('{"status": "error", "errors": ["internal"]}')

    def test_parse_auths_aggregated_old(self):
        eq_(
            parse_auths_aggregated(AUTHS_AGGREGATED_OLD_TEST_RESPONSE),
            (json.loads(AUTHS_AGGREGATED_OLD_TEST_RESPONSE)['auths'], NEXT_ROW_POINTER),
        )

    def test_parse_auths_aggregated(self):
        eq_(
            parse_auths_aggregated(AUTHS_AGGREGATED_TEST_RESPONSE),
            (json.loads(AUTHS_AGGREGATED_TEST_RESPONSE)['auths'], NEXT_ROW_POINTER),
        )

    @raises(HistoryDBApiInvalidResponseError)
    def test_parse_mail_history_invalid_no_status(self):
        parse_mail_history('{}')

    @raises(HistoryDBApiPermanentError)
    def test_parse_mail_history_responce_status_error(self):
        parse_mail_history(
            '{"status": "error", "errors": {"some_field": ["some_problem"]}}',
        )

    @raises(HistoryDBApiInvalidResponseError)
    def test_parse_last_letter_invalid_no_status(self):
        parse_last_letter('{}')

    @raises(HistoryDBApiPermanentError)
    def test_parse_last_letter_responce_status_error(self):
        parse_last_letter(
            '{"status": "error", "errors": {"some_field": ["some_problem"]}}',
        )

    @raises(HistoryDBApiInvalidResponseError)
    def test_parse_auths_aggregated_invalid(self):
        parse_auths_aggregated('{')

    @raises(HistoryDBApiTemporaryError)
    def test_parse_auths_aggregated_error(self):
        parse_auths_aggregated('{"status": "error", "errors": ["internal"]}')

    @raises(HistoryDBApiInvalidResponseError)
    def test_parse_push_history_invalid_no_status(self):
        parse_push_history('{}')

    @raises(HistoryDBApiPermanentError)
    def test_parse_push_history_responce_status_error(self):
        parse_push_history(
            '{"status": "error", "errors": {"some_field": ["some_problem"]}}',
        )
