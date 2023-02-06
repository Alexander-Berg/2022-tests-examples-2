# -*- coding: utf-8 -*-
import json
import unittest

from nose_parameterized import parameterized
from passport.backend.core.builders.social_broker.faker.social_broker import (
    bind_phonish_account_by_track_v2_ok_response,
    FakeSocialBroker,
    social_broker_v2_error_response,
)
from passport.backend.core.builders.taxi_zalogin.exceptions import (
    TaxiZaloginAuthEror,
    TaxiZaloginPermanentZaloginError,
    TaxiZaloginTemporaryZaloginError,
)
from passport.backend.core.builders.taxi_zalogin.faker import (
    FakeTaxiZalogin,
    taxi_zalogin_ok_response,
)
from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.core.test.consts import (
    TEST_TRACK_ID1,
    TEST_USER_IP1,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)
from passport.backend.library.configurator import Configurator
from passport.backend.logbroker_client.core.tests.test_events.base import get_headers_event_file
from passport.backend.logbroker_client.social_bindings.handler import (
    SocialBindingsHandler,
    SocialBindingsHandlerException,
)
from passport.backend.utils.logging_mock import LoggingMock
import pytest


TEST_UID = 123456789
TEST_UID2 = 1020304050
TEST_UNIXTIME = 1548688928
TEST_NEOPHONISH_UID = TEST_UID
TEST_PHONISH_UID = TEST_UID2


TEST_HEADER = get_headers_event_file(mode='social-bindings')
NO_APPROPRIATE_EVENTS_DATA = 'tskv\tmode=hack_password\tstatus=error\n'

BINDING_EVENT_DATA = '\t'.join([
    'tskv',
    'action=binding_created',
    'master_uid={}'.format(TEST_UID),
    'slave_userid={}'.format(TEST_UID2),
    'provider_code=ya',
    'unixtime={}'.format(TEST_UNIXTIME),
])

UNBINDING_EVENT_DATA = '\t'.join([
    'tskv',
    'action=bindings_deleted',
    'master_uid={}'.format(TEST_UID),
    'slave_provider_userids={}'.format(json.dumps([['ya', TEST_UID2]])),
    'unixtime={}'.format(TEST_UNIXTIME),
])

UNKNOWN_EVENT_DATA = '\t'.join([
    'tskv',
    'action=¯\\_(ツ)_/¯',
])

BIND_PHONISH_ACCOUNT_BY_TRACK_EVENT_DATA = '\t'.join([
    'tskv',
    'action=bind_phonish_account_by_track',
    'ip=' + TEST_USER_IP1,
    'track_id=' + TEST_TRACK_ID1,
    'uid=' + str(TEST_UID),
    'unixtime=' + str(TEST_UNIXTIME),
])


class TestTaxiZaloginHandler(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'taxi_zalogin',
                        'ticket': TEST_TICKET,
                    },
                }
            )
        )

        self.fake_taxi_zalogin = FakeTaxiZalogin()
        self.fake_taxi_zalogin.set_response_value('uid_notify', taxi_zalogin_ok_response())

        self.patches = [
            self.fake_taxi_zalogin,
            self.fake_tvm_credentials_manager,
        ]
        for patch in self.patches:
            patch.start()

        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'social_bindings/base.yaml',
                'social_bindings/testing.yaml',
                'logging.yaml',
                'social_bindings/export.yaml',
            ],
        )
        self.config.set_as_passport_settings()
        self.handler = SocialBindingsHandler(self.config)

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()

    def assert_taxi_zalogin_called(self, event_type='bind', index=-1):
        self.fake_taxi_zalogin.requests[index].assert_properties_equal(
            method='POST',
            url='http://zalogin.taxi.tst.yandex.net/v1/uid-notify?portal_uid={}&phonish_uid={}&event_type={}'.format(
                TEST_UID,
                TEST_UID2,
                event_type,
            ),
        )

    def assert_taxi_zalogin_not_called(self):
        assert self.fake_taxi_zalogin.requests == []

    def test_log_and_push_metrics(self):
        handler = SocialBindingsHandler(
            self.config,
            log_metrics=True,
            push_metrics_to_xunistater=True,
        )

        with LoggingMock() as log:
            with FakeXunistater() as fake_xunistater:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                handler.process(TEST_HEADER, BINDING_EVENT_DATA)

        assert len(fake_xunistater.requests) == 1
        fake_xunistater.requests[0].assert_properties_equal(
            url='http://localhost:10297/xpush',
            method='POST',
            post_args=json.dumps(
                {
                    'social_bindings.entries._.var/log/yandex/socialism/social-bindings.statbox.log_dmmm': {
                        'value': 1,
                    },
                    'social_bindings.entries.total.var/log/yandex/socialism/social-bindings.statbox.log_dmmm': {
                        'value': 1,
                    },
                },
                sort_keys=True,
            ),
        )

        assert log.getLogger('logbroker_client.metrics').entries == [
            (
                {
                    'file': '/var/log/yandex/socialism/social-bindings.statbox.log',
                    'handler_name': 'social_bindings',
                    'metric:social_bindings.entries._.var/log/yandex/socialism/social-bindings.statbox.log': 1,
                    'metric:social_bindings.entries.total.var/log/yandex/socialism/social-bindings.statbox.log': 1,
                    'server': '_',
                },
                'INFO',
                None,
                None,
            ),
        ]

    def test_binding_ok(self):
        self.handler.process(TEST_HEADER, BINDING_EVENT_DATA)
        self.assert_taxi_zalogin_called('bind')

    def test_unbinding_ok(self):
        self.handler.process(TEST_HEADER, UNBINDING_EVENT_DATA)
        self.assert_taxi_zalogin_called('unbind')

    def test_no_events(self):
        self.handler.process(TEST_HEADER, UNKNOWN_EVENT_DATA)
        self.assert_taxi_zalogin_not_called()

    @parameterized.expand([
        (TaxiZaloginTemporaryZaloginError,),
        (TaxiZaloginPermanentZaloginError,),
        (TaxiZaloginAuthEror,),
    ])
    def test_client_error(self, exception):
        self.fake_taxi_zalogin.set_response_side_effect('uid_notify', exception())
        with pytest.raises(SocialBindingsHandlerException):
            self.handler.process(TEST_HEADER, BINDING_EVENT_DATA)


class TestBindPhonishAccountByTrackHandler(unittest.TestCase):
    def setUp(self):
        super(TestBindPhonishAccountByTrackHandler, self).setUp()

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'social_broker',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )

        self.fake_social_broker = FakeSocialBroker()
        self.fake_social_broker.set_response_side_effect(
            'bind_phonish_account_by_track_v2',
            [
                bind_phonish_account_by_track_v2_ok_response(
                    uid=TEST_NEOPHONISH_UID,
                    phonish_uid=TEST_PHONISH_UID,
                ),
            ],
        )

        self.patches = [
            self.fake_social_broker,
            self.fake_tvm_credentials_manager,
        ]
        for patch in self.patches:
            patch.start()

        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'social_bindings/base.yaml',
                'social_bindings/testing.yaml',
                'logging.yaml',
                'social_bindings/export.yaml',
            ]
        )
        self.config.set_as_passport_settings()
        self.handler = SocialBindingsHandler(self.config)

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()

        super(TestBindPhonishAccountByTrackHandler, self).tearDown()

    def assert_social_bind_phonish_account_by_track_ok_request(self, request):
        request.assert_properties_equal(
            method='POST',
            url='https://api.social-test.yandex.ru/brokerapi/bind_phonish_account_by_track_v2?consumer=logbroker-client',
            post_args=dict(
                uid=str(TEST_UID),
                track_id=TEST_TRACK_ID1,
            ),
            headers={
                'Ya-Consumer-Client-Ip': str(TEST_USER_IP1),
                'X-Ya-Service-Ticket': TEST_TICKET,
            },
        )

    def test_ok(self):
        self.handler.process(TEST_HEADER, BIND_PHONISH_ACCOUNT_BY_TRACK_EVENT_DATA)

        assert len(self.fake_social_broker.requests) == 1
        self.assert_social_bind_phonish_account_by_track_ok_request(self.fake_social_broker.requests[0])

    def test_binding_exists(self):
        self.fake_social_broker.set_response_side_effect(
            'bind_phonish_account_by_track_v2',
            [
                bind_phonish_account_by_track_v2_ok_response(
                    uid=TEST_NEOPHONISH_UID,
                    old=True,
                    phonish_uid=TEST_PHONISH_UID,
                ),
            ],
        )

        self.handler.process(TEST_HEADER, BIND_PHONISH_ACCOUNT_BY_TRACK_EVENT_DATA)

        assert len(self.fake_social_broker.requests) == 1

    def test_profile_not_allowed(self):
        self.fake_social_broker.set_response_side_effect(
            'bind_phonish_account_by_track_v2',
            [
                social_broker_v2_error_response('profile.not_allowed'),
            ],
        )

        self.handler.process(TEST_HEADER, BIND_PHONISH_ACCOUNT_BY_TRACK_EVENT_DATA)

        assert len(self.fake_social_broker.requests) == 1

    def test_social_broker_internal_error(self):
        self.fake_social_broker.set_response_value(
            'bind_phonish_account_by_track_v2',
            social_broker_v2_error_response('internal_error'),
        )

        with self.assertRaises(SocialBindingsHandlerException) as assertion:
            self.handler.process(TEST_HEADER, BIND_PHONISH_ACCOUNT_BY_TRACK_EVENT_DATA)

        assert str(assertion.exception) == 'Social broker failed: internal_error'

    def test_social_broker_exception_unhandled(self):
        self.fake_social_broker.set_response_value(
            'bind_phonish_account_by_track_v2',
            social_broker_v2_error_response('exception.unhandled'),
        )

        with self.assertRaises(SocialBindingsHandlerException) as assertion:
            self.handler.process(TEST_HEADER, BIND_PHONISH_ACCOUNT_BY_TRACK_EVENT_DATA)

        assert str(assertion.exception) == 'Social broker failed: exception.unhandled'

    def test_social_broker_unknown_error(self):
        self.fake_social_broker.set_response_value(
            'bind_phonish_account_by_track_v2',
            social_broker_v2_error_response('unknown_error'),
        )

        with self.assertRaises(SocialBindingsHandlerException) as assertion:
            self.handler.process(TEST_HEADER, BIND_PHONISH_ACCOUNT_BY_TRACK_EVENT_DATA)

        assert str(assertion.exception) == 'Social broker failed: unknown_error'
