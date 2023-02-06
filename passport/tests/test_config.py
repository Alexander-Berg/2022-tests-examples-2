import unittest

import mock
from passport.backend.logbroker_client.core.native_runner.config import (
    Config,
    parse_config,
)


TEST_HOSTNAME = 'annoying.tv'


class ConfigTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.hostname_patch = mock.patch('socket.gethostname', return_value=TEST_HOSTNAME)
        self.hostname_patch.start()
        self.open_mock = mock.mock_open(read_data='some_ca_cert')
        self.open_patch = mock.patch('builtins.open', self.open_mock)
        self.open_patch.start()

    def tearDown(self):
        self.open_patch.stop()
        self.hostname_patch.stop()

    def test_simple__ok(self):
        config = dict(
            base=dict(
                connect_timeout=3.0,
                client_id='test/client',
                data_port=1122,
                credentials_config=dict(
                    credentials_type='tvm',
                    tvm_alias='logbroker_api',
                ),
                partitions=2,
                fixed_partitions=True,
                handler_class='some.class',
                handler_args=dict(
                    arg1='val1',
                ),
                targets=[
                    dict(
                        host='some.test.host',
                        topic='topic1',
                    ),
                ],
            ),
        )

        self.assertEqual(parse_config(config), [Config(
            partitions=2,
            credentials_config=dict(
                credentials_type='tvm',
                tvm_alias='logbroker_api',
            ),
            client_id='test/client',
            host='some.test.host',
            topic='topic1',
            handler_class='some.class',
            handler_args=dict(
                arg1='val1',
            ),
            data_port=1122,
            connect_timeout=3.0,
            fixed_partitions=True,
        )])

    def test_per_host__ok(self):
        config = dict(
            base=dict(
                connect_timeout=3.0,
                client_id='test/client',
                data_port=1122,
                max_count=10,
                credentials_config=dict(
                    credentials_type='tvm',
                    tvm_alias='logbroker_api',
                ),
                partitions=2,
                fixed_partitions=True,
                handler_class='some.class',
                handler_args=dict(
                    arg1='val1',
                    arg2='val2',
                ),
            ),
            per_host={
                r'^some\.wrong$': dict(wrong='option'),
                r'^annoying\.tv$': dict(
                    targets=[
                        dict(
                            host='some.test.host',
                            topic='topic1',
                            handler_args=dict(
                                arg3='val3',
                            ),
                            max_count=15,
                            ca_cert_file='/some/ca/cert/file',
                        ),
                        dict(
                            host='2.some.test.host',
                            topic='topic2',
                            fixed_partitions=False,
                            decompress=True,
                            ca_cert='aaazzz',
                            __handler_args=dict(
                                arg1='val1.1',
                            )
                        ),
                    ],
                ),
            },
        )

        self.assertEqual(parse_config(config), [
            Config(
                partitions=2,
                credentials_config=dict(
                    credentials_type='tvm',
                    tvm_alias='logbroker_api',
                ),
                client_id='test/client',
                host='some.test.host',
                topic='topic1',
                handler_class='some.class',
                handler_args=dict(
                    arg3='val3',
                ),
                data_port=1122,
                connect_timeout=3.0,
                fixed_partitions=True,
                decompress=False,
                ca_cert=b'some_ca_cert',
                max_count=15,
            ),
            Config(
                partitions=2,
                credentials_config=dict(
                    credentials_type='tvm',
                    tvm_alias='logbroker_api',
                ),
                client_id='test/client',
                host='2.some.test.host',
                topic='topic2',
                handler_class='some.class',
                handler_args=dict(
                    arg1='val1.1',
                    arg2='val2',
                ),
                data_port=1122,
                connect_timeout=3.0,
                fixed_partitions=False,
                decompress=True,
                ca_cert=b'aaazzz',
                max_count=10,
            ),
        ])
        self.open_mock.assert_called_once_with('/some/ca/cert/file')
