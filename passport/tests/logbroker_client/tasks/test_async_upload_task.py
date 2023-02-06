# -*- coding: utf-8 -*-
import mock
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import TEST_ALIAS
from passport.backend.takeout.common.builders import STATUS_NO_DATA
from passport.backend.takeout.common.exceptions import (
    ResponseNotReadyError,
    ServicePermanentError,
)
from passport.backend.takeout.common.job_id import make_job_id_v1
from passport.backend.takeout.common.touch import TouchFiles
from passport.backend.takeout.logbroker_client.tasks.async_upload_task import (
    async_upload_task_get,
    async_upload_task_start,
)
from passport.backend.takeout.test_utils.base import BaseTestCase
from passport.backend.takeout.test_utils.fake_builders import (
    FakeAsyncUploadServiceBuilder,
    service_ok_response,
)
import pytest


TEST_UID = 1
TEST_EXTRACT_ID = '123'
TEST_SERVICE = 'sq2'
TEST_UNIXTIME = 123456789


class AsyncUploadTaskTestCase(BaseTestCase):
    def setUp(self):
        super(AsyncUploadTaskTestCase, self).setUp()
        self.builder_faker = FakeAsyncUploadServiceBuilder()
        self.builder_faker.start()

        self.test_job_id = make_job_id_v1(TEST_UID, TEST_SERVICE, TEST_EXTRACT_ID)

    def tearDown(self):
        self.builder_faker.stop()
        del self.builder_faker
        super(AsyncUploadTaskTestCase, self).tearDown()

    @property
    def conf(self):
        return {
            'builders': {},
            'services': {
                TEST_SERVICE: {
                    'enabled': True,
                    'type': 'async_upload',
                    'tvm_dst_alias': TEST_ALIAS,
                    'urls': {
                        'base': 'http://localhost/',
                        'suffix_start': '/start',
                    },
                    'timeout': 1,
                    'retries': 3,
                },
            },
        }

    def test_start_ok(self):
        self.builder_faker.set_response_value_without_method(
            service_ok_response(),
        )
        # флаги "выемка завершена" и "данные заказаны" не взведены
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
            self.touch_faker.State.UNSET,  # STARTED
        ])

        async_upload_task_start(
            job_id=self.test_job_id,
            uid=TEST_UID,
            extract_id=TEST_EXTRACT_ID,
            service_name=TEST_SERVICE,
            unixtime=TEST_UNIXTIME,
            statbox=mock.Mock(),
            conf=self.conf,
        )

        self.touch_faker.assert_is_set([
            TouchFiles.AsyncUpload.STARTED,
            TouchFiles.AsyncUpload.ORDERED_DATA,
        ])
        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.DONE,
            TouchFiles.AsyncUpload.ORDERED_DATA,
        ])

        assert len(self.builder_faker.requests) == 1
        self.builder_faker.requests[0].assert_properties_equal(
            url='http://localhost/start',
            method='POST',
            post_args={
                'uid': TEST_UID,
                'unixtime': TEST_UNIXTIME,
                'job_id': self.test_job_id,
            },
            headers=self.tvm_headers,
        )

    def test_start_no_data_ok(self):
        self.builder_faker.set_response_value_without_method(
            service_ok_response(status=STATUS_NO_DATA),
        )
        # флаги "выемка завершена" и "данные заказаны" не взведены
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
            self.touch_faker.State.UNSET,  # STARTED
        ])

        async_upload_task_start(
            job_id=self.test_job_id,
            uid=TEST_UID,
            extract_id=TEST_EXTRACT_ID,
            service_name=TEST_SERVICE,
            unixtime=TEST_UNIXTIME,
            statbox=mock.Mock(),
            conf=self.conf,
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

        assert len(self.builder_faker.requests) == 1
        self.builder_faker.requests[0].assert_properties_equal(
            url='http://localhost/start',
            method='POST',
            post_args={
                'uid': TEST_UID,
                'unixtime': TEST_UNIXTIME,
                'job_id': self.test_job_id,
            },
            headers=self.tvm_headers,
        )

    def test_start_already_done(self):
        self.builder_faker.set_response_value_without_method(
            service_ok_response(),
        )

        async_upload_task_start(
            job_id=self.test_job_id,
            uid=TEST_UID,
            extract_id=TEST_EXTRACT_ID,
            service_name=TEST_SERVICE,
            unixtime=TEST_UNIXTIME,
            statbox=mock.Mock(),
            conf=self.conf,
        )

        self.touch_faker.assert_is_set([])
        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.DONE,
        ])

        assert len(self.builder_faker.requests) == 0

    def test_start_already_ordered_data(self):
        self.builder_faker.set_response_value_without_method(
            service_ok_response(),
        )

        # флаги "выемка завершена" не взведён
        # флаг "данные заказаны" взведён
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
            self.touch_faker.State.SET,  # ORDERED_DATA
        ])

        async_upload_task_start(
            job_id=self.test_job_id,
            uid=TEST_UID,
            extract_id=TEST_EXTRACT_ID,
            service_name=TEST_SERVICE,
            unixtime=TEST_UNIXTIME,
            statbox=mock.Mock(),
            conf=self.conf,
        )

        self.touch_faker.assert_is_set([])
        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.DONE,
            TouchFiles.AsyncUpload.ORDERED_DATA,
        ])

        assert len(self.builder_faker.requests) == 0

    def test_start_third_party_service_is_down(self):
        self.builder_faker.set_response_side_effect_without_method(ServicePermanentError('error'))

        # флаги "выемка завершена" и "данные заказаны" не взведены
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
            self.touch_faker.State.UNSET,  # ORDERED_DATA
        ])

        with pytest.raises(ServicePermanentError):
            async_upload_task_start(
                job_id=self.test_job_id,
                uid=TEST_UID,
                extract_id=TEST_EXTRACT_ID,
                service_name=TEST_SERVICE,
                unixtime=TEST_UNIXTIME,
                statbox=mock.Mock(),
                conf=self.conf,
            )

        self.touch_faker.assert_is_set([
            TouchFiles.AsyncUpload.STARTED,
        ])

        # была проверка на завершённость выгрузки
        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.DONE,
            TouchFiles.AsyncUpload.ORDERED_DATA,
        ])

        assert len(self.builder_faker.requests) == 1
        self.builder_faker.requests[0].assert_properties_equal(
            url='http://localhost/start',
            method='POST',
            post_args={
                'uid': TEST_UID,
                'unixtime': TEST_UNIXTIME,
                'job_id': self.test_job_id,
            },
            headers=self.tvm_headers,
        )

    def test_get_ok(self):
        async_upload_task_get(
            uid=TEST_UID,
            extract_id=TEST_EXTRACT_ID,
            service_name=TEST_SERVICE,
        )

        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.DONE,
        ])

    def test_get_not_ready(self):
        """Флаг ORDERED_DATA не взводится, т.к. не удалось достучаться до стороннего сервиса"""
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
        ])

        with pytest.raises(ResponseNotReadyError):
            async_upload_task_get(
                uid=TEST_UID,
                extract_id=TEST_EXTRACT_ID,
                service_name=TEST_SERVICE,
            )

        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.DONE,
        ])
