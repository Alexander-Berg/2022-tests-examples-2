# -*- coding: utf-8 -*-
import json

import mock
from nose_parameterized import parameterized
from passport.backend.core.logbroker.tests.base.base import MessageClass1
from passport.backend.core.logbroker.tests.base.test_proto.test_proto_pb2 import TestMessage as ProtobufTestMessage
from passport.backend.core.logging_utils.request_id import RequestIdManager
from passport.backend.core.protobuf.logbroker_passport_protocol.logbroker_passport_protocol_pb2 import (
    PassportProtocolMessage,
)
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.logbroker_client.core.handlers.exceptions import ProtocolError
from passport.backend.logbroker_client.core.handlers.protobuf import BaseProtobufHandler
from passport.backend.utils.string import (
    smart_bytes,
    smart_text,
)
import yaml


TEST_DATA = b'data1'
TEST_DATA_MAGIC_RAISE = b'raise:DecodeError'
TEST_REQUEST_ID = 'abcdef9165кириллица'


TEST_DATA_FOR_TEST_RUN = {
    'nested_message': {
        'string_val': u'вложенная_строка',
        'int_val': 2,
        'bool_val': True,
    },
    'string_val': u'строка',
    'int_val': 3,
    'bool_val': True,
}
TEST_PROTOBUF_STRUCT = ProtobufTestMessage(
    nested_message=ProtobufTestMessage.TestNestedMessage(
        string_val=smart_bytes(u'вложенная_строка'),
        int_val=2,
        bool_val=True,
    ),
    string_val=smart_bytes(u'строка'),
    int_val=3,
    bool_val=True,
)


class FakeHandler(BaseProtobufHandler):
    def process_message(self, header, message):
        pass


class _BaseTestHandlerProtobuf(PassportTestCase):
    def setUp(self):
        RequestIdManager.clear_request_id()
        self._fake_process_message = mock.Mock()
        self._fake_metrics_logger = mock.Mock()

        self._fake_xunistater = mock.Mock()

        self._mock_time = mock.Mock(time=mock.Mock(
            side_effect=[0.5 * x for x in range(10)],
        ))
        self._time_patch = mock.patch('passport.backend.logbroker_client.core.handlers.protobuf.time', self._mock_time)
        self._time_patch.start()

    def tearDown(self):
        self._time_patch.stop()

    def get_handler(
        self,
        log_metrics=None,
        push_metrics_to_xunistater=None,
        push_execution_time_to_xunistater=False,
        push_unhandled_exception_to_xunistater=False,
        message_class='passport.backend.core.logbroker.tests.base.base.MessageClass1',
    ):
        handler = FakeHandler(
            config={},
            message_class=message_class,
            log_metrics=log_metrics,
            push_metrics_to_xunistater=push_metrics_to_xunistater,
            push_execution_time_to_xunistater=push_execution_time_to_xunistater,
            push_unhandled_exception_to_xunistater=push_unhandled_exception_to_xunistater,
            metrics_logger=self._fake_metrics_logger,
        )
        handler._xunistater = self._fake_xunistater
        handler.process_message = self._fake_process_message
        return handler

    def get_header(self, message_class='MessageClass1', legacy=False, protocol_v='1.0'):
        header = {
            'topic': 'topic1',
            'partition': 1,
            'offset': 2,
            'path': None,
            'server': 'server1',
            'ident': None,
            'logtype': None,
            'message_class': message_class,
            'extra_fields': {'key1': 'value1', 'message_class': message_class},
        }
        if not legacy:
            header['passport_protocol_v'] = protocol_v
        return header

    def get_passport_api_service_meta(self, request_id=TEST_REQUEST_ID):
        meta = PassportProtocolMessage.Header.PassportApiMeta()
        if request_id:
            meta.request_id_string = smart_bytes(request_id)
        return meta

    def get_proto_header(self, service_meta_attribute, service_meta_value):
        header = PassportProtocolMessage.Header(
            **{service_meta_attribute: service_meta_value}
        )
        return header

    def _pack_data(self, data, proto_header):
        return PassportProtocolMessage(
            message_payload=data,
            header=proto_header,
        ).SerializeToString()

    def process(self, handler, header, data=TEST_DATA, legacy=False, proto_header=None):
        if legacy:
            handler.process(header, data)
        else:
            if proto_header is None:
                proto_header = self.get_proto_header(
                    'passport_api', self.get_passport_api_service_meta(),
                )
            handler.process(header, self._pack_data(data, proto_header))

    def assert_process_call(self, header, data=TEST_DATA, cls=MessageClass1):
        self._fake_process_message.assert_called_once()
        args = self._fake_process_message.call_args_list[0][0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0], header)
        message = args[1]
        self.assertIsInstance(message, cls)
        message.ParseFromString.assert_called_once_with(data)

    def assert_metrics_logs(self, log_entries):
        self.assertEqual(
            self._fake_metrics_logger.log.call_args_list,
            list(mock.call(entry) for entry in log_entries),
        )

    def assert_metrics_xunistater(self, log_entries):
        if log_entries:
            self._fake_xunistater.push_metrics.assert_called_once_with(*log_entries)
        else:
            self.assertEqual(self._fake_xunistater.push_metrics.call_count, 0)

    def assert_logging_prefix(self, *args):
        self.assertEqual(
            RequestIdManager.get_request_id().lstrip('@'),
            u','.join(smart_text(arg) for arg in args),
        )


class TestHandlerProtobuf(_BaseTestHandlerProtobuf):
    def test_process_message__ok(self):
        handler = self.get_handler()
        header = self.get_header()
        self.process(handler, header)
        self.assert_process_call(header)
        self.assert_metrics_logs([])
        self.assert_metrics_xunistater([])
        self.assert_logging_prefix(smart_text(TEST_REQUEST_ID))

    def test_process_message__passport_meta_empty_values__ok(self):
        handler = self.get_handler()
        header = self.get_header()
        proto_header = self.get_proto_header(
            'passport_api', self.get_passport_api_service_meta(''),
        )
        self.process(handler, header, proto_header=proto_header)
        self.assert_process_call(header)
        self.assert_metrics_logs([])
        self.assert_metrics_xunistater([])
        self.assert_logging_prefix('-')

    def test_process_legacy_message__ok(self):
        handler = self.get_handler()
        header = self.get_header(legacy=True)
        self.process(handler, header, legacy=True)
        self.assert_process_call(header)
        self.assert_metrics_logs([])
        self.assert_metrics_xunistater([])

    def test_xunistater_metrics__ok(self):
        handler = self.get_handler(push_metrics_to_xunistater=True)
        header = self.get_header()
        self.process(handler, header)
        self.assert_process_call(header)
        self.assert_metrics_logs([])
        self.assert_metrics_xunistater(
            [
                {
                    'FakeHandler.entries.total.MessageClass1_dmmm': {'value': 1},
                    'FakeHandler.entries.server1.MessageClass1_dmmm': {'value': 1},
                },
            ],
        )

    def test_xunistater_execution_time__ok(self):
        handler = self.get_handler(push_execution_time_to_xunistater=True)
        header = self.get_header()
        self.process(handler, header)
        self.assert_process_call(header)
        self.assert_metrics_logs([])
        self.assert_metrics_xunistater(
            [
                {
                    'FakeHandler.execution_time.server1.MessageClass1_dmmm': {'value': 0.5},
                    'FakeHandler.execution_time.total.MessageClass1_dmmm': {'value': 0.5},
                },
            ],
        )

    def test_xunistater_metrics_with_execution_time__ok(self):
        handler = self.get_handler(push_metrics_to_xunistater=True, push_execution_time_to_xunistater=True)
        header = self.get_header()
        self.process(handler, header)
        self.assert_process_call(header)
        self.assert_metrics_logs([])
        self.assert_metrics_xunistater(
            [
                {
                    'FakeHandler.entries.total.MessageClass1_dmmm': {'value': 1},
                    'FakeHandler.entries.server1.MessageClass1_dmmm': {'value': 1},
                    'FakeHandler.execution_time.server1.MessageClass1_dmmm': {'value': 0.5},
                    'FakeHandler.execution_time.total.MessageClass1_dmmm': {'value': 0.5},
                },
            ],
        )

    def test_xunistater_metrics_with_unhandled_exception__ok(self):
        handler = self.get_handler(push_metrics_to_xunistater=True, push_unhandled_exception_to_xunistater=True)
        header = self.get_header()
        self._fake_process_message.side_effect = RuntimeError()
        with self.assertRaises(RuntimeError):
            self.process(handler, header)
        self.assert_process_call(header)
        self.assert_metrics_logs([])
        self.assert_metrics_xunistater(
            [
                {
                    'FakeHandler.entries.total.MessageClass1_dmmm': {'value': 1},
                    'FakeHandler.entries.server1.MessageClass1_dmmm': {'value': 1},
                    'FakeHandler.unhandled_exception.server1.MessageClass1_dmmm': {'value': 1},
                    'FakeHandler.unhandled_exception.total.MessageClass1_dmmm': {'value': 1},
                },
            ],
        )

    def test_metrics_logs__ok(self):
        handler = self.get_handler(log_metrics=True)
        header = self.get_header()
        self.process(handler, header)
        self.assert_process_call(header)
        self.assert_metrics_logs(
            [
                {
                    'metric:FakeHandler.entries.total.MessageClass1': 1,
                    'metric:FakeHandler.entries.server1.MessageClass1': 1,
                    'handler_name': 'FakeHandler',
                    'file': 'MessageClass1',
                    'server': 'server1',
                },
            ],
        )
        self.assert_metrics_xunistater([])

    def test_process_message__wrong_class__skip(self):
        handler = self.get_handler(push_metrics_to_xunistater=True, log_metrics=True)
        header = self.get_header(message_class='MessageClass2')
        self.process(handler, header, data=TEST_DATA_MAGIC_RAISE)
        self.assertEqual(self._fake_process_message.call_count, 0)
        self.assert_metrics_logs([])
        self.assert_metrics_xunistater([])

    def test_process_message__decode_error__exception(self):
        handler = self.get_handler(push_metrics_to_xunistater=True, log_metrics=True)
        header = self.get_header(message_class='MessageClass1')
        with self.assertRaisesRegexp(ProtocolError, 'Payload proto parse error: Error parsing message'):
            self.process(handler, header, data=TEST_DATA_MAGIC_RAISE)
        self.assertEqual(self._fake_process_message.call_count, 0)
        self.assert_metrics_logs([])
        self.assert_metrics_xunistater([])

    @parameterized.expand([
        ('wrong', 'Malformed passport protocol version'),
        ('1,2', 'Malformed passport protocol version'),
        ('.2.3', 'Malformed passport protocol version'),
        ('3.2.', 'Malformed passport protocol version'),
        ('3.2.', 'Malformed passport protocol version'),
        ('0.0', 'Unsupported protocol version'),
    ])
    def test_process_message__wrong_version__exception(self, version, error):
        handler = self.get_handler(push_metrics_to_xunistater=True, log_metrics=True)
        header = self.get_header(protocol_v=version)
        with self.assertRaisesRegexp(ProtocolError, error):
            self.process(handler, header, data=TEST_DATA_MAGIC_RAISE)
        self.assertEqual(self._fake_process_message.call_count, 0)
        self.assert_metrics_logs([])
        self.assert_metrics_xunistater([])

    def test_process_message__wrong_protocol_protobuf__exception(self):
        handler = self.get_handler(push_metrics_to_xunistater=True, log_metrics=True)
        header = self.get_header()
        with self.assertRaisesRegexp(ProtocolError, 'Passport proto parse error'):
            handler.process(header, TEST_DATA)
        self.assertEqual(self._fake_process_message.call_count, 0)
        self.assert_metrics_logs([])
        self.assert_metrics_xunistater([])


class TestHandlerProtobufTestMode(_BaseTestHandlerProtobuf):
    def get_handler(
        self,
        log_metrics=None,
        push_metrics_to_xunistater=None,
        push_execution_time_to_xunistater=False,
        push_unhandled_exception_to_xunistater=False,
        message_class='passport.backend.core.logbroker.tests.base.test_proto.test_proto_pb2.TestMessage',
    ):
        return super(TestHandlerProtobufTestMode, self).get_handler(
            log_metrics=log_metrics,
            push_metrics_to_xunistater=push_metrics_to_xunistater,
            push_execution_time_to_xunistater=push_execution_time_to_xunistater,
            push_unhandled_exception_to_xunistater=push_unhandled_exception_to_xunistater,
            message_class=message_class,
        )

    def get_header(self, message_class='TestMessage', legacy=True, protocol_v='1.0'):
        return super(TestHandlerProtobufTestMode, self).get_header(
            message_class=message_class,
            legacy=legacy,
            protocol_v=protocol_v,
        )

    def process_test_data(self, handler, header, data):
        handler.test_data(json.dumps(header) + '|||' + data)

    def assert_process_test_call(self, header, data):
        self._fake_process_message.assert_called_once_with(header, data)

    def test_process_test_data__json__ok(self):
        handler = self.get_handler()
        header = self.get_header()
        self.process_test_data(
            handler,
            header,
            'JSON ' + json.dumps(TEST_DATA_FOR_TEST_RUN),
        )
        self.assert_process_test_call(header, TEST_PROTOBUF_STRUCT)

    def test_process_test_data__default__ok(self):
        handler = self.get_handler()
        header = self.get_header()
        self.process_test_data(
            handler,
            header,
            json.dumps(TEST_DATA_FOR_TEST_RUN),
        )
        self.assert_process_test_call(header, TEST_PROTOBUF_STRUCT)

    def test_process_test_header__default__ok(self):
        handler = self.get_handler()
        self.process_test_data(
            handler,
            {},
            json.dumps(TEST_DATA_FOR_TEST_RUN),
        )
        self.assert_process_test_call({
            'topic': 'topic1',
            'partition': 1,
            'offset': 1,
            'path': None,
            'server': 'server1',
            'ident': 'ident1',
            'logtype': None,
            'message_class': 'TestMessage',
            'extra_fields': {'message_class': 'TestMessage'},
        }, TEST_PROTOBUF_STRUCT)

    def test_process_test_data__wrong_json__error(self):
        handler = self.get_handler()
        header = self.get_header()
        with self.assertRaisesRegexp(ValueError, 'Wrong test data format: invalid JSON'):
            self.process_test_data(
                handler,
                header,
                'JSON wrong_json',
            )

    def test_process_test_data__yaml__ok(self):
        handler = self.get_handler()
        header = self.get_header()
        self.process_test_data(
            handler,
            header,
            'YAML ' + yaml.dump(TEST_DATA_FOR_TEST_RUN),
        )
        self.assert_process_test_call(header, TEST_PROTOBUF_STRUCT)

    def test_process_test_data__wrong_yaml__error(self):
        handler = self.get_handler()
        header = self.get_header()
        with self.assertRaisesRegexp(ValueError, 'Wrong test data format: invalid YAML'):
            self.process_test_data(
                handler,
                header,
                'YAML wrong: inde\n\tation',
            )

    def test_process_test_data__wrong_structure__error(self):
        handler = self.get_handler()
        header = self.get_header()
        with self.assertRaisesRegexp(ValueError, 'Wrong test data format: cannot parse'):
            self.process_test_data(
                handler,
                header,
                'JSON {"wrong": "data"}',
            )
