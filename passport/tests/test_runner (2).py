import unittest

import dataclasses
import mock
from passport.backend.logbroker_client.core.native_runner.config import Config
from passport.backend.logbroker_client.core.native_runner.runner import NativeRunner


TEST_HOSTNAME = 'annoying.tv'


class RunnerTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.hostname_patch = mock.patch('socket.gethostname', return_value=TEST_HOSTNAME)
        self.hostname_patch.start()

    def tearDown(self):
        self.hostname_patch.stop()

    def build_config(self):
        return dict(
            base=dict(
                connect_timeout=3.0,
                client_id='test/client',
                data_port=1122,
                credentials_config=dict(
                    credentials_type='tvm',
                    tvm_alias='logbroker_api',
                ),
                max_count=5,
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
                    dict(
                        host='2.some.test.host',
                        topic='topic2',
                        fixed_partitions=False,
                        decompress=True,
                        ca_cert='aaazzz',
                        max_count=10,
                    ),
                ],
            ),
        )

    def test_generate_worker_tasks__ok(self):
        runner = NativeRunner(dict(lbc=self.build_config()))
        config1 = Config(
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
            max_count=5,
        )
        config2 = dataclasses.replace(
            config1,
            host='2.some.test.host',
            topic='topic2',
            fixed_partitions=False,
            decompress=True,
            ca_cert=b'aaazzz',
            max_count=10,
        )

        self.assertEqual(
            list(runner.generate_worker_tasks()),
            [
                (config1, dict(
                    host='some.test.host',
                    port=1122,
                    ca_cert=None,
                    client_id='test/client',
                    credentials_config=dict(
                        credentials_type='tvm',
                        tvm_alias='logbroker_api',
                    ),
                    topic='topic1',
                    decompress=False,
                    use_client_locks=True,
                    connect_timeout=3.0,
                    partition_group=partition_group,
                    max_count=5,
                ))
                for partition_group in (1, 2)
            ] + [
                (config2, dict(
                    host='2.some.test.host',
                    port=1122,
                    ca_cert=b'aaazzz',
                    client_id='test/client',
                    credentials_config=dict(
                        credentials_type='tvm',
                        tvm_alias='logbroker_api',
                    ),
                    topic='topic2',
                    decompress=True,
                    use_client_locks=False,
                    connect_timeout=3.0,
                    max_count=10,
                ))
            ] * 2,
        )
