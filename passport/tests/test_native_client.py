# -*- coding: utf-8 -*-
from concurrent.futures import TimeoutError as FutureTimeoutError
from functools import partial
import re

from kikimr.public.sdk.python.persqueue.errors import SessionFailureResult
from kikimr.public.sdk.python.persqueue.grpc_pq_streaming_api import ConsumerMessageType
from kikimr.yndx.api.protos.persqueue_pb2 import ReadResponse
import mock
from nose_parameterized import parameterized
from passport.backend.core.logbroker.logbroker_base import TvmManagerCredentialsProvider
from passport.backend.core.logbroker.test.constants import TEST_CREDENTIALS_CONFIG_TVM
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.logbroker_client.core.consumers.exceptions import ExitException
from passport.backend.logbroker_client.core.logbroker.client import TimeoutException
from passport.backend.logbroker_client.core.logbroker.decompress import BadArchive
from passport.backend.logbroker_client.core.logbroker.native_client import (
    ConnectError,
    NativeLogbrokerConsumer,
    ProtocolError,
    WatchedFutureProperty,
)
from passport.backend.logbroker_client.core.test.constants import (
    TEST_CA_CERT,
    TEST_CLIENT_ID,
    TEST_CONNECT_TIMEOUT,
    TEST_DATA1,
    TEST_DATA2,
    TEST_DATA3,
    TEST_DATA4,
    TEST_DATA5,
    TEST_DATA6,
    TEST_DATA_PORT,
    TEST_HOST,
    TEST_SESSION_ID,
    TEST_TIMESTAMP1,
    TEST_TIMESTAMP2,
    TEST_TOPIC1,
)
from ydb.public.api.protos.draft.persqueue_common_pb2 import Error as PersqueueError


class RequestIdManagerFaker(object):
    def __init__(self):
        self.ids = []
        self._history = []

    @property
    def history(self):
        if self.ids:
            return self._history + [self.ids]
        else:
            return self._history

    def push_request_id(self, *values):
        self.ids.extend(values)

    def clear_request_id(self):
        if self.ids:
            self._history.append(list(self.ids))
        self.ids *= 0


class AnyRequestId(object):
    re_id = re.compile('^[a-f0-9]{12}$')

    def __eq__(self, other):
        return bool(self.re_id.match(other))


class AnyRequestIdsJoined(AnyRequestId):
    def __init__(self, count, sep='|'):
        self.count = count
        self.sep = sep

    def __eq__(self, other):
        parts = other.split(self.sep)
        return all(self.re_id.match(x) for x in parts)


class BatchIterator(object):
    def __init__(self, batches):
        self.batches = batches
        self.position = 0

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def __len__(self):
        return len(self.batches)

    def __next__(self):
        try:
            batch = self.batches[self.position]
        except IndexError:
            raise StopIteration()
        self.position += 1

        if callable(batch) and not isinstance(batch, mock.Mock):
            # batch value is side effect
            batch()
            return self.__next__()

        return batch


@with_settings_hosts
class _BaseTestNativeLogbrokerConsumer(PassportTestCase):
    def setUp(self):
        self._client_interrupted = False
        self._message_batches = []
        self._i_message_batches = iter(self._message_batches)
        self._messages_callback = mock.Mock()
        self._consumer_next_event_running = False

        self._patches = []

        self._consumer_configurator_faker = mock.Mock()
        self._consumer_configurator_class_faker = mock.Mock(return_value=self._consumer_configurator_faker)
        self._patches.append(
            mock.patch(
                'passport.backend.logbroker_client.core.logbroker.native_client.ConsumerConfigurator',
                self._consumer_configurator_class_faker,
            ),
        )

        self._auto_decompressor_faker = mock.Mock(
            decompress=mock.Mock(side_effect=lambda value: b'decompressed ' + value),
        )
        self._patches.append(
            mock.patch(
                'passport.backend.logbroker_client.core.logbroker.native_client.AutoDecompressor',
                mock.Mock(return_value=self._auto_decompressor_faker),
            ),
        )

        self._init_result = ReadResponse(
            init=ReadResponse.Init(
                session_id=TEST_SESSION_ID,
            ),
        )
        self._consumer_start_future_faker = mock.Mock(
            result=mock.Mock(
                return_value=self._init_result,
            ),
        )
        self._consumer_next_event_faker = mock.Mock(
            name='consumer_faker.next_event_faker',
            side_effect=self._consumer_next_event_emulator,
        )
        self._consumer_stop_future_faker = mock.Mock(
            name='consumer_faker.stop_future_faker',
            done=mock.Mock(return_value=False),
            result=mock.Mock(return_value=None),
        )
        self._consumer_faker = mock.Mock(
            name='consumer_faker',
            start=mock.Mock(return_value=self._consumer_start_future_faker),
            stop_future=self._consumer_stop_future_faker,
            next_event=self._consumer_next_event_faker,
        )
        self._api_start_future_faker = mock.Mock()
        self._api_faker = mock.Mock(
            start=mock.Mock(return_value=self._api_start_future_faker),
            create_consumer=mock.Mock(return_value=self._consumer_faker),
        )
        self._api_class_faker = mock.Mock(return_value=self._api_faker)
        self._patches.append(
            mock.patch(
                'passport.backend.logbroker_client.core.logbroker.native_client.PQStreamingAPI',
                self._api_class_faker,
            ),
        )

        self._tvm_manager_faker = mock.Mock()
        self._patches.append(
            mock.patch(
                'passport.backend.core.logbroker.logbroker_base.get_tvm_credentials_manager',
                mock.Mock(return_value=self._tvm_manager_faker),
            ),
        )

        self._request_id_manager_faker = RequestIdManagerFaker()
        self._patches.append(
            mock.patch(
                'passport.backend.logbroker_client.core.utils.RequestIdManager',
                self._request_id_manager_faker,
            ),
        )

        self._fake_future_watch_log = mock.Mock()
        self._patches.append(
            mock.patch.object(
                WatchedFutureProperty,
                '_warn',
                self._fake_future_watch_log,
            ),
        )

        for patch in self._patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self._patches):
            patch.stop()

    def _is_interrupted(self):
        return self._client_interrupted

    def _build_client(
        self, credentials_config=None, decompress=True, connect=False,
        use_client_locks=False, partition_group=None, max_count=None,
    ):
        if credentials_config is None:
            credentials_config = TEST_CREDENTIALS_CONFIG_TVM
        client = NativeLogbrokerConsumer(
            host=TEST_HOST,
            port=TEST_DATA_PORT,
            ca_cert=TEST_CA_CERT,
            client_id=TEST_CLIENT_ID,
            credentials_config=credentials_config,
            topic=TEST_TOPIC1,
            connect_timeout=TEST_CONNECT_TIMEOUT,
            is_interrupted_callback=self._is_interrupted,
            decompress=decompress,
            use_client_locks=use_client_locks,
            partition_group=partition_group,
            max_count=max_count,
        )
        if connect:
            client.start()
        return client

    def _build_lock_message(self):
        return mock.Mock(
            type=ConsumerMessageType.MSG_LOCK,
            message=mock.Mock(
                lock=mock.Mock(
                    topic=TEST_TOPIC1,
                    partition=0,
                ),
            ),
            ready_to_read=mock.Mock(),
        )

    def _build_release_message(self):
        return mock.Mock(
            type=ConsumerMessageType.MSG_RELEASE,
            message=mock.Mock(
                release=mock.Mock(
                    topic=TEST_TOPIC1,
                    partition=0,
                ),
            ),
        )

    def _build_message(self, messages, offset, partition=0):
        return mock.Mock(
            message=[
                mock.Mock(
                    data=_data,
                    offset=offset,
                    meta=mock.Mock(
                        seq_no=offset + _i,
                        create_time_ms=TEST_TIMESTAMP1,
                        write_time_ms=TEST_TIMESTAMP2,
                    ),
                )
                for _i, _data in enumerate(messages)
            ],
            topic=TEST_TOPIC1,
            partition=partition,
        )

    def _build_message_batch(
        self, batches, result_type=ConsumerMessageType.MSG_DATA, name=None,
        cookie=1,
    ):
        main_name = 'message_batch'
        if name is not None:
            main_name = name + '_' + main_name
        return mock.Mock(
            name=main_name,
            message=mock.Mock(
                name='{}.message'.format(main_name),
                data=mock.Mock(
                    name='{}.message.data'.format(main_name),
                    message_batch=BatchIterator(batches),
                    cookie=cookie,
                ),
            ),
            type=result_type,
        )

    def _build_common_message(self, offset=100):
        return self._build_message(
            messages=[TEST_DATA1],
            offset=offset,
            partition=0,
        )

    def _build_common_message_batch(self, name=None):
        batch_name = 'common'
        if name is not None:
            batch_name = name + '_' + batch_name
        return self._build_message_batch(
            [
                self._build_common_message(),
            ],
            name=batch_name,
        )

    def _bind_messages(self, message_batches):
        self._message_batches = message_batches
        self._i_message_batches = iter(self._message_batches)

    def _consumer_next_event_emulator(self):
        """
        Эмулятор поведения PQStreamingConsumer.next_event:
        если в данный момент уже есть next event future в статусе running,
        то этот метод вернёт future, из которого никогда не будет получен результат
        """
        if self._consumer_next_event_running:
            return mock.Mock(
                name='next_future_faker_stuck',
                result=mock.Mock(side_effect=FutureTimeoutError),
            )
        else:
            self._consumer_next_event_running = True
            return mock.Mock(
                name='next_future_faker',
                result=mock.Mock(side_effect=self._consumer_next_event_future_result),
            )

    def _consumer_next_event_future_result(self, timeout):
        self._consumer_next_event_running = False
        result = next(self._i_message_batches)
        if isinstance(result, Exception):
            raise result
        elif callable(result) and not isinstance(result, mock.Mock):
            return result()
        else:
            return result

    def _assert_messages(self, messages, decompress=True):
        expected_messages = list(dict(message) for message in messages)
        for expected_message in expected_messages:
            if decompress:
                decompressed_data = b'decompressed ' + expected_message['data']
            else:
                decompressed_data = expected_message['data']
            expected_message['decompressed_data'] = decompressed_data
            expected_message['topic'] = TEST_TOPIC1
            expected_message['create_time_ms'] = TEST_TIMESTAMP1
            expected_message['write_time_ms'] = TEST_TIMESTAMP2

        real_messages = [
            {
                'decompressed_data': kwargs['decompressed_data'],
                'topic': kwargs['topic'],
                'data': kwargs['message'].data,
                'offset': kwargs['message'].offset,
                'seq_no': kwargs['message'].meta.seq_no,
                'create_time_ms': kwargs['message'].meta.create_time_ms,
                'write_time_ms': kwargs['message'].meta.write_time_ms,
                'partition': kwargs['partition'],
            }
            for _args, kwargs in self._messages_callback.call_args_list
        ]
        self.assertEqual(real_messages, expected_messages)

    def _assert_no_messages(self):
        self._assert_messages([])

    def _assert_api_started(self, client):
        self._api_class_faker.assert_called_once_with(
            host=TEST_HOST,
            port=TEST_DATA_PORT,
            root_certificates=TEST_CA_CERT,
        )
        self._api_faker.start.assert_called_once_with()
        self._api_start_future_faker.result.assert_called_once_with(TEST_CONNECT_TIMEOUT)
        self.assertTrue(client.api_started)

    def _assert_consumer_not_started(self, client):
        self.assertFalse(client.consumer_started)
        self.assertIsNone(client._consumer)
        self.assertIsNone(client._session_id)
        self._consumer_faker.start.assert_not_called()
        self._consumer_start_future_faker.result.assert_not_called()

    def _assert_consumer_started(self, client):
        self._api_faker.create_consumer.assert_called_once_with(
            self._consumer_configurator_faker,
            client._credentials,
        )
        self._consumer_faker.start.assert_called_once_with()
        self._consumer_start_future_faker.result.assert_called_once_with(TEST_CONNECT_TIMEOUT)
        self.assertTrue(client.consumer_started)
        self.assertEqual(client._session_id, TEST_SESSION_ID)

    def _assert_common_message(self):
        self._assert_messages(
            [
                dict(
                    data=TEST_DATA1,
                    offset=100,
                    seq_no=100,
                    partition=0,
                ),
            ],
        )

    def _assert_request_id_set(self, values):
        self.assertEqual(self._request_id_manager_faker.history, values)

    def _assert_no_request_id(self):
        self.assertFalse(self._request_id_manager_faker.ids)

    def _assert_commits(self, *cookies):
        commit = self._consumer_faker.commit
        expected_calls = [mock.call(cookie) for cookie in cookies]
        self.assertEqual(commit.call_args_list, expected_calls)

    def _assert_no_commits(self):
        self._assert_commits()

    def _assert_no_future_watch_warnings_triggered(self):
        self._fake_future_watch_log.assert_not_called()


class TestNativeLogbrokerConsumerConnect(_BaseTestNativeLogbrokerConsumer):
    def test_create__ok(self):
        client = self._build_client(max_count=1)
        self.assertEqual(client._host, TEST_HOST)
        self.assertEqual(client._port, TEST_DATA_PORT)
        self.assertEqual(client._ca_cert, TEST_CA_CERT)
        self.assertEqual(client._topic, TEST_TOPIC1)
        self.assertEqual(client._connect_timeout, TEST_CONNECT_TIMEOUT)
        self.assertIsInstance(client._credentials, TvmManagerCredentialsProvider)
        self.assertEqual(client.api_started, False)
        self.assertEqual(client.consumer_started, False)
        self.assertEqual(client._decompressor, self._auto_decompressor_faker)
        self.assertEqual(client._received_count, 0)
        self._consumer_configurator_class_faker.assert_called_once_with(
            topics=TEST_TOPIC1, client_id=TEST_CLIENT_ID, use_client_locks=False,
            max_count=1,
        )
        self._assert_no_request_id()
        self._assert_no_future_watch_warnings_triggered()

    def test_create_explicit_partition__ok(self):
        self._build_client(partition_group=2, use_client_locks=True)
        self._consumer_configurator_class_faker.assert_called_once_with(
            topics=TEST_TOPIC1, client_id=TEST_CLIENT_ID, use_client_locks=True,
            partition_groups=[2], max_count=None,
        )

    def test_start_consumer_and_api__ok(self):
        client = self._build_client()

        client.start_api()
        self._assert_api_started(client)
        self._assert_consumer_not_started(client)

        client.start_consumer()
        self._assert_api_started(client)
        self._assert_consumer_started(client)

        self._assert_no_request_id()
        self._assert_no_future_watch_warnings_triggered()

    def test_start__ok(self):
        client = self._build_client()
        client.start()
        self._assert_api_started(client)
        self._assert_consumer_started(client)
        self._assert_no_request_id()
        self._assert_no_future_watch_warnings_triggered()

    def test_start__api_start_timeout__raises_and_calls_start_only_once(self):
        client = self._build_client()
        self._api_start_future_faker.result.side_effect = FutureTimeoutError()
        for _ in range(2):
            with self.assertRaises(TimeoutException):
                client.start()
        self._api_faker.start.assert_called_once_with()
        self._assert_no_future_watch_warnings_triggered()

    def test_consumer_start_timeout__exception(self):
        client = self._build_client()
        self._consumer_start_future_faker.result.side_effect = FutureTimeoutError()
        with self.assertRaises(TimeoutException):
            client.start()
        self._assert_no_future_watch_warnings_triggered()

    def test_consumer_start_timeout__exception__consumer_and_start_not_called_twice(self):
        client = self._build_client()
        self._consumer_start_future_faker.result.side_effect = FutureTimeoutError()
        with self.assertRaises(TimeoutException):
            client.start()
        self._api_faker.create_consumer.assert_called_once()
        self._consumer_faker.start.assert_called_once_with()

        with self.assertRaises(TimeoutException):
            client.start()
        self._api_faker.create_consumer.assert_called_once()
        self._consumer_faker.start.assert_called_once_with()
        self._assert_no_future_watch_warnings_triggered()

        self._consumer_start_future_faker.result.side_effect = None
        self._consumer_start_future_faker.result.return_value = self._init_result
        client.start()
        self._api_faker.create_consumer.assert_called_once()
        self._consumer_faker.start.assert_called_once_with()
        self._assert_no_future_watch_warnings_triggered()

    def test_consumer_start_error__exception(self):
        client = self._build_client()
        self._consumer_start_future_faker.result.return_value = SessionFailureResult(
            reason='reason', description=PersqueueError(description='abc', code=123),
        )
        with self.assertRaises(ConnectError):
            client.start()
        self._assert_no_future_watch_warnings_triggered()

    def test_consumer_start_error__wrong_result_attr_types__no_side_effects(self):
        client = self._build_client()
        self._consumer_start_future_faker.result.return_value = SessionFailureResult(
            reason=123, description={'123': u'абв'},
        )
        with self.assertRaises(ConnectError):
            client.start()
        self._assert_no_future_watch_warnings_triggered()

    def test_consumer_start_wrong_result_fields__no_side_effect(self):
        client = self._build_client()
        self._consumer_start_future_faker.result.return_value = ReadResponse()
        with self.assertRaises(ProtocolError):
            client.start()
        self._assert_no_future_watch_warnings_triggered()

    def test_consumer_start_wrong_result_type__no_side_effect(self):
        client = self._build_client()
        self._consumer_start_future_faker.result.return_value = 'абв'
        with self.assertRaises(ProtocolError):
            client.start()
        self._assert_no_future_watch_warnings_triggered()


class TestNativeLogbrokerConsumerHandleMessage(_BaseTestNativeLogbrokerConsumer):
    def test_simple__ok(self):
        client = self._build_client(connect=True)
        self._bind_messages([
            self._build_message_batch(
                [
                    self._build_message(
                        messages=[
                            TEST_DATA1,
                            TEST_DATA2,
                        ],
                        offset=100,
                        partition=0,
                    ),
                    self._build_message(
                        messages=[
                            TEST_DATA3,
                            TEST_DATA4,
                        ],
                        offset=102,
                        partition=0,
                    ),
                ],
                cookie=1,
            ),
            FutureTimeoutError(),
            FutureTimeoutError(),
            FutureTimeoutError(),
            self._build_message_batch(
                [
                    self._build_message(
                        messages=[
                            'garbage',
                        ],
                        offset=199,
                        partition=1,
                    ),
                ],
                cookie=2,
                result_type=ConsumerMessageType.MSG_COMMIT,
            ),
            self._build_message_batch(
                [
                    self._build_message(
                        messages=[
                            TEST_DATA5,
                        ],
                        offset=200,
                        partition=1,
                    ),
                    self._build_message(
                        messages=[
                            TEST_DATA6,
                        ],
                        offset=201,
                        partition=1,
                    ),
                ],
                cookie=3,
            ),
        ])
        client.handle_message(self._messages_callback)
        client.handle_message(self._messages_callback)
        with self.assertRaises(StopIteration):
            client.handle_message(self._messages_callback)

        self._assert_messages(
            [
                dict(
                    data=TEST_DATA1,
                    offset=100,
                    seq_no=100,
                    partition=0,
                ),
                dict(
                    data=TEST_DATA2,
                    offset=100,
                    seq_no=101,
                    partition=0,
                ),
                dict(
                    data=TEST_DATA3,
                    offset=102,
                    seq_no=102,
                    partition=0,
                ),
                dict(
                    data=TEST_DATA4,
                    offset=102,
                    seq_no=103,
                    partition=0,
                ),
                dict(
                    data=TEST_DATA5,
                    offset=200,
                    seq_no=200,
                    partition=1,
                ),
                dict(
                    data=TEST_DATA6,
                    offset=201,
                    seq_no=201,
                    partition=1,
                ),
            ]
        )
        self._assert_commits(1, 3)
        self._assert_request_id_set(
            [
                [1, AnyRequestId()],
                [1, AnyRequestId()],
                [1, AnyRequestId()],
                [1, AnyRequestId()],
                [AnyRequestIdsJoined(4)],
                [3, AnyRequestId()],
                [3, AnyRequestId()],
                [AnyRequestIdsJoined(2)],
            ],
        )
        self.assertEqual(client._received_count, 6)
        self._assert_no_future_watch_warnings_triggered()

    def test__erroneous_message_type__protocol_error(self):
        client = self._build_client(connect=True)
        self._bind_messages(
            [
                self._build_message_batch(
                    [
                        self._build_message(
                            messages=['garbage'],
                            offset=101,
                            partition=0,
                        ),
                    ],
                    result_type=ConsumerMessageType.MSG_ERROR,
                ),
                self._build_common_message_batch(),
            ],
        )
        with self.assertRaisesRegexp(ProtocolError, r'^Message read error'):
            client.handle_message(self._messages_callback)
        client.handle_message(self._messages_callback)

        self._assert_commits(1)
        self._assert_common_message()
        self._assert_no_future_watch_warnings_triggered()

    def test__unknown_message_type__protocol_error(self):
        client = self._build_client(connect=True)
        self._bind_messages(
            [
                self._build_message_batch(
                    [
                        self._build_message(
                            messages=['garbage'],
                            offset=101,
                            partition=0,
                        ),
                    ],
                    result_type=ConsumerMessageType.MSG_LOCK,
                ),
                self._build_common_message_batch(),
            ],
        )
        with self.assertRaisesRegexp(ProtocolError, r'^Wrong message type'):
            client.handle_message(self._messages_callback)
        client.handle_message(self._messages_callback)

        self._assert_commits(1)
        self._assert_common_message()
        self._assert_no_future_watch_warnings_triggered()

    def test__wrong_read_result_type__protocol_error(self):
        client = self._build_client(connect=True)
        self._bind_messages([u'абв', self._build_common_message_batch()])
        with self.assertRaises(ProtocolError):
            client.handle_message(self._messages_callback)
        client.handle_message(self._messages_callback)

        self._assert_commits(1)
        self._assert_common_message()
        self._assert_no_future_watch_warnings_triggered()

    def test_bad_archive__protocol_error(self):
        client = self._build_client(connect=True)
        old_decompressor_side_effect = self._auto_decompressor_faker.decompress.side_effect

        def new_side_effect(body):
            self._auto_decompressor_faker.decompress.side_effect = old_decompressor_side_effect
            raise BadArchive()

        self._auto_decompressor_faker.decompress.side_effect = new_side_effect

        self._bind_messages(
            [
                self._build_common_message_batch(),
                self._build_common_message_batch(),
            ],
        )
        with self.assertRaisesRegexp(ProtocolError, r'^Failed to decompress data'):
            client.handle_message(self._messages_callback)
        client.handle_message(self._messages_callback)

        self._assert_commits(1)
        self._assert_common_message()
        self._assert_no_future_watch_warnings_triggered()

    def test_interrupt_await_data__exit_exception(self):
        client = self._build_client(connect=True)
        self._client_interrupted = True
        with self.assertRaises(ExitException):
            client.handle_message(self._messages_callback)
        self._assert_no_future_watch_warnings_triggered()

    def test_interrupt_await_event__exit_exception(self):
        client = self._build_client(connect=True)

        def side_effect():
            self._client_interrupted = True
            raise FutureTimeoutError()

        self._bind_messages(
            [
                FutureTimeoutError(),
                FutureTimeoutError(),
                side_effect,
                FutureTimeoutError(),
            ],
        )
        with self.assertRaises(ExitException):
            client.handle_message(self._messages_callback)
        self._assert_no_commits()
        self._assert_no_future_watch_warnings_triggered()

    @parameterized.expand((i,) for i in range(3))
    def test_interrupt_between_batches__no_next_commits(self, interrupt_idx):
        client = self._build_client(connect=True)

        messages = [
            self._build_common_message_batch(),
            self._build_message_batch([
                self._build_common_message(offset=101),
                self._build_common_message(offset=102),
                self._build_common_message(offset=103),
                self._build_common_message(offset=104),
            ], cookie=2),
            self._build_message_batch([
                self._build_common_message(offset=105),
                self._build_common_message(offset=106),
            ], cookie=3),
        ]

        def side_effect(res):
            self._client_interrupted = True
            return res

        bound_side_effect = partial(side_effect, messages[interrupt_idx])
        messages[interrupt_idx] = bound_side_effect

        self._bind_messages(messages)
        with self.assertRaises(ExitException):
            for _ in range(4):
                client.handle_message(self._messages_callback)

        self._assert_commits(*[1, 2, 3][:interrupt_idx + 1])
        self._assert_no_future_watch_warnings_triggered()

    @parameterized.expand((i,) for i in range(3))
    def test_interrupt_inside_batches__batch_committed(self, interrupt_idx):
        client = self._build_client(connect=True)

        def side_effect():
            self._client_interrupted = True

        interrupted_batch_messages = [
            self._build_common_message(offset=101),
            self._build_common_message(offset=102),
            self._build_common_message(offset=104),
        ]
        interrupted_batch_messages.insert(interrupt_idx, side_effect)

        self._bind_messages([
            self._build_common_message_batch(),
            self._build_message_batch(interrupted_batch_messages, cookie=2),
            self._build_message_batch([
                self._build_common_message(offset=105),
                self._build_common_message(offset=106),
            ], cookie=3),
        ])
        with self.assertRaises(ExitException):
            for _ in range(4):
                client.handle_message(self._messages_callback)

        self._assert_commits(1, 2)
        self._assert_no_future_watch_warnings_triggered()

    def test_exit_inside_handler__no_current_or_next_commits(self):
        client = self._build_client(connect=True)

        self._bind_messages([
            self._build_common_message_batch(),
            self._build_message_batch([
                self._build_common_message(offset=101),
                self._build_message(["INTERRUPT"], offset=102),
                self._build_common_message(offset=104),
            ], cookie=2),
            self._build_message_batch([
                self._build_common_message(offset=105),
                self._build_common_message(offset=106),
            ], cookie=3),
        ])

        def _handle_with_exception(topic, partition, message, decompressed_data):
            raise ExitException()

        with self.assertRaises(ExitException):
            for i in range(4):
                if i == 1:
                    messages_callback = _handle_with_exception
                else:
                    messages_callback = self._messages_callback
                client.handle_message(messages_callback)

        self._assert_commits(1)
        self._assert_no_future_watch_warnings_triggered()

    def test_connection_lost_before_read__connect_error(self):
        client = self._build_client(connect=True)
        self._consumer_faker.start.assert_called_once_with()
        self._consumer_stop_future_faker.done.return_value = True
        self._consumer_stop_future_faker.result.return_value = SessionFailureResult(
            reason='reason', description=PersqueueError(description='abc', code=1),
        )

        self._bind_messages(
            [
                self._build_common_message_batch(),
                self._build_common_message_batch(),
            ],
        )
        with self.assertRaisesRegexp(
            ConnectError,
            'Consumer stopped: reason=reason description=[^\n]+INITIALIZING[^\n]+abc[^\n]+$',
        ):
            client.handle_message(self._messages_callback)
        self._assert_no_messages()
        self._assert_no_commits()

        client.start()
        self.assertEqual(self._api_faker.create_consumer.call_count, 2)
        self.assertEqual(self._consumer_faker.start.call_count, 2)
        self._assert_no_future_watch_warnings_triggered()

    def test_connection_lost_during_read__connect_error(self):
        client = self._build_client(connect=True)
        self._consumer_faker.start.assert_called_once_with()

        def side_effect():
            self._consumer_stop_future_faker.done.return_value = True
            self._consumer_stop_future_faker.result.return_value = SessionFailureResult(
                reason='reason', description=PersqueueError(description='abc', code=1),
            )
            return self._build_common_message_batch('2')

        self._bind_messages(
            [
                self._build_common_message_batch('1'),
                side_effect,
            ],
        )
        client.handle_message(self._messages_callback)
        with self.assertRaisesRegexp(
            ConnectError,
            'Consumer stopped: reason=reason description=[^\n]+INITIALIZING[^\n]+abc[^\n]+$',
        ):
            client.handle_message(self._messages_callback)
        self._assert_common_message()
        self._assert_commits(1)

        client.start()
        self.assertEqual(self._api_faker.create_consumer.call_count, 2)
        self.assertEqual(self._consumer_faker.start.call_count, 2)
        self._assert_no_future_watch_warnings_triggered()

    @parameterized.expand([
        ('abc', 'abc'),
        (SessionFailureResult(reason=123, description={'123': u'абв'}), r"reason=123 description=\{'123': ('абв'|u'.+')\}"),
    ])
    def test_connection_lost__wrong_result_type__no_side_effect(self, stop_result, expect_template):
        client = self._build_client(connect=True)
        self._consumer_faker.start.assert_called_once_with()
        self._consumer_stop_future_faker.done.return_value = True
        self._consumer_stop_future_faker.result.return_value = stop_result

        self._bind_messages(
            [
                self._build_common_message_batch(),
                self._build_common_message_batch(),
            ],
        )
        with self.assertRaisesRegexp(ConnectError, 'Consumer stopped: ' + expect_template):
            client.handle_message(self._messages_callback)
        self._assert_no_messages()
        self._assert_no_commits()

        client.start()
        self.assertEqual(self._api_faker.create_consumer.call_count, 2)
        self.assertEqual(self._consumer_faker.start.call_count, 2)
        self._assert_no_future_watch_warnings_triggered()

    def test_future_watch__ok(self):
        client = self._build_client(connect=False)
        self._assert_no_future_watch_warnings_triggered()
        fake_future = mock.Mock(
            done=mock.Mock(return_value=True),
        )

        client._consumer_start_poll.future = fake_future
        self._assert_no_future_watch_warnings_triggered()
        client._consumer_start_poll.future = None
        self._assert_no_future_watch_warnings_triggered()

        fake_future.done.return_value = False
        client._consumer_start_poll.future = fake_future
        self._assert_no_future_watch_warnings_triggered()
        client._consumer_start_poll.future = None
        self._fake_future_watch_log.assert_called_once()

    def test_no_client_locks__lock_message__exception(self):
        self._bind_messages(
            [
                self._build_lock_message(),
            ],
        )
        client = self._build_client(connect=True)
        with self.assertRaises(ProtocolError):
            client.handle_message(self._messages_callback)

    def test_no_client_locks__release_message__exception(self):
        self._bind_messages(
            [
                self._build_release_message(),
            ],
        )

        client = self._build_client(connect=True)
        with self.assertRaises(ProtocolError):
            client.handle_message(self._messages_callback)

    def test_client_locks__lock_message_and_release_message__ok(self):
        lock_message = self._build_lock_message()

        def check_state_after_lock_message__then_next_message():
            lock_message.ready_to_read.assert_called_once()
            self.assertEqual(
                client._remote_partition_state,
                {
                    'state': 'ASSIGNED',
                    'topic': TEST_TOPIC1,
                    'partition': 0,
                },
            )
            return self._build_common_message_batch()

        def exit_side_effect():
            self._client_interrupted = True
            raise FutureTimeoutError()

        self._bind_messages(
            [
                lock_message,
                check_state_after_lock_message__then_next_message,
                self._build_release_message(),
                exit_side_effect,
            ],
        )

        client = self._build_client(connect=True, use_client_locks=True)
        client.handle_message(self._messages_callback)
        with self.assertRaises(ExitException):
            client.handle_message(self._messages_callback)

        self._assert_common_message()
        self.assertEqual(
            client._remote_partition_state,
            {
                'state': 'RELEASED',
                'old_topic': TEST_TOPIC1,
                'old_partition': 0,
            },
        )
