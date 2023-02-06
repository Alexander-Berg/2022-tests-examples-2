# -*- coding: utf-8 -*-
import mock
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.logbroker_client.core.consumers.simple.native_emitter import PartitionsCountNativeEmitter
from passport.backend.logbroker_client.core.test.constants import (
    TEST_CA_CERT,
    TEST_CLIENT_ID,
    TEST_CLIENT_ID2,
    TEST_CREDENTIALS_CONFIG,
    TEST_CREDENTIALS_CONFIG2,
    TEST_DATA_PORT,
    TEST_DATA_PORT2,
    TEST_ENDPOINT1,
    TEST_ENDPOINT2,
    TEST_HOST,
    TEST_HOST_RE,
    TEST_TOPIC1,
    TEST_TOPIC2,
    TEST_TOPIC3,
)


@with_settings_hosts
class TestPartitionsCountNativeEmitter(PassportTestCase):
    def setUp(self):
        self._tasks_queue_put = mock.Mock()
        self._tasks_queue = mock.Mock(put=self._tasks_queue_put)

        self._socket_mock = mock.Mock(gethostname=mock.Mock(return_value=TEST_HOST))
        self._socket_patch = mock.patch(
            'passport.backend.logbroker_client.core.consumers.simple.native_emitter.socket',
            self._socket_mock,
        )
        self._socket_patch.start()

    def tearDown(self):
        self._socket_patch.stop()

    def _build_emitter(
        self, per_host_config, workers_count, connect_timeout=None,
        ca_cert=None, ssl=None, decompress=None, use_client_locks=None,
    ):
        args = dict(
            per_host_config=per_host_config,
            data_port=TEST_DATA_PORT,
            client_id=TEST_CLIENT_ID,
            credentials_config=TEST_CREDENTIALS_CONFIG,
            workers_count=workers_count,
        )
        if connect_timeout is not None:
            args['connect_timeout'] = connect_timeout
        if ca_cert is not None:
            args['ca_cert'] = ca_cert
        if ssl is not None:
            args['ssl'] = ssl
        if decompress is not None:
            args['decompress'] = decompress
        if use_client_locks is not None:
            args['use_client_locks'] = use_client_locks
        emitter = PartitionsCountNativeEmitter(**args)
        emitter.tasks_queue = self._tasks_queue
        return emitter

    @staticmethod
    def _make_host_config(host_config):
        return {
            TEST_HOST_RE: host_config,
            'garbage': {
                'targets': [
                    {'host': 'garbage_host', 'topic': 'garbage_topic'},
                ],
            },
        }

    def _assert_tasks(self, tasks):
        self.assertEqual(
            self._tasks_queue_put.call_count,
            len(tasks),
            'Wrong tasks number {}, expected {}\nReal: {}\nExpected: {}'.format(
                self._tasks_queue_put.call_count,
                len(tasks),
                self._tasks_queue_put.call_args_list,
                tasks,
            ),
        )
        self.assertEqual(
            [call[0][0] for call in self._tasks_queue_put.call_args_list],
            tasks,
        )

    @mock.patch('passport.backend.logbroker_client.core.consumers.simple.native_emitter.time')
    def test_loop__ok(self, time):
        emitter = self._build_emitter(
            per_host_config=self._make_host_config(
                {
                    'targets': [
                        {'host': '1', 'topic': '1'},
                    ],
                },
            ),
            workers_count=1,
        )

        def __interrupt(*_):
            emitter.INTERRUPTED = True

        time.sleep = mock.Mock(side_effect=__interrupt)
        emitter.emit = mock.Mock()
        emitter.loop()
        emitter.emit.assert_called_once_with()
        time.sleep.assert_called_once_with(1)

    def test_emit__single_target_single_worker__ok(self):
        emitter = self._build_emitter(
            per_host_config=self._make_host_config(
                {
                    'targets': [
                        {'host': TEST_ENDPOINT1, 'topic': TEST_TOPIC1},
                    ],
                },
            ),
            workers_count=1,
            ssl=False,
            ca_cert=TEST_CA_CERT,
            connect_timeout=0.5,
            decompress=True,
        )
        emitter.emit()
        self._assert_tasks([
            {
                'host': TEST_ENDPOINT1,
                'port': TEST_DATA_PORT,
                'ssl': False,
                'ca_cert': TEST_CA_CERT,
                'client_id': TEST_CLIENT_ID,
                'credentials_config': TEST_CREDENTIALS_CONFIG,
                'topic': TEST_TOPIC1,
                'connect_timeout': 0.5,
                'decompress': True,
                'use_client_locks': False,
            },
        ])

    def test_emit__multiple_targets_multiple_workers__ok(self):
        emitter = self._build_emitter(
            per_host_config=self._make_host_config(
                {
                    'targets': [
                        {
                            'host': TEST_ENDPOINT1,
                            'topic': TEST_TOPIC1,
                            'ssl': True,
                        },
                        {
                            'host': TEST_ENDPOINT1,
                            'topic': TEST_TOPIC2,
                            'ssl': False,
                        },
                        {
                            'host': TEST_ENDPOINT2,
                            'topic': TEST_TOPIC3,
                            'data_port': TEST_DATA_PORT2,
                            'client_id': TEST_CLIENT_ID2,
                            'credentials_config': TEST_CREDENTIALS_CONFIG2,
                        },
                    ],
                },
            ),
            workers_count=4,
            use_client_locks=True,
        )
        emitter.emit()
        self._assert_tasks([
            {
                'host': TEST_ENDPOINT1,
                'port': TEST_DATA_PORT,
                'ssl': True,
                'ca_cert': None,
                'client_id': TEST_CLIENT_ID,
                'credentials_config': TEST_CREDENTIALS_CONFIG,
                'topic': TEST_TOPIC1,
                'decompress': False,
                'use_client_locks': True,
            },
            {
                'host': TEST_ENDPOINT1,
                'port': TEST_DATA_PORT,
                'ssl': False,
                'ca_cert': None,
                'client_id': TEST_CLIENT_ID,
                'credentials_config': TEST_CREDENTIALS_CONFIG,
                'topic': TEST_TOPIC2,
                'decompress': False,
                'use_client_locks': True,
            },
            {
                'host': TEST_ENDPOINT2,
                'port': TEST_DATA_PORT2,
                'ssl': True,
                'ca_cert': None,
                'client_id': TEST_CLIENT_ID2,
                'credentials_config': TEST_CREDENTIALS_CONFIG2,
                'topic': TEST_TOPIC3,
                'decompress': False,
                'use_client_locks': True,
            },
            {
                'host': TEST_ENDPOINT1,
                'port': TEST_DATA_PORT,
                'ssl': True,
                'ca_cert': None,
                'client_id': TEST_CLIENT_ID,
                'credentials_config': TEST_CREDENTIALS_CONFIG,
                'topic': TEST_TOPIC1,
                'decompress': False,
                'use_client_locks': True,
            },
        ])

    def test_workers_less_than_targets__error(self):
        with self.assertRaisesRegexp(ValueError, 'workers count .+ less than targets count'):
            self._build_emitter(
                per_host_config=self._make_host_config(
                    {
                        'targets': [
                            {'host': '1', 'topic': '1'},
                            {'host': '2', 'topic': '2'},
                        ],
                    },
                ),
                workers_count=1,
            )
