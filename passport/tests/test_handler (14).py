# -*- coding: utf-8 -*-
import json
from uuid import UUID

import mock
from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.library.configurator import Configurator
from passport.backend.logbroker_client.ufo.handler import UfoHandler
from passport.backend.utils.logging_mock import LoggingMock


HEADER_WITH_AUTH_CHALLENGE_FILE = {
    'sourceid': 'base64:tTOfUD6sTFy9l4a_mIq8WQ',
    'seqno': '509549082',
    'topic': 'rt3.iva--historydb--raw',
    'path': '/var/log/yandex/passport-api/historydb/auth_challenge.log',
    'server': 'pass-dd-i84.sezam.yandex.net',
    'partition': '7',
    'offset': '535729'
}

AUTH_CHALLENGE_DATA = (
    '1 2017-03-29T16:28:08.505471+03 updated 482306368 8c4a1084-1483-11e7-8660-8b8fd17329e3 - '
    '`{"ip": "78.25.122.90", "yandexuid": "7796750191461246057", "user_agent_info": '
    '{"BrowserVersion": "36.0.2130.80", "BrowserEngine": "WebKit", "BrowserBase": "Chromium", '
    '"BrowserBaseVersion": "49.0.2623.112", "isBrowser": true, "OSFamily": "Windows", "OSName": "Windows XP", '
    '"BrowserName": "Opera", "BrowserEngineVersion": "537.36", "OSVersion": "5.1"}}`\n'
    '2 2017-03-29T16:28:10.186636+03 updated 381808016 8d4b0844-1483-11e7-9135-8138b6fc29f5 - '
    '`{"ip": "2606:f180:2:301:301:d1e4:94f3:5eb", "yandexuid": "6114628491489667104", '
    '"user_agent_info": {"BrowserVersion": "56.0.2924", "BrowserEngine": "WebKit", "BrowserBase": "Chromium", '
    '"BrowserBaseVersion": "56.0.2924.87", "isBrowser": true, "OSFamily": "Windows", "OSName": "Windows 7", '
    '"BrowserName": "Chrome", "BrowserEngineVersion": "537.36", "OSVersion": "6.1"}}` -\n'
)

AUTH_CHALLENGE_RC_DATA = (
    '1 2017-03-29T16:28:08.505471+03 updated 482306368 8c4a1084-1483-11e7-8660-8b8fd17329e3 - '
    '`{"ip": "78.25.122.90", "yandexuid": "7796750191461246057", "user_agent_info": '
    '{"BrowserVersion": "36.0.2130.80", "BrowserEngine": "WebKit", "BrowserBase": "Chromium", '
    '"BrowserBaseVersion": "49.0.2623.112", "isBrowser": true, "OSFamily": "Windows", '
    '"OSName": "Windows XP", "BrowserName": "Opera", "BrowserEngineVersion": "537.36", "OSVersion": "5.1"}}`\n'
    '2 2017-03-29T16:28:10.186636+03 updated 381808016 8d4b0844-1483-11e7-9135-8138b6fc29f5 - '
    '`{"ip": "2606:f180:2:301:301:d1e4:94f3:5eb", "yandexuid": "6114628491489667104", "user_agent_info": '
    '{"BrowserVersion": "56.0.2924", "BrowserEngine": "WebKit", "BrowserBase": "Chromium", '
    '"BrowserBaseVersion": "56.0.2924.87", "isBrowser": true, "OSFamily": "Windows", "OSName": "Windows 7",'
    ' "BrowserName": "Chrome", "BrowserEngineVersion": "537.36", "OSVersion": "6.1"}}` env=rc\n'
)


class TestUfoHandler(object):

    def setup_method(self, method):
        self.cluster_mock = mock.Mock()
        self.cluster_patch = mock.patch(
            'passport.backend.logbroker_client.ufo.handler.UfoHandler._get_cassandra', self.cluster_mock,
        )
        self.cluster_patch.start()
        self.fake_ydb = FakeYdb()
        self.fake_ydb.start()

        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'ufo/base.yaml',
                'ufo/secrets.yaml',
                'ufo/testing.yaml',
                'logging.yaml',
                'ufo/export.yaml',
            ]
        )

        self.ufo_handler = UfoHandler(
            config=self.config,
            contact_points=['fake-storage-1', 'fake-storage-2'],
            consistency_level_name='ONE',
        )

    def teardown_method(self, method):
        self.cluster_patch.stop()
        self.fake_ydb.stop()
        del self.cluster_patch
        del self.fake_ydb

    def test_log_and_push_metrics(self):
        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'ufo/base.yaml',
                'ufo/secrets.yaml',
                'ufo/testing.yaml',
                'logging.yaml',
                'ufo/export.yaml',
            ]
        )
        self.config.set_as_passport_settings()

        self.ufo_handler = UfoHandler(
            config=self.config,
            contact_points=['fake-storage-1', 'fake-storage-2'],
            consistency_level_name='ONE',
            log_metrics=True,
            push_metrics_to_xunistater=True,
        )

        with LoggingMock() as log:
            with FakeXunistater() as fake_xunistater:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                with mock.patch('passport.backend.logbroker_client.ufo.handler.UfoHandler.get_unique_id', return_value=2000000):
                    with mock.patch('passport.backend.logbroker_client.ufo.handler.UfoHandler.get_timestamp', return_value=3000000):
                        self.ufo_handler.process(HEADER_WITH_AUTH_CHALLENGE_FILE, AUTH_CHALLENGE_DATA)

        assert len(fake_xunistater.requests) == 1
        fake_xunistater.requests[0].assert_properties_equal(
            url='http://localhost:10295/xpush',
            method='POST',
            post_args=json.dumps(
                {
                    "ufo.entries.pass-dd-i84.sezam.yandex.net.var/log/yandex/passport-api/historydb/auth_challenge.log_dmmm": {
                        "value": 2,
                    },
                    "ufo.entries.total.var/log/yandex/passport-api/historydb/auth_challenge.log_dmmm": {
                        "value": 2,
                    },
                },
                sort_keys=True,
            ),
        )

        assert log.getLogger('logbroker_client.metrics').entries == [
            ({'file': '/var/log/yandex/passport-api/historydb/auth_challenge.log',
              'handler_name': 'ufo',
              u'metric:ufo.entries.pass-dd-i84.sezam.yandex.net.var/log/yandex/passport-api/historydb/auth_challenge.log': 2,
              u'metric:ufo.entries.total.var/log/yandex/passport-api/historydb/auth_challenge.log': 2,
              'server': 'pass-dd-i84.sezam.yandex.net'},
             'INFO',
             None,
             None),
        ]

    def test_profile_ok(self):
        with mock.patch('passport.backend.logbroker_client.ufo.handler.UfoHandler.get_unique_id', return_value=2000000):
            self.ufo_handler.process(HEADER_WITH_AUTH_CHALLENGE_FILE, AUTH_CHALLENGE_DATA)

        assert self.ufo_handler.profile_session.execute.call_count == 2
        self.ufo_handler.profile_session.execute.assert_called_with(
            self.ufo_handler.prepared_insert_auth_env_query,
            (
                381808016,
                UUID('8d4b0844-1483-11e7-9135-8138b6fc29f5'),
                '{"ip": "2606:f180:2:301:301:d1e4:94f3:5eb", "yandexuid": "6114628491489667104", '
                '"user_agent_info": {"BrowserVersion": "56.0.2924", "BrowserEngine": "WebKit", '
                '"BrowserBase": "Chromium", "BrowserBaseVersion": "56.0.2924.87", "isBrowser": true, '
                '"OSFamily": "Windows", "OSName": "Windows 7", "BrowserName": "Chrome", "BrowserEngineVersion": '
                '"537.36", "OSVersion": "6.1"}}',
            ),
        )
        assert (
            self.fake_ydb.executed_queries() ==
            [{
                'query': (
                    'declare $inverted_event_timestamp as Uint64;\n'
                    'declare $uid as Uint64;\n'
                    'declare $unique_id as Uint64;\n'
                    'declare $updated_at as Uint64;\n'
                    'declare $value as Json;\n'
                    'upsert into [profile-testing]'
                    ' (inverted_event_timestamp, uid, unique_id, updated_at, value)\n'
                    'values ($inverted_event_timestamp, $uid, $unique_id, $updated_at, $value);\n'
                ),
                'parameters': {
                    '$updated_at': 1490794088000000,
                    '$uid': 482306368,
                    '$unique_id': 2000000,
                    '$inverted_event_timestamp': 18445253279621551615L,
                    '$value': '{"ip": "78.25.122.90", "yandexuid": "7796750191461246057", '
                              '"user_agent_info": {"BrowserVersion": "36.0.2130.80", "BrowserEngine": '
                              '"WebKit", "BrowserBase": "Chromium", "BrowserBaseVersion": "49.0.2623.112",'
                              ' "isBrowser": true, "OSFamily": "Windows", "OSName": "Windows XP",'
                              ' "BrowserName": "Opera", "BrowserEngineVersion": "537.36", '
                              '"OSVersion": "5.1"}, "timestamp": 1490794088}'
                },
                'commit_tx': True,
            }, {
                'query': (
                    'declare $inverted_event_timestamp as Uint64;\n'
                    'declare $uid as Uint64;\n'
                    'declare $unique_id as Uint64;\n'
                    'declare $updated_at as Uint64;\n'
                    'declare $value as Json;\n'
                    'upsert into [profile-testing] '
                    '(inverted_event_timestamp, uid, unique_id, updated_at, value)\n'
                    'values ($inverted_event_timestamp, $uid, $unique_id, $updated_at, $value);\n'
                ),
                'parameters': {
                    '$updated_at': 1490794090000000,
                    '$uid': 381808016,
                    '$unique_id': 2000000,
                    '$inverted_event_timestamp': 18445253279619551615L,
                    '$value': '{"ip": "2606:f180:2:301:301:d1e4:94f3:5eb", "yandexuid": "6114628491489667104",'
                              ' "user_agent_info": {"BrowserVersion": "56.0.2924", "BrowserEngine": "WebKit",'
                              ' "BrowserBase": "Chromium", "BrowserBaseVersion": "56.0.2924.87", '
                              '"isBrowser": true, "OSFamily": "Windows", "OSName": "Windows 7", '
                              '"BrowserName": "Chrome", "BrowserEngineVersion": "537.36", "OSVersion": '
                              '"6.1"}, "timestamp": 1490794090}'
                },
                'commit_tx': True,
            }]
        )

    def test_profile_to_rc_ok(self):
        self.ufo_handler.process(HEADER_WITH_AUTH_CHALLENGE_FILE, AUTH_CHALLENGE_RC_DATA)
        assert self.ufo_handler.profile_session.execute.call_count == 2
        expected_calls = [
            mock.call(
                self.ufo_handler.prepared_insert_auth_env_query,
                (
                    482306368,
                    UUID('8c4a1084-1483-11e7-8660-8b8fd17329e3'),
                    '{"ip": "78.25.122.90", "yandexuid": "7796750191461246057", "user_agent_info": '
                    '{"BrowserVersion": "36.0.2130.80", "BrowserEngine": "WebKit", "BrowserBase": "Chromium", '
                    '"BrowserBaseVersion": "49.0.2623.112", "isBrowser": true, "OSFamily": "Windows", "OSName": '
                    '"Windows XP", "BrowserName": "Opera", "BrowserEngineVersion": "537.36", "OSVersion": "5.1"}}',
                ),
            ),
            mock.call(
                self.ufo_handler.prepared_insert_auth_env_rc_query,
                (
                    381808016,
                    UUID('8d4b0844-1483-11e7-9135-8138b6fc29f5'),
                    '{"ip": "2606:f180:2:301:301:d1e4:94f3:5eb", "yandexuid": "6114628491489667104", '
                    '"user_agent_info": {"BrowserVersion": "56.0.2924", "BrowserEngine": "WebKit", '
                    '"BrowserBase": "Chromium", "BrowserBaseVersion": "56.0.2924.87", "isBrowser": true, '
                    '"OSFamily": "Windows", "OSName": "Windows 7", "BrowserName": "Chrome", "BrowserEngineVersion": '
                    '"537.36", "OSVersion": "6.1"}}',
                ),
            ),
        ]
        self.ufo_handler.profile_session.execute.assert_has_calls(expected_calls)
