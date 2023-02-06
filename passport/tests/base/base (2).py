# -*- coding: utf-8 -*-
from socket import gethostname

from google.protobuf.message import DecodeError
from kikimr.public.sdk.python.persqueue import grpc_pq_streaming_api
from kikimr.public.sdk.python.persqueue.errors import (
    SessionDeathReason,
    SessionFailureResult,
)
from kikimr.public.sdk.python.persqueue.grpc_pq_streaming_api import ProducerConfigurator
from kikimr.yndx.api.protos.persqueue_pb2 import WriteResponse
import mock
from passport.backend.core.logbroker.logbroker import NamedSingletonMeta
from passport.backend.core.logbroker.logbroker_base import TvmManagerCredentialsProvider
from passport.backend.core.logbroker.test.constants import (
    TEST_CONNECT_TIMEOUT,
    TEST_CREDENTIALS_CONFIG_TVM,
    TEST_HOST1,
    TEST_HOST2,
    TEST_META,
    TEST_NAME1,
    TEST_NAME2,
    TEST_PAYLOAD,
    TEST_PAYLOAD_ENCODED,
    TEST_PORT1,
    TEST_PORT2,
    TEST_SEQ,
    TEST_SOURCE_ID,
    TEST_SOURCE_ID_PREFIX,
    TEST_STR_VERSION,
    TEST_TOPIC1,
    TEST_TOPIC2,
    TEST_TVM_ALIAS,
    TEST_UUID,
    TEST_VERSION,
    TEST_WRITE_TIMEOUT,
)
from passport.backend.core.logging_utils.faker.fake_tskv_logger import GraphiteLoggerFaker
from passport.backend.core.protobuf.logbroker_passport_protocol.logbroker_passport_protocol_pb2 import (
    PassportProtocolMessage,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    smart_bytes,
    with_settings_hosts,
)
from passport.backend.core.tvm import TvmCredentialsManager
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
import six
from ydb.public.api.protos.draft.persqueue_common_pb2 import Error as PersqueueError


class ProtobufFaker(mock.Mock):
    def __init__(self, data=None, fields=None, *args, **kwargs):
        fields = fields or {}
        kwargs.update(fields)
        name = kwargs.get('name', 'protobuf_faker')

        def parse_from_string(in_data):
            if in_data == b'raise:DecodeError':
                raise DecodeError('Error parsing message')
            else:
                return 'decoded:{}'.format(in_data)

        super(ProtobufFaker, self).__init__(
            ParseFromString=mock.Mock(
                name='{}.ParseFromString'.format(name),
                side_effect=parse_from_string,
            ),
            SerializeToString=mock.Mock(
                name='{}.SerializeToString'.format(name),
                return_value=smart_bytes(u'str:{}'.format(data)),
            ),
            _fields=fields,
            _data=data,
            *args, **kwargs
        )

    def HasField(self, field):
        return field in self._fields

    def __str__(self):
        return '{} data={} fields={}'.format(
            super(ProtobufFaker, self).__str__(), self._data, self._fields,
        )

    def __unicode__(self):
        return u'{} data={} fields={}'.format(
            super(ProtobufFaker, self).__str__(), self._data, self._fields,
        )


class FakeFuture(mock.Mock):
    def __init__(self, name=None, result_value=None, result_side_effect=None, done=True):
        super(FakeFuture, self).__init__(
            name=name,
            result=mock.Mock(
                name='{}.result'.format(name),
                side_effect=result_side_effect,
                return_value=result_value,
            ),
            done=mock.Mock(
                name='{}.done'.format(name),
                side_effect=lambda: self._done
            )
        )
        self._done = done

    def set_result_value(self, value):
        self.result.return_value = value

    def set_result_side_effect(self, side_effect):
        self.result.side_effect = side_effect

    def set_done(self, done):
        self._done = done


class PqProducerFaker(mock.Mock):
    def __init__(self):
        start_result_ok = self.get_start_result_ok()
        write_result_ok = WriteResponse(
            ack=WriteResponse.Ack(
                seq_no=0,
            ),
        )
        fake_start_future = FakeFuture(
            name='pq_producer.start()->future',
            result_value=start_result_ok,
        )
        fake_write_future = FakeFuture(
            name='pq_producer.write()->future',
            result_value=write_result_ok,
        )
        fake_stop_future = FakeFuture(
            name='pq_producer.stop_future',
            done=False,
        )
        super(PqProducerFaker, self).__init__(
            name='pq_producer',
            start=mock.Mock(
                name='pq_producer.start',
                return_value=fake_start_future,
            ),
            write=mock.Mock(
                name='pq_producer.write',
                return_value=fake_write_future,
            ),
            stop_future=fake_stop_future,
        )
        self.start_result_ok = start_result_ok
        self.write_result_ok = write_result_ok
        self.fake_start_future = fake_start_future
        self.fake_write_future = fake_write_future

    def get_start_result_ok(self, max_seq_no=0):
        return WriteResponse(
            init=WriteResponse.Init(
                max_seq_no=max_seq_no,
            ),
        )

    def set_start_result_ok(self, max_seq_no=0):
        self.set_start_result(self.get_start_result_ok(max_seq_no))

    def set_seq_no(self, seq_no):
        self.start_result_ok.init.max_seq_no = seq_no
        self.write_result_ok.ack.seq_no = seq_no + 1

    def set_start_result_failure(
        self,
        reason=SessionDeathReason.FailedWithError,
        description=None,
        default_description_text='description',
    ):
        if description is None:
            description = WriteResponse(error=PersqueueError(code=1, description=default_description_text))
        self.fake_start_future.set_result_value(
            SessionFailureResult(reason=reason, description=description),
        )

    def set_start_result_invalid_type(self, value):
        self.set_start_result(value)

    def set_start_result_invalid(self, value):
        self.set_start_result(ProtobufFaker(data=value))

    def set_start_result(self, value):
        self.set_start_side_effect(None)
        self.fake_start_future.set_result_value(value)

    def set_start_side_effect(self, side_effect):
        self.fake_start_future.set_result_side_effect(side_effect)

    def set_write_side_effect(self, side_effect):
        self.fake_write_future.set_result_side_effect(side_effect)

    def set_write_result_invalid(self, value):
        self.fake_write_future.set_result_value(
            ProtobufFaker(data=value),
        )

    def set_write_result_invalid_type(self, value):
        self.fake_write_future.set_result_value(value)

    def set_connection_lost(self, result='test_error'):
        self.write.side_effect = AssertionError('write() shouldn\' be called while disconnected')
        self.stop_future.set_done(True)
        self.stop_future.set_result_value(result)

    def assert_start_result_called_with(self, *args, **kwargs):
        self.fake_start_future.result.assert_called_once_with(*args, **kwargs)

    def assert_write_result_called_with(self, *args, **kwargs):
        self.fake_write_future.result.assert_called_once_with(*args, **kwargs)


class PqApiFaker(mock.Mock):
    def __init__(self):
        fake_producer = PqProducerFaker()
        fake_start_future = FakeFuture(
            name='pq_streaming_api.start()->future',
            result_value=mock.Mock(
                name='pq_streaming_api__start_result',
            ),
        )
        super(PqApiFaker, self).__init__(
            name='pq_streaming_api',
            start=mock.Mock(
                name='pq_streaming_api.start',
                return_value=fake_start_future,
            ),
            create_producer=mock.Mock(
                name='pq_streaming_api.create_producer',
                return_value=fake_producer,
            )
        )
        self.fake_producer = fake_producer
        self.fake_start_future = fake_start_future

    def assert_start_result_called_with(self, *args, **kwargs):
        self.fake_start_future.result.assert_called_once_with(*args, **kwargs)


class MessageClass1(ProtobufFaker):
    pass


class MessageClass2(ProtobufFaker):
    pass


@with_settings_hosts(
    LOGBROKER_WRITERS={
        TEST_NAME1: {
            'host': TEST_HOST1,
            'port': TEST_PORT1,
            'topic': TEST_TOPIC1,
            'message_class': '{}.MessageClass1'.format(__name__),
            'credentials_config': TEST_CREDENTIALS_CONFIG_TVM,
            'source_id_prefix': TEST_SOURCE_ID_PREFIX,
            'connect_timeout': TEST_CONNECT_TIMEOUT,
            'write_timeout': TEST_WRITE_TIMEOUT,
            'extra_fields': TEST_META,
        },
        TEST_NAME2: {
            'host': TEST_HOST2,
            'port': TEST_PORT2,
            'topic': TEST_TOPIC2,
            'message_class': '{}.MessageClass2'.format(__name__),
            'credentials_config': TEST_CREDENTIALS_CONFIG_TVM,
            'source_id_prefix': TEST_SOURCE_ID_PREFIX,
            'connect_timeout': TEST_CONNECT_TIMEOUT,
            'write_timeout': TEST_WRITE_TIMEOUT,
            'ca_cert_file': '/path/to/ca/cert/file',
        },
    },
)
class TestLogbrokerBase(PassportTestCase):
    def setUp(self):
        self._patches = []
        NamedSingletonMeta._instances = {}

        self._fake_api = PqApiFaker()
        self._fake_producer = self._fake_api.fake_producer
        self._fake_api_class = mock.Mock(
            name='PqStreamingApi',
            return_value=self._fake_api,
        )
        self._patches.append(
            mock.patch.object(
                grpc_pq_streaming_api,
                'PQStreamingAPI',
                self._fake_api_class,
            ),
        )
        self._fake_tvm_manager = FakeTvmCredentialsManager()
        self._fake_tvm_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': TEST_TVM_ALIAS,
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )
        self._patches.append(self._fake_tvm_manager)

        self._patches.append(
            mock.patch(
                'passport.backend.core.logbroker.logbroker.uuid',
                mock.Mock(uuid4=mock.Mock(return_value=TEST_UUID)),
            ),
        )

        self._fake_graphite_log = GraphiteLoggerFaker()
        self._fake_graphite_log.bind_entry(
            'logbroker',
            service='logbroker',
        )
        self._patches.append(self._fake_graphite_log)

        self._open_mock = mock.mock_open(read_data='ca_cert')
        self._patches.append(
            mock.patch(
                '{}.open'.format('__builtin__' if six.PY2 else 'builtins'),
                self._open_mock,
            ),
        )

        for patch in self._patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self._patches):
            patch.stop()

    def assert_producer_create_params_ok(
        self, client, host=TEST_HOST1, port=TEST_PORT1, topic=TEST_TOPIC1,
        source_id=TEST_SOURCE_ID, extra_fields=TEST_META, seq=TEST_SEQ,
        root_certificates=None,
    ):
        self._fake_api_class.assert_called_once_with(host, port, root_certificates=root_certificates)
        configurator = client._configurator
        credentials = client._credentials
        self.assertIsInstance(configurator, ProducerConfigurator)
        self.assertEqual(configurator.topic, topic)
        self.assertEqual(configurator.source_id, source_id)
        self.assertEqual(configurator.extra_fields, extra_fields)
        self.assertIsInstance(credentials, TvmManagerCredentialsProvider)
        self.assertIsInstance(credentials.tvm_credentials_manager, TvmCredentialsManager)

        self.assertEqual(client._max_seq_no, seq)

    def assert_producer_start_status(
        self, client, connect_timeout=TEST_CONNECT_TIMEOUT, started=True,
    ):
        configurator = client._configurator
        credentials = client._credentials
        producer = self._fake_api.fake_producer
        if started:
            self._fake_api.start.assert_called_once_with()
            self._fake_api.assert_start_result_called_with(timeout=connect_timeout)
            producer.start.assert_called_once_with()
            producer.assert_start_result_called_with(timeout=connect_timeout)
            self._fake_api.create_producer.assert_called_once_with(configurator, credentials)
        else:
            self._fake_api.start.assert_not_called()
            producer.start.assert_not_called()
            self._fake_api.create_producer.assert_not_called()

    def assert_graphite_log_ok(self, lines):
        self._fake_graphite_log.assert_has_written(
            [self._fake_graphite_log.entry('logbroker', **line) for line in lines],
        )


class BaseTestCases(object):
    """ Хак, чтобы unittest не выполнял базовые тесты дважды """
    class LogbrokerWriterClassTestBase(TestLogbrokerBase):
        writer_class = None

        def setUp(self):
            super(BaseTestCases.LogbrokerWriterClassTestBase, self).setUp()
            self._version_patch = mock.patch.object(
                self.writer_class, 'PROTOCOL_VERSION', TEST_VERSION,
            )
            self._version_patch.start()

        def tearDown(self):
            super(BaseTestCases.LogbrokerWriterClassTestBase, self).tearDown()
            self._version_patch.stop()

        def get_logbroker_writer(self, name, **kwargs):
            raise NotImplementedError()

        def send_writer1(self, writer, data=TEST_PAYLOAD):
            writer.send(MessageClass1(data))

        def assert_sent(self, writer, data=TEST_PAYLOAD_ENCODED):
            writer._producer._producer.write.assert_called_once()
            args = writer._producer._producer.write.call_args[0]
            self.assertEqual(len(args), 2)
            write_arg = args[1]
            msg = PassportProtocolMessage()
            msg.ParseFromString(write_arg)
            self.assertEqual(msg.message_payload, data)
            return msg

        def test_get_logbroker_writer__multiple_classes__ok(self):
            writer1 = self.get_logbroker_writer(TEST_NAME1)
            self.assertIsInstance(writer1, self.writer_class)
            self.assertEqual(self._fake_api_class.call_count, 1)
            self.assertEqual(writer1.conf['host'], TEST_HOST1)
            self.assertIs(writer1.message_class, MessageClass1)
            expected_extra_fields = TEST_META
            expected_extra_fields.update(
                {
                    'message_class': 'MessageClass1',
                    'server': gethostname(),
                    'passport_protocol_v': TEST_STR_VERSION,
                },
            )
            self.assert_producer_create_params_ok(
                writer1._producer,
                seq=0,
                extra_fields=expected_extra_fields,
            )
            self.assert_producer_start_status(writer1._producer, started=False)

            writer2 = self.get_logbroker_writer(TEST_NAME2)
            self.assertIsInstance(writer2, self.writer_class)
            self.assertEqual(self._fake_api_class.call_count, 2)
            self.assertEqual(writer2.conf['host'], TEST_HOST2)
            self.assertIs(writer2.message_class, MessageClass2)
            self.assertIsNot(writer2, writer1)
            expected_extra_fields = {
                'message_class': 'MessageClass2',
                'server': gethostname(),
                'passport_protocol_v': TEST_STR_VERSION,
            }
            self.assertEqual(writer2._producer._configurator.extra_fields, expected_extra_fields)
            self.assert_producer_start_status(writer2._producer, started=False)

            writer1_1 = self.get_logbroker_writer(TEST_NAME1)
            self.assertEqual(self._fake_api_class.call_count, 2)
            self.assertIs(writer1_1, writer1)
            self.assertEqual(
                NamedSingletonMeta._instances,
                {
                    (self.writer_class, TEST_NAME1): writer1,
                    (self.writer_class, TEST_NAME2): writer2,
                },
            )
