# -*- coding: utf-8 -*-
from io import BytesIO
import itertools
import json
import os
import shutil
import tempfile
import time

from botocore.exceptions import ClientError
from frozendict import frozendict
import mock
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.builders.passport.faker.fake_passport import (
    FakePassport,
    passport_ok_response,
)
from passport.backend.core.logbroker.faker.fake_logbroker import FakeLogbrokerWriterProto
from passport.backend.core.logging_utils.faker.fake_tskv_logger import StatboxLoggerFaker
from passport.backend.core.protobuf.takeout.takeout_pb2 import TakeoutRequest
from passport.backend.core.s3.faker.fake_s3 import (
    FakeS3Client,
    s3_ok_response,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_CLIENT_ID_2,
    TEST_TICKET,
)
from passport.backend.logbroker_client.core.consumers.simple.native_worker import NativeLogbrokerWorker
from passport.backend.logbroker_client.core.test.native_client.protobuf_handler import BaseProtobufHandlerTestCase
from passport.backend.logbroker_client.takeout_tasks.handler import TakeoutTaskHandler
from passport.backend.takeout.common.builders import (
    STATUS_NO_DATA,
    STATUS_PENDING,
)
from passport.backend.takeout.common.conf import get_config
from passport.backend.takeout.common.conf.crypto import get_keys_for_encrypting
from passport.backend.takeout.common.conf.services import ServiceConfig
from passport.backend.takeout.common.crypto import encrypt_stream
from passport.backend.takeout.common.job_id import make_job_id_v1
from passport.backend.takeout.common.logbroker import TakeoutLogbrokerWriterProto
from passport.backend.takeout.common.touch import TouchFiles
from passport.backend.takeout.test_utils.fake_builders import (
    FakeAsyncServiceBuilder,
    FakeAsyncUploadServiceBuilder,
    FakeSyncServiceBuilder,
    raw_file_response,
    service_ok_response,
)
from passport.backend.takeout.test_utils.fake_redis import FakeRedis
from passport.backend.takeout.test_utils.touch import FakeTouchFiles


TEST_SERVICES_CONFIG = {
    'alice_iot': ServiceConfig.from_dict({
        'enabled': True,
        'type': 'sync',
        'tvm_dst_alias': 'takeout',
        'urls': {
            'base': 'http://iot-beta.quasar.yandex.net',
            'suffix_get': '/takeout',
        },
    }),
    'ether': ServiceConfig.from_dict({
        'enabled': True,
        'type': 'async',
        'tvm_dst_alias': 'takeout',
        'urls': {
            'base': 'https://ether-backend.yandex-team.ru',
            'suffix_start': '/takeout',
            'suffix_get': '/takeout',
        },
    }),
    'corporate_blog': ServiceConfig.from_dict({
        'enabled': True,
        'type': 'async_upload',
        'tvm_dst_alias': 'takeout',
        'urls': {
            'base': 'https://takeout-test.yablogs.yandex.net',
            'suffix_start': '/takeout',
        },
    }),
    'grocery-takeout': ServiceConfig.from_dict({
        'type': 'sync',
        'tvm_dst_alias': 'disabled_service',
        'urls': {'base': ''},
    }),
}
TEST_SERVICE_NAME = 'ether'
TEST_STEP = 'start'
TEST_TASK_ID = '12345678'
TEST_UID = 123
TEST_EXTRACT_ID = '456'
TEST_UNIXTIME = int(time.time())
TEST_JOB_ID = 'job-321'

TEST_BUCKET = 'takeout'
TEST_FILE_CONTENT = b'test_content'

TEST_PASSWORD = 'pass'
TEST_DIR = tempfile.mkdtemp()

TEST_DELAY_DELTA = 600
TEST_EXPIRE_DELTA = 3000

TEST_COUNT_FOR_FULL_CHECK = 100

TEST_NOW_TS = 1644596225.123

TEST_DELAY_THROTTLING_MIN_EXEC_TIME = 0.2


def encrypt_bytes(bytes_sequence):
    keys = get_keys_for_encrypting()
    key_version = get_config()['s3']['encryption_key_version']

    input_stream = BytesIO(bytes_sequence)
    output_file = encrypt_stream(
        input_stream,
        keys,
        key_version,
    )
    return output_file.read()


class _BaseTestTakeoutTaskHandler(BaseProtobufHandlerTestCase):
    MESSAGE_CLASS = 'passport.backend.core.protobuf.takeout.takeout_pb2.TakeoutRequest'
    TOPIC = 'takeout-tasks'
    CONFIGS = [
        'base.yaml',
        'takeout/secrets.yaml?',
        'takeout-tasks/base.yaml',
        'takeout-tasks/testing.yaml',
        'logging.yaml',
        'export.yaml',
        {
            'passport': {
                'use_tvm': False,
            },
            'archive': {
                'cooking_directory': TEST_DIR,
            },
            'task_deltas': {
                'expire': TEST_EXPIRE_DELTA,
            },
            'delay_throttling_min_exec_time': TEST_DELAY_THROTTLING_MIN_EXEC_TIME,
        },
        'takeout-tasks/export.yaml',
    ]
    EXTRA_EXPORTED_CONFIGS = {
        'LOGBROKER_WRITERS': {
            'takeout_tasks': frozendict({
                'host': 'logbroker.yandex.net',
                'port': 2135,
                'topic': 'passport/passport-takeout-tasks-testing',
                'message_class': 'passport.backend.core.protobuf.takeout.takeout_pb2.TakeoutRequest',
                'source_id_prefix': 'passport-takeout-takeout-tasks',
                'credentials_config': {
                    'credentials_type': 'tvm',
                    'tvm_alias': 'logbroker_api',
                },
                'connect_timeout': 2.0,
            }),
        },

        'PASSPORT_URL': 'http://passport.localhost/',
        'PASSPORT_TIMEOUT': 1,
        'PASSPORT_RETRIES': 2,
        'PASSPORT_CONSUMER': 'takeout',

        'S3_ENDPOINT': 'http://s3.localhost/',
        'S3_SECRET_KEY_ID': 'key_id',
        'S3_SECRET_KEY': 'key',
        'S3_CONNECT_TIMEOUT': 1,
        'S3_READ_TIMEOUT': 1,
        'S3_RETRIES': 2,
        'S3_TAKEOUT_BUCKET_NAME': 'takeout',
        'SSL_CA_CERT': 'default-ca-cert-path',
    }

    def setUp(self):
        super(_BaseTestTakeoutTaskHandler, self).setUp()

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'takeout',
                        'ticket': TEST_TICKET,
                    },
                    str(TEST_CLIENT_ID_2): {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                }
            )
        )

        self.s3_faker = FakeS3Client()

        self.services_config = mock.patch(
            'passport.backend.logbroker_client.takeout_tasks.handler.get_service_configs',
            mock.Mock(return_value=TEST_SERVICES_CONFIG),
        )
        self.builder_services_config = mock.patch(
            'passport.backend.takeout.common.builders.get_service_configs',
            mock.Mock(return_value=TEST_SERVICES_CONFIG),
        )
        self.check_archive_services_config = mock.patch(
            'passport.backend.takeout.logbroker_client.make_archive.get_service_configs',
            mock.Mock(return_value=TEST_SERVICES_CONFIG),
        )

        self.logbroker_writer_faker = FakeLogbrokerWriterProto(TakeoutLogbrokerWriterProto, 'takeout_tasks')

        self.statbox_faker = StatboxLoggerFaker()

        self.fake_passport = FakePassport()
        self.fake_passport.set_response_value('takeout_start_extract', passport_ok_response())

        self.redis_faker = FakeRedis()

        self.fake_blackbox = FakeBlackbox()
        self.fake_blackbox.set_blackbox_response_value(
            method='userinfo',
            value=blackbox_userinfo_response(uid=TEST_UID),
        )

        self.touch_faker = FakeTouchFiles(self.s3_faker, self.redis_faker)

        self.current_task_patch = mock.patch.object(
            NativeLogbrokerWorker,
            'current_task',
            dict(host='1.host.com', partition_group=3),
        )

        self.fake_time = mock.Mock(return_value=TEST_NOW_TS)
        self.now_patch = mock.patch('time.time', self.fake_time)

        self.fake_sleep = mock.Mock()
        self.sleep_patch = mock.patch('time.sleep', self.fake_sleep)

        self.patches = [
            self.fake_tvm_credentials_manager,
            self.s3_faker,
            self.services_config,
            self.builder_services_config,
            self.check_archive_services_config,
            self.logbroker_writer_faker,
            self.statbox_faker,
            self.fake_passport,
            self.fake_blackbox,
            self.current_task_patch,
            self.now_patch,
            self.sleep_patch,
            self.redis_faker,
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        super(_BaseTestTakeoutTaskHandler, self).tearDown()

        for patch in reversed(self.patches):
            patch.stop()

    def _make_handler(self, **kwargs):
        return TakeoutTaskHandler(
            config=self.config,
            message_class=self.MESSAGE_CLASS,
            **kwargs
        )

    def _make_extract_data(self, uid=TEST_UID, unixtime=TEST_UNIXTIME, extract_id=TEST_EXTRACT_ID, services=None,
                           retries=None, max_retries=None):
        return TakeoutRequest(
            task_base_message=TakeoutRequest.TaskBaseMessage(
                task_id=TEST_TASK_ID,
                uid=uid,
                unixtime=unixtime,
                task_name='extract',
                extract_id=extract_id,
                retries=retries,
                max_retries=max_retries,
            ),
            extract=TakeoutRequest.TaskExtractMessage(
                services=services,
            ),
        )

    def _make_extract_service_data(self, uid=TEST_UID, unixtime=TEST_UNIXTIME, extract_id=TEST_EXTRACT_ID,
                                   service_name=TEST_SERVICE_NAME, step=None, job_id=None,
                                   retries=None, max_retries=None):
        return TakeoutRequest(
            task_base_message=TakeoutRequest.TaskBaseMessage(
                task_id=TEST_TASK_ID,
                uid=uid,
                unixtime=unixtime,
                task_name='extract_service',
                extract_id=extract_id,
                retries=retries,
                max_retries=max_retries,
            ),
            extract_service=TakeoutRequest.TaskExtractServiceMessage(
                service=service_name,
                step=step,
                job_id=job_id,
            ),
        )

    def _make_data_for_make_archive(self, services, uid=TEST_UID, unixtime=TEST_UNIXTIME, extract_id=TEST_EXTRACT_ID,
                                    retries=0):
        return TakeoutRequest(
            task_base_message=TakeoutRequest.TaskBaseMessage(
                task_id=TEST_TASK_ID,
                uid=uid,
                unixtime=unixtime,
                task_name='make_archive',
                extract_id=extract_id,
                retries=retries,
            ),
            make_archive=TakeoutRequest.TaskMakeArchiveMessage(
                services=services,
            ),
        )

    def _make_data_for_cleanup(self, uid=TEST_UID, unixtime=TEST_UNIXTIME, extract_id=TEST_EXTRACT_ID, retries=0,
                               delay_until=0, seq=0, source=''):
        return TakeoutRequest(
            task_base_message=TakeoutRequest.TaskBaseMessage(
                task_id=TEST_TASK_ID,
                uid=uid,
                unixtime=unixtime,
                task_name='cleanup',
                extract_id=extract_id,
                retries=retries,
                delay_until=delay_until,
                seq=seq,
                source=source,
                send_time=int(TEST_NOW_TS),
            ),
        )

    def check_statbox_log(self, task_id=TEST_TASK_ID, uid=TEST_UID, unixtime=TEST_UNIXTIME, extract_id=TEST_EXTRACT_ID,
                          task_name='extract', status='ok', **kwargs):
        expected_values = dict(
            log_source='logbroker',
            tskv_format='takeout-log',
            task_id=task_id,
            uid=str(uid),
            extract_id=extract_id,
            archive_requested_unixtime=str(unixtime),
            status=status,
            task_name=task_name,
        )
        expected_values.update(**kwargs)

        self.statbox_faker.assert_has_written([
            self.statbox_faker.entry('base', **expected_values),
        ])

    @property
    def tvm_headers(self):
        return {
            'X-Ya-Service-Ticket': TEST_TICKET,
        }


class TestTakeoutStartTaskHandler(_BaseTestTakeoutTaskHandler):
    def test_construct(self):
        self._make_handler()
        self._make_extract_data()
        self._make_extract_service_data()

    def test_override_logbroker_writer_settings(self):
        with mock.patch(
            'passport.backend.logbroker_client.takeout_tasks.'
            'handler.get_takeout_logbroker_writer',
        ) as mock_get_writer:
            self._make_handler()
        mock_get_writer.assert_called_once_with('takeout_tasks', '1.host.com', 3)

    def test_extract_ok(self):
        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(handler=handler, data=self._make_extract_data().SerializeToString())

        self.assert_xunistater_logged(
            dict(
                url='http://localhost:10307/xpush',
                method='POST',
                post_args=json.dumps(
                    {
                        'takeout_tasks.entries.server1.TakeoutRequest_dmmm': {
                            'value': 1,
                        },
                        'takeout_tasks.entries.total.TakeoutRequest_dmmm': {
                            'value': 1,
                        },
                    },
                    sort_keys=True,
                ),
            ),
        )

        self.assertEqual(len(self.logbroker_writer_faker.requests), 4)
        self.assertEqual(len(self.fake_passport.requests), 1)
        self.check_statbox_log()
        self.fake_sleep.assert_not_called()


class TestTakeoutSyncTaskHandler(_BaseTestTakeoutTaskHandler):
    def setUp(self):
        super(TestTakeoutSyncTaskHandler, self).setUp()

        self.builder_faker = FakeSyncServiceBuilder()
        self.builder_faker.start()

    def tearDown(self):
        self.builder_faker.stop()
        del self.builder_faker

        super(TestTakeoutSyncTaskHandler, self).tearDown()

    def test_sync_extract_ok(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,
        ])

        self.builder_faker.set_response_side_effect_without_method([
            service_ok_response(
                files={
                    'file1': 'content1',
                    'file2': 'content2',
                },
                file_links=[
                    'http://127.0.0.1/file3',
                    'http://127.0.0.1/file4',
                ],
            ),
            raw_file_response('file3', b'content3'),
            raw_file_response('file4', b'content4'),
        ])

        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_extract_service_data(service_name='alice_iot').SerializeToString(),
        )

        self.assertEqual(len(self.builder_faker.requests), 3)

        assert len(self.s3_faker.calls_by_method('put_object')) == 4
        expected_s3_folder = '%s/%s/%s/' % (TEST_UID, TEST_EXTRACT_ID, 'alice_iot')
        assert sorted([
            self.s3_faker.calls_by_method('put_object')[i]['Key']
            for i in range(4)
        ]) == [
            expected_s3_folder + 'file1.kv1',
            expected_s3_folder + 'file2.kv1',
            expected_s3_folder + 'file3.kv1',
            expected_s3_folder + 'file4.kv1',
        ]

        assert len(self.redis_faker.redis_calls_by_method('setex')) == 2
        self.touch_faker.assert_was_checked([TouchFiles.Sync.DONE])
        self.touch_faker.assert_is_set([
            TouchFiles.Sync.STARTED,
            TouchFiles.Sync.DONE,
        ])

    def test_retries_exceed(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,
        ])

        self.builder_faker.set_response_side_effect_without_method([
            service_ok_response(
                file_links=[
                    'http://127.0.0.1/file1',
                    'http://127.0.0.1/file2',
                ],
            ),
            raw_file_response('BAD_FILENAME', b'content1'),
        ])

        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_extract_service_data(
                service_name='alice_iot',
                retries=2,
                max_retries=2,
            ).SerializeToString(),
        )

        self.check_statbox_log(
            archive_requested_unixtime=str(TEST_UNIXTIME),
            error='ServicePermanentError',
            error_message="Got unacceptable filename 'BAD_FILENAME'",
            retries='2',
            service_name='alice_iot',
            status='failure',
            task_name='extract_service',
        )
        self.assertEqual(len(self.logbroker_writer_faker.requests), 0)

    def test_error_in_extract_task_implementation(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,
        ])

        self.builder_faker.set_response_side_effect_without_method([
            service_ok_response(
                file_links=[
                    'http://127.0.0.1/file1',
                    'http://127.0.0.1/file2',
                ],
            ),
            raw_file_response('BAD_FILENAME', b'content1'),
        ])

        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_extract_service_data(service_name='alice_iot', step='start').SerializeToString(),
        )

        self.check_statbox_log(
            archive_requested_unixtime=str(TEST_UNIXTIME),
            error='ServicePermanentError',
            error_message="Got unacceptable filename 'BAD_FILENAME'",
            retries='0',
            service_name='alice_iot',
            status='retry_failure',
            step='start',
            task_name='extract_service',
        )
        self.assertEqual(len(self.builder_faker.requests), 2)
        # заново поставили задачу в LB
        self.assertEqual(len(self.logbroker_writer_faker.requests), 1)


class TestTakeoutAsyncTaskHandler(_BaseTestTakeoutTaskHandler):
    def setUp(self):
        super(TestTakeoutAsyncTaskHandler, self).setUp()

        self.builder_faker = FakeAsyncServiceBuilder()
        self.builder_faker.start()

    def tearDown(self):
        self.builder_faker.stop()
        del self.builder_faker

        super(TestTakeoutAsyncTaskHandler, self).tearDown()

    def test_start_ok(self):
        self.builder_faker.set_response_value_without_method(
            service_ok_response(job_id=TEST_JOB_ID),
        )

        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_extract_service_data(service_name=TEST_SERVICE_NAME, step=TEST_STEP).SerializeToString(),
        )

        self.assertEqual(len(self.logbroker_writer_faker.requests), 1)

        self.assertEqual(len(self.builder_faker.requests), 1)
        self.builder_faker.requests[0].assert_properties_equal(
            url='https://ether-backend.yandex-team.ru/takeout',
            method='POST',
            post_args={
                'uid': TEST_UID,
                'unixtime': TEST_UNIXTIME,
            },
            headers=self.tvm_headers,
        )

        self.touch_faker.assert_is_set([
            TouchFiles.AsyncPoll.STARTED,
        ])

    def test_get_ok(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,
        ])

        self.builder_faker.set_response_side_effect_without_method([
            service_ok_response(
                files={
                    'file1': 'content1',
                    'file2': 'content2',
                },
                file_links=[
                    'http://127.0.0.1/file3',
                    'http://127.0.0.1/file4',
                ],
            ),
            raw_file_response('file3', b'content3'),
            raw_file_response('file4', b'content4'),
        ])

        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_extract_service_data(
                service_name=TEST_SERVICE_NAME,
                step='get',
                job_id=TEST_JOB_ID,
            ).SerializeToString(),
        )

        self.assertEqual(len(self.builder_faker.requests), 3)
        self.builder_faker.requests[0].assert_properties_equal(
            url='https://ether-backend.yandex-team.ru/takeout',
            method='POST',
            post_args={
                'job_id': TEST_JOB_ID,
            },
            headers=self.tvm_headers,
        )


class TestTakeoutAsyncUploadTaskHandler(_BaseTestTakeoutTaskHandler):
    def setUp(self):
        super(TestTakeoutAsyncUploadTaskHandler, self).setUp()

        self.builder_faker = FakeAsyncUploadServiceBuilder()
        self.builder_faker.start()

        self.test_service_name = 'corporate_blog'
        self.test_job_id = make_job_id_v1(TEST_UID, 'corporate_blog', TEST_EXTRACT_ID)

    def tearDown(self):
        self.builder_faker.stop()
        del self.builder_faker

        super(TestTakeoutAsyncUploadTaskHandler, self).tearDown()

    def test_start_ok_with_no_data(self):
        self.builder_faker.set_response_value_without_method(
            service_ok_response(status=STATUS_NO_DATA),
        )
        # флаги "выемка завершена" и "данные заказаны" не взведены
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
            self.touch_faker.State.UNSET,  # STARTED
        ])

        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_extract_service_data(
                service_name=self.test_service_name,
                step=TEST_STEP,
                job_id=self.test_job_id,
            ).SerializeToString(),
        )

        self.touch_faker.assert_is_set([
            TouchFiles.AsyncUpload.STARTED,
            TouchFiles.AsyncUpload.ORDERED_DATA,
            # при no_data проставляется этот флаг
            TouchFiles.AsyncUpload.DONE,
        ])
        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.DONE,
            TouchFiles.AsyncUpload.ORDERED_DATA,
        ])

        self.assertEqual(len(self.builder_faker.requests), 1)
        self.assertEqual(len(self.logbroker_writer_faker.requests), 1)

    def test_get_not_ready(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
        ])

        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_extract_service_data(
                service_name=self.test_service_name,
                step='get',
                job_id=self.test_job_id,
            ).SerializeToString(),
        )

        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.DONE,
        ])

        self.assertEqual(len(self.logbroker_writer_faker.requests), 1)


class TestTakeoutMakeArchiveHandler(_BaseTestTakeoutTaskHandler):
    def setUp(self):
        super(TestTakeoutMakeArchiveHandler, self).setUp()

        self.test_dir = TEST_DIR
        encrypted_file_content = encrypt_bytes(TEST_FILE_CONTENT)

        self.builder_faker = FakeAsyncServiceBuilder()
        self.builder_faker.start()

        self.s3_faker.set_response_side_effect(
            'list_objects',
            [
                s3_ok_response(
                    Contents=[
                        {
                            'Key': 'test_folder/1.jpg.kv1',
                            'Size': len(encrypted_file_content),
                        },
                    ],
                ),
                s3_ok_response(Contents=[]),
            ],
        )
        self.s3_faker.set_response_side_effect(
            'download_fileobj',
            lambda Bucket, Key, Fileobj: (
                Fileobj.write(encrypted_file_content),
                Fileobj.seek(0),
            ),
        )
        self.s3_faker.set_response_side_effect('head_object', ClientError({'Error': {'Code': '404'}}, ''))
        self.s3_faker.set_response_value('put_object', s3_ok_response())

        self.fake_passport.set_response_value('takeout_finish_extract', passport_ok_response())

        self.expected_archive_name = 'archive_%(extract_id)s_%(uid)s_%(ts)s.7z' % {
            'uid': TEST_UID,
            'extract_id': TEST_EXTRACT_ID,
            'ts': TEST_UNIXTIME,
        }
        self.expected_archive_filepath = '%(uid)s/%(extract_id)s/%(archive_name)s' % {
            'uid': TEST_UID,
            'extract_id': TEST_EXTRACT_ID,
            'archive_name': self.expected_archive_name,
        }

        def run_7z():
            with open(os.path.join(self.test_dir, self.expected_archive_filepath), 'w') as f:
                f.write('archive_content')
            return 'output', 'errors'

        self.random_patch = mock.patch('random.sample', mock.Mock(return_value=TEST_PASSWORD))
        self.random_patch.start()

        subprocess_mock = mock.MagicMock()
        subprocess_mock.poll.return_value = 0  # returncode
        subprocess_mock.communicate.side_effect = lambda *args, **kwargs: run_7z()
        subprocess_mock.__enter__.return_value = subprocess_mock
        self.popen_mock = mock.Mock(return_value=subprocess_mock)
        self.popen_patch = mock.patch('subprocess.Popen', self.popen_mock)
        self.popen_patch.start()

        self.shutil_move_mock = mock.Mock()
        self.shutil_move_patch = mock.patch('shutil.move', self.shutil_move_mock)
        self.shutil_move_patch.start()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

        self.shutil_move_patch.stop()
        self.popen_patch.stop()
        self.random_patch.stop()
        self.builder_faker.stop()

        del self.popen_patch
        del self.popen_mock
        del self.random_patch
        del self.builder_faker

        super(TestTakeoutMakeArchiveHandler, self).tearDown()

    def test_ok(self):
        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_data_for_make_archive(services=[]).SerializeToString(),
        )

        self.check_statbox_log(
            task_name='make_archive',
            cleanup_task_sent='1',
        )
        self.assertEqual(len(self.fake_passport.requests), 1)
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://passport.localhost/1/bundle/takeout/extract/finish/?consumer=takeout',
            post_args={
                'uid': TEST_UID,
                'archive_s3_key': 'res/%s' % self.expected_archive_filepath,
                'archive_password': TEST_PASSWORD,
            },
        )

        self.assertEqual(len(self.logbroker_writer_faker.requests), 1)

    def test_files_not_ready(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,
        ])

        self.builder_faker.set_response_value_without_method(
            service_ok_response(status=STATUS_PENDING),
        )

        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_data_for_make_archive(
                services=[TEST_SERVICE_NAME, ],
                retries=TEST_COUNT_FOR_FULL_CHECK,
            ).SerializeToString(),
        )

        self.check_statbox_log(
            archive_requested_unixtime=str(TEST_UNIXTIME),
            status='retry_later',
            error='ResponseNotReadyError',
            error_message='Services not ready: %s' % TEST_SERVICE_NAME,
            task_name='make_archive',
            retries=str(TEST_COUNT_FOR_FULL_CHECK),
        )


class TestTakeoutCleanupHandler(_BaseTestTakeoutTaskHandler):
    def setUp(self):
        super(TestTakeoutCleanupHandler, self).setUp()

        self.s3_faker.set_response_value(
            'delete_object',
            s3_ok_response(status=204),
        )
        self.s3_faker.set_response_side_effect(
            'list_objects',
            [
                s3_ok_response(
                    Contents=[
                        {
                            'Key': '%s/%s/passport/.takeout-touch/sync-started' % (TEST_UID, TEST_EXTRACT_ID),
                        },
                        {
                            'Key': '%s/%s/passport/1.jpg.kv1' % (TEST_UID, TEST_EXTRACT_ID),
                        },
                        {
                            'Key': '%s/%s/mail/2.jpg.kv1' % (TEST_UID, TEST_EXTRACT_ID),
                        },
                    ],
                ),
                s3_ok_response(
                    Contents=[
                        {
                            'Key': '%s/%s/disk/3.jpg.kv1' % (TEST_UID, TEST_EXTRACT_ID),
                        },
                    ],
                ),
                s3_ok_response(
                    Contents=[],
                ),
            ],
        )

    def test_ok(self):
        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_data_for_cleanup().SerializeToString(),
        )

        self.check_statbox_log(task_name='cleanup')
        self.assertEqual(len(self.s3_faker.calls_by_method('list_objects')), 3)

    def test_delay_ok(self):
        delay_until = int(TEST_NOW_TS) + TEST_DELAY_DELTA
        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_data_for_cleanup(delay_until=delay_until).SerializeToString(),
        )

        self.logbroker_writer_faker.assert_message_sent(
            self._make_data_for_cleanup(delay_until=delay_until, seq=1, source='delay'),
            as_dict=False,
        )
        self.fake_sleep.assert_called_once_with(TEST_DELAY_THROTTLING_MIN_EXEC_TIME)

    def test_delay_partial_throttle_ok(self):
        delay_until = int(TEST_NOW_TS) + TEST_DELAY_DELTA
        exec_end = TEST_NOW_TS + 0.1
        self.fake_time.side_effect = itertools.chain(
            itertools.repeat(TEST_NOW_TS, times=2),  # start_time, is_message_delayed()
            itertools.repeat(exec_end),
        )
        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_data_for_cleanup(delay_until=delay_until).SerializeToString(),
        )

        self.logbroker_writer_faker.assert_message_sent(
            self._make_data_for_cleanup(delay_until=delay_until, seq=1, source='delay'),
            as_dict=False,
        )
        assert len(self.fake_sleep.call_args_list) == 1
        assert abs(0.1 - self.fake_sleep.call_args_list[0][0][0]) < 0.001

    def test_delay_no_throttle_ok(self):
        delay_until = int(TEST_NOW_TS) + TEST_DELAY_DELTA
        exec_end = TEST_NOW_TS + TEST_DELAY_THROTTLING_MIN_EXEC_TIME
        self.fake_time.side_effect = itertools.chain(
            itertools.repeat(TEST_NOW_TS, times=2),  # start_time, is_message_delayed()
            itertools.repeat(exec_end),
        )
        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_data_for_cleanup(delay_until=delay_until).SerializeToString(),
        )

        self.logbroker_writer_faker.assert_message_sent(
            self._make_data_for_cleanup(delay_until=delay_until, seq=1, source='delay'),
            as_dict=False,
        )
        self.fake_sleep.assert_not_called()

    def test_expire_ok(self):
        unixtime = int(time.time()) - TEST_EXPIRE_DELTA
        handler = self._make_handler(push_metrics_to_xunistater=True)
        self.process(
            handler=handler,
            data=self._make_data_for_cleanup(unixtime=unixtime).SerializeToString(),
        )
        self.check_statbox_log(task_name='cleanup', status='expired', unixtime=unixtime, delay_until='0')
        self.assertEqual(len(self.logbroker_writer_faker.requests), 0)
