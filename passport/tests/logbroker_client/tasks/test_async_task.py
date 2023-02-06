# -*- coding: utf-8 -*-
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import TEST_ALIAS
from passport.backend.takeout.common.builders import (
    ServicePermanentError,
    STATUS_NO_DATA,
    STATUS_PENDING,
)
from passport.backend.takeout.common.exceptions import ResponseNotReadyError
from passport.backend.takeout.common.redis import get_redis
from passport.backend.takeout.common.touch import TouchFiles
from passport.backend.takeout.common.utils import make_redis_cache_key
from passport.backend.takeout.logbroker_client.tasks.async_task import (
    async_task_get,
    async_task_start,
)
from passport.backend.takeout.test_utils.base import BaseTestCase
from passport.backend.takeout.test_utils.fake_builders import (
    FakeAsyncServiceBuilder,
    raw_file_response,
    service_ok_response,
)
import pytest


TEST_UID = 1
TEST_EXTRACT_ID = '123'
TEST_SERVICE = 'sq2'
TEST_UNIXTIME = 123456789
TEST_JOB_ID = 'job-321'


class AsyncTaskTestCase(BaseTestCase):
    def setUp(self):
        super(AsyncTaskTestCase, self).setUp()

        self.builder_faker = FakeAsyncServiceBuilder()
        self.builder_faker.start()

    def tearDown(self):
        self.builder_faker.stop()
        del self.builder_faker

        super(AsyncTaskTestCase, self).tearDown()

    @property
    def conf(self):
        return {
            'builders': {},
            'services': {
                TEST_SERVICE: {
                    'enabled': True,
                    'type': 'async',
                    'tvm_dst_alias': TEST_ALIAS,
                    'urls': {
                        'base': 'http://localhost/',
                        'suffix_start': '/start',
                        'suffix_get': 'get',
                    },
                    'timeout': 1,
                    'retries': 3,
                },
            },
        }

    def test_start_ok(self):
        self.builder_faker.set_response_value_without_method(
            service_ok_response(job_id=TEST_JOB_ID),
        )
        job_id = async_task_start(
            uid=TEST_UID,
            extract_id=TEST_EXTRACT_ID,
            service_name=TEST_SERVICE,
            unixtime=TEST_UNIXTIME,
            conf=self.conf,
        )
        assert job_id == TEST_JOB_ID
        assert len(self.builder_faker.requests) == 1
        self.builder_faker.requests[0].assert_properties_equal(
            url='http://localhost/start',
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

    def test_start_no_data_ok(self):
        self.builder_faker.set_response_value_without_method(
            service_ok_response(status=STATUS_NO_DATA),
        )
        job_id = async_task_start(
            uid=TEST_UID,
            extract_id=TEST_EXTRACT_ID,
            service_name=TEST_SERVICE,
            unixtime=TEST_UNIXTIME,
            conf=self.conf,
        )
        assert job_id is None
        assert len(self.builder_faker.requests) == 1
        self.builder_faker.requests[0].assert_properties_equal(
            url='http://localhost/start',
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
            self.touch_faker.State.UNSET,  # DONE
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

        async_task_get(
            uid=TEST_UID,
            extract_id=TEST_EXTRACT_ID,
            service_name=TEST_SERVICE,
            job_id=TEST_JOB_ID,
            conf=self.conf,
        )

        assert len(self.builder_faker.requests) == 3
        self.builder_faker.requests[0].assert_properties_equal(
            url='http://localhost/get',
            method='POST',
            post_args={
                'job_id': TEST_JOB_ID,
            },
            headers=self.tvm_headers,
        )
        self.builder_faker.requests[1].assert_properties_equal(
            url='http://127.0.0.1/file3',
            method='GET',
            headers=self.tvm_headers,
        )
        self.builder_faker.requests[2].assert_properties_equal(
            url='http://127.0.0.1/file4',
            method='GET',
            headers=self.tvm_headers,
        )
        assert len(self.s3_faker.calls_by_method('put_object')) == 4
        expected_s3_folder = '%s/%s/%s/' % (TEST_UID, TEST_EXTRACT_ID, TEST_SERVICE)
        assert sorted([
            self.s3_faker.calls_by_method('put_object')[i]['Key']
            for i in range(4)
        ]) == [
            expected_s3_folder + 'file1.kv1',
            expected_s3_folder + 'file2.kv1',
            expected_s3_folder + 'file3.kv1',
            expected_s3_folder + 'file4.kv1',
        ]

        redis_key = make_redis_cache_key(TEST_UID, TEST_EXTRACT_ID, TEST_SERVICE)
        assert get_redis().smembers(redis_key) == {b'http://127.0.0.1/file3', b'http://127.0.0.1/file4'}

        assert len(self.fake_redis.redis_calls_by_method('setex')) == 1
        self.touch_faker.assert_is_set([
            TouchFiles.AsyncPoll.DONE,
        ])

    def test_get_file_links_already_downloaded(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
        ])

        redis_key = make_redis_cache_key(TEST_UID, TEST_EXTRACT_ID, TEST_SERVICE)
        get_redis().sadd(redis_key, 'http://127.0.0.1/file3', 'http://127.0.0.1/file4')

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
        ])

        async_task_get(
            uid=TEST_UID,
            extract_id=TEST_EXTRACT_ID,
            service_name=TEST_SERVICE,
            job_id=TEST_JOB_ID,
            conf=self.conf,
        )

        assert len(self.builder_faker.requests) == 1
        self.builder_faker.requests[0].assert_properties_equal(
            url='http://localhost/get',
            method='POST',
            post_args={
                'job_id': TEST_JOB_ID,
            },
            headers=self.tvm_headers,
        )
        assert len(self.s3_faker.calls_by_method('put_object')) == 2
        expected_s3_folder = '%s/%s/%s/' % (TEST_UID, TEST_EXTRACT_ID, TEST_SERVICE)
        assert sorted([
            self.s3_faker.calls_by_method('put_object')[i]['Key']
            for i in range(2)
        ]) == [
            expected_s3_folder + 'file1.kv1',
            expected_s3_folder + 'file2.kv1',
        ]

        assert len(self.fake_redis.redis_calls_by_method('setex')) == 1
        self.touch_faker.assert_is_set([
            TouchFiles.AsyncPoll.DONE,
        ])

    def test_bad_file_content(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
        ])

        self.builder_faker.set_response_side_effect_without_method([
            service_ok_response(
                files={
                    'file': 10,  # это не строка, поэтому ругнёмся
                },
            ),
        ])

        with pytest.raises(ServicePermanentError):
            async_task_get(
                uid=TEST_UID,
                extract_id=TEST_EXTRACT_ID,
                service_name=TEST_SERVICE,
                job_id=TEST_JOB_ID,
                conf=self.conf,
            )

        assert len(self.builder_faker.requests) == 1

    def test_get_bad_filename_inplace(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
        ])

        self.builder_faker.set_response_side_effect_without_method([
            service_ok_response(
                files={
                    'FILE1': 'content1',
                },
            ),
        ])

        with pytest.raises(ServicePermanentError):
            async_task_get(
                uid=TEST_UID,
                extract_id=TEST_EXTRACT_ID,
                service_name=TEST_SERVICE,
                job_id=TEST_JOB_ID,
                conf=self.conf,
            )

        assert len(self.builder_faker.requests) == 1

    def test_get_bad_filename_in_filelinks(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
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

        with pytest.raises(ServicePermanentError):
            async_task_get(
                uid=TEST_UID,
                extract_id=TEST_EXTRACT_ID,
                service_name=TEST_SERVICE,
                job_id=TEST_JOB_ID,
                conf=self.conf,
            )

        assert len(self.builder_faker.requests) == 2

    def test_get_no_data(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
        ])

        self.builder_faker.set_response_value_without_method(
            service_ok_response(status=STATUS_NO_DATA),
        )
        async_task_get(
            uid=TEST_UID,
            extract_id=TEST_EXTRACT_ID,
            service_name=TEST_SERVICE,
            job_id=TEST_JOB_ID,
            conf=self.conf,
        )
        assert len(self.builder_faker.requests) == 1
        self.touch_faker.assert_is_set([
            TouchFiles.AsyncPoll.DONE,
        ])

        assert len(self.fake_redis.redis_calls_by_method('setex')) == 1
        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncPoll.DONE,
        ])

    def test_get_no_data_from_start(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
        ])

        async_task_get(
            uid=TEST_UID,
            extract_id=TEST_EXTRACT_ID,
            service_name=TEST_SERVICE,
            job_id=None,  # no_data на этапе start
            conf=self.conf,
        )
        assert len(self.builder_faker.requests) == 0

        self.touch_faker.assert_is_set([
            TouchFiles.AsyncPoll.DONE,
        ])
        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncPoll.DONE,
        ])

    def test_get_pending(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
        ])

        self.builder_faker.set_response_value_without_method(
            service_ok_response(status=STATUS_PENDING),
        )
        with pytest.raises(ResponseNotReadyError):
            async_task_get(
                uid=TEST_UID,
                extract_id=TEST_EXTRACT_ID,
                service_name=TEST_SERVICE,
                job_id=TEST_JOB_ID,
                conf=self.conf,
            )

        assert len(self.builder_faker.requests) == 1
        assert not self.s3_faker.calls_by_method('put_object')

        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncPoll.DONE,
        ])
