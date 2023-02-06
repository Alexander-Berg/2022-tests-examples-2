# -*- coding: utf-8 -*-
from concurrent.futures import TimeoutError as FutureTimeoutError

from parameterized import parameterized
from passport.backend.core.logbroker.exceptions import (
    ConnectionLost,
    ProtocolError,
    TimeoutError,
    TransportError,
)
from passport.backend.core.logbroker.logbroker_sdk_client import LogbrokerProducer
from passport.backend.core.logbroker.test.constants import (
    TEST_CONNECT_TIMEOUT,
    TEST_CREDENTIALS_CONFIG_TVM,
    TEST_HOST1,
    TEST_META,
    TEST_PAYLOAD,
    TEST_PORT1,
    TEST_SEQ,
    TEST_SOURCE_ID,
    TEST_TOPIC1,
    TEST_WRITE_TIMEOUT,
)
from passport.backend.core.logbroker.tests.base.base import TestLogbrokerBase
from passport.backend.core.logging_utils.loggers import GraphiteLogger


class TestLogbrokerProducer(TestLogbrokerBase):
    def _get_client(self, connect=False, ca_cert=None):
        self._fake_producer.set_seq_no(TEST_SEQ)
        producer = LogbrokerProducer(
            host=TEST_HOST1,
            port=TEST_PORT1,
            topic=TEST_TOPIC1,
            source_id=TEST_SOURCE_ID,
            connect_timeout=TEST_CONNECT_TIMEOUT,
            write_timeout=TEST_WRITE_TIMEOUT,
            credentials_config=TEST_CREDENTIALS_CONFIG_TVM,
            extra_fields=TEST_META,
            graphite_logger=GraphiteLogger(service='logbroker'),
            ca_cert=ca_cert,
        )
        if connect:
            producer.start()
        return producer

    def _producer_restart_on_reconnect_assertion(self, client, restart):
        expected_create_producer_count = self._fake_api.create_producer.call_count
        expected_start_count = self._fake_producer.start.call_count
        expected_result_count = self._fake_producer.fake_start_future.result.call_count + 1
        if restart:
            expected_create_producer_count += 1
            expected_start_count += 1
        self._fake_api.fake_producer.set_start_result_ok()
        client.start()
        self.assertEqual(self._fake_api.create_producer.call_count, expected_create_producer_count)
        self.assertEqual(self._fake_producer.start.call_count, expected_start_count)
        self.assertEqual(self._fake_producer.fake_start_future.result.call_count, expected_result_count)

    def _assert_no_producer_restart_on_reconnect(self, client):
        self._producer_restart_on_reconnect_assertion(client, restart=False)

    def _assert_producer_restart_on_reconnect(self, client):
        self._producer_restart_on_reconnect_assertion(client, restart=True)

    def test_start_api_and_create_producer__ok(self):
        client = self._get_client()
        client.start_api()
        self.assertIs(client._api, self._fake_api)
        self.assertIsNone(client._producer)
        self.assertTrue(client.api_started)
        self.assertFalse(client.producer_started)

        client.start_producer()
        self.assertIs(client._producer, self._fake_api.fake_producer)
        self.assertTrue(client.producer_started)

    def test_connect__ok(self):
        client = self._get_client(ca_cert=b'abc')
        client.start()
        self.assertIs(client._api, self._fake_api)
        self.assertIs(client._producer, self._fake_api.fake_producer)
        self.assert_producer_create_params_ok(client, root_certificates=b'abc')

    def test_connect__api_start_timeout__exception(self):
        self._fake_api.fake_start_future.result.side_effect = FutureTimeoutError()
        client = self._get_client()
        with self.assertRaisesRegexp(TimeoutError, r'Timeout starting API'):
            client.start()

    def test_connect__producer_start_timeout__exception__no_consumer_restart(self):
        self._fake_api.fake_producer.set_start_side_effect(FutureTimeoutError())
        client = self._get_client()
        with self.assertRaisesRegexp(TimeoutError, r'Timeout starting producer'):
            client.start()

        self._assert_no_producer_restart_on_reconnect(client)

    @parameterized.expand([
        ('some reason', TransportError),
        ('access to topic aaa from cluster bbb denied for ccc@ddd due to \'access denied for consumer eee : no ReadTopic permission\'', ProtocolError),
        ('no topics found', ProtocolError),
    ])
    def test_connect__producer_start_error__exception__consumer_restart(self, descr_text, exc_class):
        self._fake_producer.set_start_result_failure(default_description_text=descr_text)
        client = self._get_client()
        with self.assertRaisesRegexp(exc_class, r'Error starting producer.+'):
            client.start()

        self._assert_producer_restart_on_reconnect(client)

    def test_connect__producer_start_failure__exception_format__ok(self):
        self._fake_producer.set_start_result_failure()
        client = self._get_client()
        with self.assertRaisesRegexp(
            TransportError,
            r'Error starting producer: reason=SessionDeathReason.FailedWithError '
            r'description=[^\n]+INITIALIZING[^\n]+description[^\n]+$',
        ):
            client.start()

        self._assert_producer_restart_on_reconnect(client)

    def test_connect__producer_start_failure__wrong_field_types__no_side_effect(self):
        self._fake_producer.set_start_result_failure(description=u'Абцд')
        client = self._get_client()
        with self.assertRaises(TransportError):
            client.start()

        self._assert_producer_restart_on_reconnect(client)

    def test_connect__producer_start_wrong_reply_type__exception(self):
        self._fake_producer.set_start_result_invalid_type(u'рез1')
        client = self._get_client()
        with self.assertRaisesRegexp(ProtocolError, r'Wrong producer start result type:.+рез1'):
            client.start()

        self._assert_producer_restart_on_reconnect(client)

    def test_connect__producer_start_wrong_reply_fields__exception(self):
        self._fake_producer.set_start_result_invalid('res1')
        client = self._get_client()
        with self.assertRaisesRegexp(ProtocolError, r'Wrong producer start result:.+res1'):
            client.start()

        self._assert_producer_restart_on_reconnect(client)

    def test_write__ok(self):
        producer = self._get_client(connect=True)
        producer.write(TEST_PAYLOAD)
        self._fake_producer.write.assert_called_once_with(TEST_SEQ + 1, TEST_PAYLOAD)
        self._fake_producer.assert_write_result_called_with(timeout=TEST_WRITE_TIMEOUT)
        self.assert_graphite_log_ok([dict(status='ok', response='success')])

    def test_write__timeout__exception(self):
        producer = self._get_client(connect=True)
        self._fake_producer.set_write_side_effect(FutureTimeoutError())
        with self.assertRaisesRegexp(TimeoutError, r'Timeout writing message'):
            producer.write(TEST_PAYLOAD)
        self.assert_graphite_log_ok([dict(status='TimeoutError', response='timeout')])

    def test_write__wrong_reply__exception(self):
        producer = self._get_client(connect=True)
        self._fake_producer.set_write_result_invalid('res1')
        with self.assertRaisesRegexp(TransportError, r'Send error.+res1'):
            producer.write(TEST_PAYLOAD)
        self.assert_graphite_log_ok([dict(status='TransportError', response='failed')])

    def test_write__wrong_reply_type__exception(self):
        producer = self._get_client(connect=True)
        self._fake_producer.set_write_result_invalid_type(u'рез1')
        with self.assertRaisesRegexp(ProtocolError, r'Wrong write result type.+рез1.+(str|unicode)'):
            producer.write(TEST_PAYLOAD)
        self.assert_graphite_log_ok([dict(status='ProtocolError', response='failed')])

    def test_write__connection_lost__exception(self):
        producer = self._get_client(connect=True)
        self._fake_producer.set_connection_lost()
        self.assertTrue(producer.producer_started)
        with self.assertRaisesRegexp(ConnectionLost, r'Producer stopped: test_error'):
            producer.write(TEST_PAYLOAD)
        self.assert_graphite_log_ok([dict(status='ConnectionLost', response='failed')])
        self.assertFalse(producer.producer_started)

        self._assert_producer_restart_on_reconnect(producer)
