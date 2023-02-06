# -*- coding: utf-8 -*-
import json

from passport.backend.core.builders.oauth import (
    OAuthAccountNotFoundError,
    OAuthPermanentError,
)
from passport.backend.core.builders.oauth.faker import FakeOAuth
from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)
from passport.backend.library.configurator import Configurator
from passport.backend.logbroker_client.core.tests.test_events.base import get_headers_event_file
from passport.backend.logbroker_client.revoke_oauth_tokens.handler import (
    RevokeOAuthTokensHandler,
    RevokeOAuthTokensHandlerException,
)
from passport.backend.utils.logging_mock import LoggingMock
import pytest


TEST_UID = 123456789
TEST_UNIXTIME = 1548688928
TEST_DEVICE_ID = 'test-device-id'
TEST_IP = '127.0.0.1'

TEST_NO_APPROPRIATE_EVENTS_DATA = '\t'.join([
    'tskv',
    'action=revoke_drive_device',
    'device_id=%s' % TEST_DEVICE_ID,
    'unixtime=%s' % TEST_UNIXTIME,
    'uid=%s' % TEST_UID,
    'ip=%s' % TEST_IP,
    '_is_external_event=1',
])
TEST_REVOKE_OAUTH_TOKEN_DATA = '\t'.join([
    'tskv',
    'action=revoke_drive_device',
    'device_id=%s' % TEST_DEVICE_ID,
    'unixtime=%s' % TEST_UNIXTIME,
    'uid=%s' % TEST_UID,
    'ip=%s' % TEST_IP,
])

TEST_OAUTH_OK_RESPONSE = json.dumps({'status': 'ok'})


TEST_HEADER = get_headers_event_file(mode='passport_statbox')


class TestRevokeOAuthTokensHandler(object):
    def setup_method(self, method):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'oauth',
                        'ticket': TEST_TICKET,
                    },
                }
            )
        )
        self.fake_oauth = FakeOAuth()

        self.patches = [
            self.fake_tvm_credentials_manager,
            self.fake_oauth,
        ]
        for patch in self.patches:
            patch.start()

        self.fake_oauth.set_response_value('revoke_device', TEST_OAUTH_OK_RESPONSE)

        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'revoke-oauth-tokens/base.yaml',
                'revoke-oauth-tokens/testing.yaml',
                'logging.yaml',
                'revoke-oauth-tokens/export.yaml',
            ]
        )
        self.config.set_as_passport_settings()
        self.handler = RevokeOAuthTokensHandler(self.config)

    def teardown_method(self, method):
        for patch in reversed(self.patches):
            patch.stop()

    def assert_oauth_called(self):
        assert len(self.fake_oauth.requests) == 1
        self.fake_oauth.requests[0].assert_properties_equal(
            method='POST',
            url='https://oauth-test-internal.yandex.ru/api/1/device/revoke',
            post_args=dict(
                uid=str(TEST_UID),
                device_id=TEST_DEVICE_ID,
                consumer='passport-lbc',
            ),
            headers={
                'Ya-Consumer-Client-Ip': TEST_IP,
            },
        )

    def assert_oauth_not_called(self):
        assert len(self.fake_oauth.requests) == 0

    def test_log_and_push_metrics(self):
        config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'revoke-oauth-tokens/base.yaml',
                'revoke-oauth-tokens/testing.yaml',
                'logging.yaml',
                'revoke-oauth-tokens/export.yaml',
            ]
        )
        config.set_as_passport_settings()
        handler = RevokeOAuthTokensHandler(
            config,
            log_metrics=True,
            push_metrics_to_xunistater=True,
        )

        with LoggingMock() as log:
            with FakeXunistater() as fake_xunistater:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                handler.process(TEST_HEADER, TEST_REVOKE_OAUTH_TOKEN_DATA)

        assert len(fake_xunistater.requests) == 1
        fake_xunistater.requests[0].assert_properties_equal(
            url='http://localhost:10300/xpush',
            method='POST',
            post_args=json.dumps(
                {
                    'revoke_oauth_tokens.entries._.var/log/yandex/passport-api/statbox/statbox.log_dmmm': {
                        'value': 1,
                    },
                    'revoke_oauth_tokens.entries.total.var/log/yandex/passport-api/statbox/statbox.log_dmmm': {
                        'value': 1,
                    },
                },
                sort_keys=True,
            ),
        )

        assert log.getLogger('logbroker_client.metrics').entries == [
            (
                {
                    'file': '/var/log/yandex/passport-api/statbox/statbox.log',
                    'handler_name': 'revoke_oauth_tokens',
                    'metric:revoke_oauth_tokens.entries._.var/log/yandex/passport-api/statbox/statbox.log': 1,
                    'metric:revoke_oauth_tokens.entries.total.var/log/yandex/passport-api/statbox/statbox.log': 1,
                    'server': '_',
                },
                'INFO',
                None,
                None,
            ),
        ]

    def test_no_events(self):
        self.handler.process(TEST_HEADER, TEST_NO_APPROPRIATE_EVENTS_DATA)
        self.assert_oauth_not_called()

    def test_oauth_error(self):
        self.fake_oauth.set_response_side_effect('revoke_device', OAuthPermanentError())
        with pytest.raises(RevokeOAuthTokensHandlerException):
            self.handler.process(TEST_HEADER, TEST_REVOKE_OAUTH_TOKEN_DATA)

    def test_account_not_found(self):
        self.fake_oauth.set_response_side_effect('revoke_device', OAuthAccountNotFoundError())
        self.handler.process(TEST_HEADER, TEST_REVOKE_OAUTH_TOKEN_DATA)
        self.assert_oauth_called()

    def test_ok(self):
        self.handler.process(TEST_HEADER, TEST_REVOKE_OAUTH_TOKEN_DATA)
        self.assert_oauth_called()
