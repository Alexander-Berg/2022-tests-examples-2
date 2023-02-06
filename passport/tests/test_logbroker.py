# -*- coding: utf-8 -*-
import mock
from passport.backend.core.logbroker.exceptions import (
    BaseLogbrokerError,
    ConnectionLost,
)
from passport.backend.core.logbroker.logbroker import (
    get_logbroker_writer,
    LogbrokerWriterProto,
)
from passport.backend.core.logbroker.test.constants import (
    TEST_HOST1,
    TEST_NAME1,
    TEST_NAME2,
    TEST_PAYLOAD_UNICODE,
    TEST_PAYLOAD_UNICODE_ENCODED,
)
from passport.backend.core.logbroker.tests.base.base import BaseTestCases


class TestLogbrokerWriterProto(BaseTestCases.LogbrokerWriterClassTestBase):
    writer_class = LogbrokerWriterProto

    def get_logbroker_writer(self, name, **kwargs):
        return get_logbroker_writer(name, **kwargs)

    def test_get_logbroker_writer__producer_start_exception__ok(self):
        self._fake_producer.set_start_result_failure()
        writer = self.get_logbroker_writer(TEST_NAME1)
        with self.assertRaises(BaseLogbrokerError):
            writer.warm_up()

    def test_override_host_and_partition__ok(self):
        writer1 = self.get_logbroker_writer(TEST_NAME1)
        self.assertIsInstance(writer1, self.writer_class)
        self.assertEqual(writer1._producer.host, TEST_HOST1)
        self.assertIsNone(writer1._producer._partition_group)

        writer2 = self.get_logbroker_writer(TEST_NAME2, override_host='test.host2', partition_group=3)
        self.assertIsInstance(writer2, self.writer_class)
        self.assertIsNot(writer2, writer1)
        self.assertEqual(writer2._producer.host, 'test.host2')
        self.assertEqual(writer2._producer._partition_group, 3)
        self.assertEqual(writer2._producer._configurator.partition_group, 3)

    def test_send__ok(self):
        writer = self.get_logbroker_writer(TEST_NAME1)
        self.send_writer1(writer)
        self.assert_producer_start_status(writer._producer, started=True)
        self.assert_sent(writer)
        self.assert_graphite_log_ok([dict(status='ok', response='success')])

    def test_warm_up_and_send__ok(self):
        writer = self.get_logbroker_writer(TEST_NAME1)
        writer.warm_up()
        self.assert_producer_start_status(writer._producer, started=True)

        self.send_writer1(writer)
        self.assert_producer_start_status(writer._producer, started=True)
        self.assert_sent(writer)
        self.assert_graphite_log_ok([dict(status='ok', response='success')])

    def test_send_unicode__ok(self):
        writer = self.get_logbroker_writer(TEST_NAME1)
        self.send_writer1(writer, TEST_PAYLOAD_UNICODE)
        self.assert_producer_start_status(writer._producer, started=True)
        self.assert_sent(writer, data=TEST_PAYLOAD_UNICODE_ENCODED)
        self.assert_graphite_log_ok([dict(status='ok', response='success')])

    def test_send__wrong_class__exception(self):
        writer = self.get_logbroker_writer(TEST_NAME2)
        with self.assertRaisesRegexp(
            ValueError,
            r'must be an instance of MessageClass2',
        ):
            self.send_writer1(writer)
        self.assert_producer_start_status(writer._producer, started=True)
        self.assert_graphite_log_ok([])

    def test_send__connection_lost__exception(self):
        writer = self.get_logbroker_writer(TEST_NAME1)
        writer.warm_up()
        writer._producer._producer.set_connection_lost()
        with self.assertRaisesRegexp(ConnectionLost, 'Producer stopped: test_error'):
            self.send_writer1(writer)

        self._fake_producer.start.assert_called_once_with()
        self._fake_producer.write.assert_not_called()
        self.assert_graphite_log_ok([dict(status='ConnectionLost', response='failed')])

    def test_send__producer_became_stopped__restart(self):
        writer = self.get_logbroker_writer(TEST_NAME1)
        writer.warm_up()
        writer._producer.producer_started = False
        self.assertEqual(writer._producer._producer.start.call_count, 1)
        self.send_writer1(writer)

        self.assertEqual(writer._producer._producer.start.call_count, 2)
        writer._producer._producer.start.assert_has_calls([mock.call(), mock.call()])
        self.assert_sent(writer)
        self.assert_graphite_log_ok([dict(status='ok', response='success')])
