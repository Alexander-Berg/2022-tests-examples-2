# -*- coding: utf-8 -*-
import inspect
from signal import SIGINT

import mock
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.logbroker_client.core.consumers.exceptions import ExitException
from passport.backend.logbroker_client.core.consumers.simple.native_worker import NativeLogbrokerWorker
from passport.backend.logbroker_client.core.handlers.exceptions import (
    HandlerException,
    ProtocolError,
)
from passport.backend.logbroker_client.core.logbroker.client import BaseLogbrokerClientException
from passport.backend.logbroker_client.core.logbroker.native_client import ConnectError
from passport.backend.logbroker_client.core.test.constants import (
    TEST_CA_CERT,
    TEST_CLIENT_ID,
    TEST_CONNECT_TIMEOUT,
    TEST_CREDENTIALS_CONFIG,
    TEST_DATA1,
    TEST_DATA2,
    TEST_DATA_PORT,
    TEST_FILE,
    TEST_HOST,
    TEST_LOGTYPE,
    TEST_MESSAGE_CLASS,
    TEST_PASSPORT_PROTOCOL_VERSION,
    TEST_TOPIC1,
)


class MockClient(mock.Mock):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'mock_native_client'
        super(MockClient, self).__init__(
            __enter__=mock.Mock(),
            __exit__=mock.Mock(),
            api_started=False,
            consumer_started=False,
            start=mock.Mock(),
            start_api=mock.Mock(),
            start_consumer=mock.Mock(),
            connect=mock.Mock(),
            **kwargs
        )
        self.start.side_effect = self._start_effect
        self.start_api.side_effect = self._start_api_effect
        self.start_consumer.side_effect = self._start_consumer_effect

    def _start_effect(self):
        self.api_started = True
        self.consumer_started = True

    def _start_api_effect(self):
        self.api_started = True

    def _start_consumer_effect(self):
        self.consumer_started = True


@with_settings_hosts
class TestNativeLogbrokerWorker(PassportTestCase):
    FAKE_HANDLER_OBJPATH = 'fake_handler_class'

    def setUp(self):
        self._patches = []
        self._handler_mock = mock.Mock()
        self._fake_exports = {
            self.FAKE_HANDLER_OBJPATH: mock.Mock(
                return_value=mock.Mock(
                    process=self._handler_mock,
                ),
            ),
        }

        self._client_mock = MockClient()
        self._client_handle_message_mock = self._client_mock.handle_message
        self._client_class_mock = mock.Mock(return_value=self._client_mock)
        self._patches.append(
            mock.patch(
                'passport.backend.logbroker_client.core.consumers.simple.native_worker.NativeLogbrokerConsumer',
                self._client_class_mock,
            ),
        )

        self._patches.append(
            mock.patch(
                'passport.backend.logbroker_client.core.consumers.simple.worker.importobj',
                self._fake_importobj,
            ),
        )

        self._sleep_mock = mock.Mock()
        self._patches.append(
            mock.patch(
                'passport.backend.logbroker_client.core.consumers.simple.native_worker.time',
                mock.Mock(sleep=self._sleep_mock),
            ),
        )

        for patch in self._patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self._patches):
            patch.stop()

    def _fake_importobj(self, objpath):
        return self._fake_exports[objpath]

    def _emit_side_effect(self, side_effect):
        if callable(side_effect) and not isinstance(side_effect, mock.Mock):
            return side_effect()
        elif isinstance(side_effect, Exception):
            raise side_effect
        else:
            return side_effect

    def _wrap_side_effects(self, effects):
        return (self._emit_side_effect(e) for e in effects)

    def _task(
        self, host=TEST_HOST, port=TEST_DATA_PORT, client_id=TEST_CLIENT_ID,
        credentials_config=TEST_CREDENTIALS_CONFIG, topic=TEST_TOPIC1,
        connect_timeout=None, ca_cert=None, decompress=False, use_client_locks=False,
        partition_group=None, max_count=None,
    ):
        task = {
            'host': host,
            'port': port,
            'client_id': client_id,
            'credentials_config': credentials_config,
            'topic': topic,
            'decompress': decompress,
            'use_client_locks': use_client_locks,
            'max_count': max_count,
        }
        if connect_timeout is not None:
            task['connect_timeout'] = connect_timeout
        if ca_cert is not None:
            task['ca_cert'] = ca_cert
        if partition_group is not None:
            task['partition_group'] = partition_group
        return task

    def _build_handler_config(self, args=None):
        args = args or {}
        return {'class': self.FAKE_HANDLER_OBJPATH, 'args': args}

    def _build_worker(self):
        return NativeLogbrokerWorker(handler=self._build_handler_config(), config={})

    def _build_worker_with_task(self, task):
        worker = self._build_worker()
        worker.read_task = mock.Mock(side_effect=[task])
        return worker

    def _build_message(self, offset, extra_items):
        return mock.Mock(
            offset=offset,
            meta=mock.Mock(
                extra_fields=mock.Mock(
                    items=[mock.Mock(key=k, value=v) for k, v in extra_items.items()],
                ),
            ),
        )

    @staticmethod
    def _mock_except(obj, keep):
        for method in dir(obj):
            if method.startswith('_') or method in keep:
                continue
            setattr(obj, method, mock.Mock())

    @staticmethod
    def _raise(exception):
        raise exception

    def _bind_client_message_loop(self, effects):
        side_effect_callbacks = []
        for effect in effects:
            if isinstance(effect, Exception):
                side_effect_callbacks.append(
                    (lambda _effect: lambda handler: self._raise(_effect))(effect),
                )
            elif callable(effect):
                side_effect_callbacks.append(effect)
            else:
                side_effect_callbacks.append(
                    (lambda _effect: lambda handler: handler(**_effect))(effect),
                )
        i_effect = iter(side_effect_callbacks)
        self._client_handle_message_mock.side_effect = lambda handler: next(i_effect)(handler)

    def _assert_messages(self, messages):
        self.assertEqual(self._handler_mock.call_count, len(messages))
        self._handler_mock.assert_has_calls(
            [mock.call(message['header'], message['decompressed_data']) for message in messages],
        )

    def test_loop__ok(self):
        task = self._task()
        worker = self._build_worker_with_task(task)
        self._mock_except(worker, ['read_task', 'loop', 'run_task'])
        worker.create_client.return_value = self._client_mock

        worker.loop()
        worker.read_task.assert_called_once_with()
        worker.create_client.assert_called_once_with(task)
        worker.connect_loop.assert_called_once_with(self._client_mock)
        worker.read_loop.assert_called_once_with(self._client_mock)
        self._client_mock.__enter__.assert_called_once_with()
        self._client_mock.__exit__.assert_called_once_with(None, None, None)

    def test_loop__exit_on_task_read_error(self):
        worker = self._build_worker()
        self._mock_except(worker, ['loop', 'run_task'])
        worker.read_task.side_effect = IOError

        worker.loop()
        worker.read_task.assert_called_once_with()
        worker.create_client.assert_not_called()
        worker.connect_loop.assert_not_called()
        worker.read_loop.assert_not_called()
        self._client_mock.__enter__.assert_not_called()
        self._client_mock.__exit__.assert_not_called()

    def test_create_client__default__ok(self):
        worker = self._build_worker()
        task = self._task()
        client = worker.create_client(task)
        self.assertEqual(client, self._client_mock)
        self._client_class_mock.assert_called_once_with(
            host=TEST_HOST,
            port=TEST_DATA_PORT,
            ca_cert=None,
            client_id=TEST_CLIENT_ID,
            credentials_config=TEST_CREDENTIALS_CONFIG,
            topic=TEST_TOPIC1,
            connect_timeout=0.3,
            is_interrupted_callback=worker._is_interrupted,
            decompress=False,
            use_client_locks=False,
            partition_group=None,
            max_count=None,
        )
        self.assertIs(worker._is_interrupted(), False)
        worker.handle_sigint(SIGINT, inspect.currentframe())
        self.assertIs(worker._is_interrupted(), True)

    def test_create_client__overridden_args__ok(self):
        worker = self._build_worker()
        task = self._task(
            ca_cert=TEST_CA_CERT,
            connect_timeout=TEST_CONNECT_TIMEOUT,
            use_client_locks=True,
            partition_group=3,
            max_count=4,
        )
        client = worker.create_client(task)
        self.assertEqual(client, self._client_mock)
        self._client_class_mock.assert_called_once_with(
            host=TEST_HOST,
            port=TEST_DATA_PORT,
            ca_cert=TEST_CA_CERT,
            client_id=TEST_CLIENT_ID,
            credentials_config=TEST_CREDENTIALS_CONFIG,
            topic=TEST_TOPIC1,
            connect_timeout=TEST_CONNECT_TIMEOUT,
            is_interrupted_callback=worker._is_interrupted,
            decompress=False,
            use_client_locks=True,
            partition_group=3,
            max_count=4,
        )

    def test_connect_loop__first_try__ok(self):
        worker = self._build_worker()
        worker.connect_loop(self._client_mock)
        self._client_mock.start.assert_called_once_with()
        self._sleep_mock.assert_not_called()

    def test_connect_loop__retry__ok(self):
        worker = self._build_worker()
        self._client_mock.start.side_effect = [
            BaseLogbrokerClientException,
            BaseLogbrokerClientException,
            None,
        ]
        worker.connect_loop(self._client_mock)
        self.assertEqual(self._client_mock.start.call_count, 3)
        self._client_mock.start.assert_has_calls([mock.call(), mock.call(), mock.call()])
        self.assertEqual(self._sleep_mock.call_count, 2)
        self._sleep_mock.assert_has_calls([mock.call(1.0), mock.call(1.0)])

    def test_connect_loop__client_exception__raises(self):
        worker = self._build_worker()
        self._client_mock.start.side_effect = [
            ValueError,
        ]
        with self.assertRaises(ValueError):
            worker.connect_loop(self._client_mock)

    def test_reconnect_loop__first_try__ok(self):
        worker = self._build_worker()
        worker.reconnect_loop(self._client_mock)
        self._client_mock.start.assert_not_called()
        self._client_mock.start_consumer.assert_called_once_with()
        self._sleep_mock.assert_not_called()

    def test_reconnect_loop__retry__ok(self):
        worker = self._build_worker()
        self._client_mock.start_consumer.side_effect = [
            BaseLogbrokerClientException,
            BaseLogbrokerClientException,
            None,
        ]
        worker.reconnect_loop(self._client_mock)
        self._client_mock.start.assert_not_called()
        self.assertEqual(self._client_mock.start_consumer.call_count, 3)
        self._client_mock.start_consumer.assert_has_calls([mock.call(), mock.call(), mock.call()])
        self.assertEqual(self._sleep_mock.call_count, 2)
        self._sleep_mock.assert_has_calls([mock.call(1.0), mock.call(1.0)])

    def test_reconnect_loop__client_exception__raises(self):
        worker = self._build_worker()
        self._client_mock.start_consumer.side_effect = [
            ValueError,
        ]
        with self.assertRaises(ValueError):
            worker.reconnect_loop(self._client_mock)

    def test_read_loop__ok(self):
        worker = self._build_worker_with_task(self._task())
        extra_items = {
            'file': TEST_FILE,
            'server': TEST_HOST,
            'ident': TEST_CLIENT_ID,
            'logtype': TEST_LOGTYPE,
            'message_class': TEST_MESSAGE_CLASS,
            'passport_protocol_v': TEST_PASSPORT_PROTOCOL_VERSION,
        }
        messages = [
            dict(
                topic=TEST_TOPIC1,
                partition=0,
                message=self._build_message(
                    offset=1,
                    extra_items=extra_items,
                ),
                decompressed_data=TEST_DATA1,
            ),
            BaseLogbrokerClientException(),
            dict(
                topic=TEST_TOPIC1,
                partition=2,
                message=self._build_message(
                    offset=3,
                    extra_items={'path': TEST_FILE},
                ),
                decompressed_data=TEST_DATA2,
            ),
        ]
        self._bind_client_message_loop(messages)
        with self.assertRaises(StopIteration):
            worker.read_loop(self._client_mock)
        self._sleep_mock.assert_called_once_with(0.1)
        self._assert_messages(
            [
                dict(
                    header=dict(
                        topic=TEST_TOPIC1,
                        partition=0,
                        offset=1,
                        path=TEST_FILE,
                        server=TEST_HOST,
                        ident=TEST_CLIENT_ID,
                        logtype=TEST_LOGTYPE,
                        message_class=TEST_MESSAGE_CLASS,
                        passport_protocol_v=TEST_PASSPORT_PROTOCOL_VERSION,
                        extra_fields=extra_items,
                    ),
                    decompressed_data=TEST_DATA1,
                ),
                dict(
                    header=dict(
                        topic=TEST_TOPIC1,
                        partition=2,
                        offset=3,
                        path=TEST_FILE,
                        server=None,
                        ident=None,
                        logtype=None,
                        message_class=None,
                        passport_protocol_v=None,
                        extra_fields={'path': TEST_FILE},
                    ),
                    decompressed_data=TEST_DATA2,
                ),
            ],
        )

    def test_read_loop__exit_exception__ok(self):
        worker = self._build_worker_with_task(self._task())
        extra_items = {
            'file': TEST_FILE,
            'server': TEST_HOST,
            'ident': TEST_CLIENT_ID,
            'logtype': TEST_LOGTYPE,
            'message_class': TEST_MESSAGE_CLASS,
            'passport_protocol_v': TEST_PASSPORT_PROTOCOL_VERSION,
        }
        messages = [
            dict(
                topic=TEST_TOPIC1,
                partition=0,
                message=self._build_message(
                    offset=1,
                    extra_items=extra_items,
                ),
                decompressed_data=TEST_DATA1,
            ),
            ExitException(),
        ]
        self._bind_client_message_loop(messages)
        worker.read_loop(self._client_mock)
        self._assert_messages(
            [
                dict(
                    header=dict(
                        topic=TEST_TOPIC1,
                        partition=0,
                        offset=1,
                        path=TEST_FILE,
                        server=TEST_HOST,
                        ident=TEST_CLIENT_ID,
                        logtype=TEST_LOGTYPE,
                        message_class=TEST_MESSAGE_CLASS,
                        passport_protocol_v=TEST_PASSPORT_PROTOCOL_VERSION,
                        extra_fields=extra_items,
                    ),
                    decompressed_data=TEST_DATA1,
                ),
            ],
        )

    def test_read_loop__reconnect__ok(self):
        worker = self._build_worker_with_task(self._task())
        extra_items = {
            'file': TEST_FILE,
            'server': TEST_HOST,
            'ident': TEST_CLIENT_ID,
            'logtype': TEST_LOGTYPE,
            'message_class': TEST_MESSAGE_CLASS,
            'passport_protocol_v': TEST_PASSPORT_PROTOCOL_VERSION,
        }
        messages = [
            dict(
                topic=TEST_TOPIC1,
                partition=0,
                message=self._build_message(
                    offset=1,
                    extra_items=extra_items,
                ),
                decompressed_data=TEST_DATA1,
            ),
            ConnectError(),
            dict(
                topic=TEST_TOPIC1,
                partition=0,
                message=self._build_message(
                    offset=2,
                    extra_items=extra_items,
                ),
                decompressed_data=TEST_DATA2,
            ),
        ]
        self._bind_client_message_loop(messages)

        worker.reconnect_loop = mock.Mock()
        with self.assertRaises(StopIteration):
            worker.read_loop(self._client_mock)

        self._assert_messages(
            [
                dict(
                    header=dict(
                        topic=TEST_TOPIC1,
                        partition=0,
                        offset=1,
                        path=TEST_FILE,
                        server=TEST_HOST,
                        ident=TEST_CLIENT_ID,
                        logtype=TEST_LOGTYPE,
                        message_class=TEST_MESSAGE_CLASS,
                        passport_protocol_v=TEST_PASSPORT_PROTOCOL_VERSION,
                        extra_fields=extra_items,
                    ),
                    decompressed_data=TEST_DATA1,
                ),
                dict(
                    header=dict(
                        topic=TEST_TOPIC1,
                        partition=0,
                        offset=2,
                        path=TEST_FILE,
                        server=TEST_HOST,
                        ident=TEST_CLIENT_ID,
                        logtype=TEST_LOGTYPE,
                        message_class=TEST_MESSAGE_CLASS,
                        passport_protocol_v=TEST_PASSPORT_PROTOCOL_VERSION,
                        extra_fields=extra_items,
                    ),
                    decompressed_data=TEST_DATA2,
                ),
            ],
        )
        worker.reconnect_loop.assert_called_once_with(self._client_mock)

    def test_read_loop__retry_handler__ok(self):
        self._handler_mock.side_effect = [
            HandlerException,
            Exception,
            None,
        ]
        worker = self._build_worker_with_task(self._task())
        extra_items = {
            'file': TEST_FILE,
            'server': TEST_HOST,
            'ident': TEST_CLIENT_ID,
            'logtype': TEST_LOGTYPE,
            'message_class': TEST_MESSAGE_CLASS,
            'passport_protocol_v': TEST_PASSPORT_PROTOCOL_VERSION,
        }
        messages = [
            dict(
                topic=TEST_TOPIC1,
                partition=0,
                message=self._build_message(
                    offset=1,
                    extra_items=extra_items,
                ),
                decompressed_data=TEST_DATA1,
            ),
        ]
        self._bind_client_message_loop(messages)
        with self.assertRaises(StopIteration):
            worker.read_loop(self._client_mock)
        self.assertEqual(self._sleep_mock.call_count, 2)
        self._sleep_mock.assert_has_calls([mock.call(0.1)] * 2)
        self._assert_messages(
            [
                dict(
                    header=dict(
                        topic=TEST_TOPIC1,
                        partition=0,
                        offset=1,
                        path=TEST_FILE,
                        server=TEST_HOST,
                        ident=TEST_CLIENT_ID,
                        logtype=TEST_LOGTYPE,
                        message_class=TEST_MESSAGE_CLASS,
                        passport_protocol_v=TEST_PASSPORT_PROTOCOL_VERSION,
                        extra_fields=extra_items,
                    ),
                    decompressed_data=TEST_DATA1,
                ),
            ] * 3,
        )

    def test_read_loop__protocol_error__skip(self):
        self._handler_mock.side_effect = [
            ProtocolError,
            ProtocolError,
        ]
        worker = self._build_worker_with_task(self._task())
        messages = [
            dict(
                topic=TEST_TOPIC1,
                partition=0,
                message=self._build_message(
                    offset=1,
                    extra_items={},
                ),
                decompressed_data=TEST_DATA1,
            ),
            BaseLogbrokerClientException(),
            dict(
                topic=TEST_TOPIC1,
                partition=2,
                message=self._build_message(
                    offset=3,
                    extra_items={},
                ),
                decompressed_data=TEST_DATA2,
            ),
        ]
        self._bind_client_message_loop(messages)
        with self.assertRaises(StopIteration):
            worker.read_loop(self._client_mock)
        self._sleep_mock.assert_called_once_with(0.1)
        self._assert_messages(
            [
                dict(
                    header=dict(
                        topic=TEST_TOPIC1,
                        partition=0,
                        offset=1,
                        path=None,
                        server=None,
                        ident=None,
                        logtype=None,
                        message_class=None,
                        passport_protocol_v=None,
                        extra_fields={},
                    ),
                    decompressed_data=TEST_DATA1,
                ),
                dict(
                    header=dict(
                        topic=TEST_TOPIC1,
                        partition=2,
                        offset=3,
                        path=None,
                        server=None,
                        ident=None,
                        logtype=None,
                        message_class=None,
                        passport_protocol_v=None,
                        extra_fields={},
                    ),
                    decompressed_data=TEST_DATA2,
                ),
            ],
        )
