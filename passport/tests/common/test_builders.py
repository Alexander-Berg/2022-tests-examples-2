# -*- coding: utf-8 -*-
import json
import unittest

import mock
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_ALIAS,
)
from passport.backend.takeout.common.builders import (
    AsyncServiceBuilder,
    AsyncUploadServiceBuilder,
    ServiceTemporaryError,
    STATUS_NO_DATA,
    STATUS_PENDING,
    SyncServiceBuilder,
)
from passport.backend.takeout.common.exceptions import (
    ResponseNotReadyError,
    ServicePermanentError,
)
from passport.backend.takeout.test_utils.fake_builders import (
    FakeAsyncServiceBuilder,
    FakeAsyncUploadServiceBuilder,
    FakeSyncServiceBuilder,
    raw_file_response,
    service_error_response,
    service_ok_response,
)
import pytest


TEST_UID = 123
TEST_TS = 123456789
TEST_JOB_ID = 'job-321'


class BaseServiceBuilderTestCase(unittest.TestCase):
    service_type = None
    builder_class = None

    def setUp(self):
        self.tvm_faker = FakeTvmCredentialsManager()
        self.tvm_faker.start()
        self.tvm_faker.set_data(fake_tvm_credentials_data())

        self.builder = self.builder_class(service_name=self.service_name, conf=self.conf)

    def tearDown(self):
        self.tvm_faker.stop()
        del self.tvm_faker
        del self.builder

    @property
    def service_name(self):
        return 'some_%s_service' % self.service_type

    @property
    def conf(self):
        return {
            'builders': {},
            'services': {
                self.service_name: {
                    'enabled': True,
                    'type': self.service_type,
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


class TestServiceBuilderCommon(BaseServiceBuilderTestCase):
    service_type = 'sync'
    builder_class = SyncServiceBuilder

    def setUp(self):
        super(TestServiceBuilderCommon, self).setUp()

        self.builder.useragent = mock.Mock()
        self.builder.useragent.request_error_class = Exception

        self.response = mock.Mock()
        self.builder.useragent.request.return_value = self.response
        self.response.content = service_ok_response()
        self.response.status_code = 200

    def tearDown(self):
        del self.response
        super(TestServiceBuilderCommon, self).tearDown()

    def test_failed_to_parse_response(self):
        self.response.status_code = 400
        self.response.content = b'not a json'
        with pytest.raises(ServiceTemporaryError):
            self.builder.get_info(uid=TEST_UID, unixtime=TEST_TS)

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = b'"server is down"'
        with pytest.raises(ServiceTemporaryError):
            self.builder.get_info(uid=TEST_UID, unixtime=TEST_TS)

    def test_service_error(self):
        self.response.status_code = 200
        self.response.content = service_error_response(error='backend.failed')
        with pytest.raises(ServiceTemporaryError):
            self.builder.get_info(uid=TEST_UID, unixtime=TEST_TS)

    def test_unknown_service(self):
        with pytest.raises(ValueError):
            self.builder_class(service_name='foo', conf=self.conf)

    def test_bad_service_type(self):
        with pytest.raises(ValueError):
            AsyncServiceBuilder(service_name=self.service_name, conf=self.conf)


class TestSyncServiceBuilder(BaseServiceBuilderTestCase):
    service_type = 'sync'
    builder_class = SyncServiceBuilder

    def setUp(self):
        super(TestSyncServiceBuilder, self).setUp()

        self.faker = FakeSyncServiceBuilder()
        self.faker.start()
        self.faker.set_response_value_without_method(service_ok_response())

    def tearDown(self):
        self.faker.stop()
        del self.faker
        super(TestSyncServiceBuilder, self).tearDown()

    def test_get__ok(self):
        self.faker.set_response_value_without_method(service_ok_response(files={'foo': 'bar'}))
        response = self.builder.get_info(uid=TEST_UID, unixtime=TEST_TS)
        assert response == json.loads(service_ok_response(files={'foo': 'bar'}))
        self.faker.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/get',
            post_args={
                'uid': TEST_UID,
                'unixtime': TEST_TS,
            },
        )

    def test_get__no_data_or_filelinks(self):
        self.faker.set_response_value_without_method(service_ok_response())
        with pytest.raises(ServicePermanentError):
            self.builder.get_info(uid=TEST_UID, unixtime=TEST_TS)

    def test_get__invalid_response_status(self):
        self.faker.set_response_value_without_method(service_ok_response(status='null'))

        with pytest.raises(ServicePermanentError):
            self.builder.get_info(uid=TEST_UID, unixtime=TEST_TS)

    def test_get_from_url__ok_unquoted_filename(self):
        self.faker.set_response_value_without_method(raw_file_response(file_name='filename.jpg', content=b'secret'))

        file_name, file_object = self.builder.get_info_from_url(custom_url='https://drive.google.com/file')
        assert file_name == 'filename.jpg'
        assert file_object.read() == b'secret'
        self.faker.requests[0].assert_properties_equal(
            method='GET',
            url='https://drive.google.com/file',
        )

    def test_get_from_url__ok_filename_is_quoted(self):
        self.faker.set_response_value_without_method(raw_file_response(file_name='"filename.jpg"', content=b'secret'))

        file_name, file_object = self.builder.get_info_from_url(custom_url='https://drive.google.com/file')
        assert file_name == 'filename.jpg'
        assert file_object.read() == b'secret'
        self.faker.requests[0].assert_properties_equal(
            method='GET',
            url='https://drive.google.com/file',
        )

    def test_get_from_url__ok_filename_is_quoted_with_trailing_parameter(self):
        self.faker.set_response_value_without_method(raw_file_response(file_name='"filename.jpg"; foo=bar', content=b'secret'))

        file_name, file_object = self.builder.get_info_from_url(custom_url='https://drive.google.com/file')
        assert file_name == 'filename.jpg'
        assert file_object.read() == b'secret'
        self.faker.requests[0].assert_properties_equal(
            method='GET',
            url='https://drive.google.com/file',
        )

    def test_get_from_url__no_content_disposition_header(self):
        with pytest.raises(ServicePermanentError):
            self.builder.get_info_from_url(custom_url='https://drive.google.com/file')

    def test_get_from_url_malformed_content_disposition_header(self):
        self.faker.set_response_value_without_method(
            raw_file_response(file_name='filename.jpg', content=b'secret', content_disposition='malformed'),
        )

        with pytest.raises(ServicePermanentError):
            self.builder.get_info_from_url(custom_url='https://drive.google.com/file')


class TestAsyncServiceBuilder(BaseServiceBuilderTestCase):
    service_type = 'async'
    builder_class = AsyncServiceBuilder

    def setUp(self):
        super(TestAsyncServiceBuilder, self).setUp()

        self.faker = FakeAsyncServiceBuilder()
        self.faker.start()
        self.faker.set_response_value_without_method(service_ok_response())

    def tearDown(self):
        self.faker.stop()
        del self.faker
        super(TestAsyncServiceBuilder, self).tearDown()

    def test_start__ok(self):
        self.faker.set_response_value_without_method(service_ok_response(job_id=TEST_JOB_ID))

        response = self.builder.start(uid=TEST_UID, unixtime=TEST_TS)
        assert response == json.loads(service_ok_response(job_id=TEST_JOB_ID))
        self.faker.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/start',
            post_args={
                'uid': TEST_UID,
                'unixtime': TEST_TS,
            },
        )

    def test_start_no_data__ok(self):
        self.faker.set_response_value_without_method(service_ok_response(status=STATUS_NO_DATA))

        response = self.builder.start(uid=TEST_UID, unixtime=TEST_TS)
        assert response == json.loads(service_ok_response(status=STATUS_NO_DATA))
        self.faker.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/start',
            post_args={
                'uid': TEST_UID,
                'unixtime': TEST_TS,
            },
        )

    def test_start__invalid_response_status(self):
        self.faker.set_response_value_without_method(service_ok_response(status='null'))

        with pytest.raises(ServicePermanentError):
            self.builder.start(uid=TEST_UID, unixtime=TEST_TS)

    def test_start__no_job_id_in_response(self):
        with pytest.raises(ServicePermanentError):
            self.builder.start(uid=TEST_UID, unixtime=TEST_TS)

    def test_start__empty_job_id_in_response(self):
        self.faker.set_response_value_without_method(service_ok_response(job_id=''))

        with pytest.raises(ServicePermanentError):
            self.builder.start(uid=TEST_UID, unixtime=TEST_TS)

    def test_get__ok(self):
        self.faker.set_response_value_without_method(service_ok_response(files={'foo': 'bar'}))
        response = self.builder.get_info(job_id=TEST_JOB_ID)
        assert response == json.loads(service_ok_response(files={'foo': 'bar'}))
        self.faker.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/get',
            post_args={
                'job_id': TEST_JOB_ID,
            },
        )

    def test_get__no_data_or_filelinks(self):
        self.faker.set_response_value_without_method(service_ok_response())
        with pytest.raises(ServicePermanentError):
            self.builder.get_info(job_id=TEST_JOB_ID)

    def test_get_pending(self):
        self.faker.set_response_value_without_method(service_ok_response(status=STATUS_PENDING))

        with pytest.raises(ResponseNotReadyError):
            self.builder.get_info(job_id=TEST_JOB_ID)

    def test_get__invalid_response_status(self):
        self.faker.set_response_value_without_method(service_ok_response(status='null'))

        with pytest.raises(ServicePermanentError):
            self.builder.get_info(job_id=TEST_JOB_ID)

    def test_get_from_url__ok_unquoted_filename(self):
        self.faker.set_response_value_without_method(raw_file_response(file_name='filename.jpg', content=b'secret'))

        file_name, file_object = self.builder.get_info_from_url(custom_url='https://drive.google.com/file')
        assert file_name == 'filename.jpg'
        assert file_object.read() == b'secret'
        self.faker.requests[0].assert_properties_equal(
            method='GET',
            url='https://drive.google.com/file',
        )

    def test_get_from_url__ok_filename_is_quoted(self):
        self.faker.set_response_value_without_method(raw_file_response(file_name='"filename.jpg"', content=b'secret'))

        file_name, file_object = self.builder.get_info_from_url(custom_url='https://drive.google.com/file')
        assert file_name == 'filename.jpg'
        assert file_object.read() == b'secret'
        self.faker.requests[0].assert_properties_equal(
            method='GET',
            url='https://drive.google.com/file',
        )

    def test_get_from_url__ok_filename_is_quoted_with_trailing_parameter(self):
        self.faker.set_response_value_without_method(raw_file_response(file_name='"filename.jpg"; foo=bar', content=b'secret'))

        file_name, file_object = self.builder.get_info_from_url(custom_url='https://drive.google.com/file')
        assert file_name == 'filename.jpg'
        assert file_object.read() == b'secret'
        self.faker.requests[0].assert_properties_equal(
            method='GET',
            url='https://drive.google.com/file',
        )

    def test_get_from_url__no_content_disposition_header(self):
        with pytest.raises(ServicePermanentError):
            self.builder.get_info_from_url(custom_url='https://drive.google.com/file')

    def test_get_from_url_malformed_content_disposition_header(self):
        self.faker.set_response_value_without_method(
            raw_file_response(file_name='filename.jpg', content=b'secret', content_disposition='malformed'),
        )

        with pytest.raises(ServicePermanentError):
            self.builder.get_info_from_url(custom_url='https://drive.google.com/file')


class TestAsyncUploadServiceBuilder(BaseServiceBuilderTestCase):
    service_type = 'async_upload'
    builder_class = AsyncUploadServiceBuilder

    def setUp(self):
        super(TestAsyncUploadServiceBuilder, self).setUp()

        self.faker = FakeAsyncUploadServiceBuilder()
        self.faker.start()
        self.faker.set_response_value_without_method(service_ok_response())

    def tearDown(self):
        self.faker.stop()
        del self.faker
        super(TestAsyncUploadServiceBuilder, self).setUp()

    def test_start__ok(self):
        response = self.builder.start(uid=TEST_UID, unixtime=TEST_TS, job_id=TEST_JOB_ID)
        assert response == json.loads(service_ok_response())
        self.faker.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/start',
            post_args={
                'uid': TEST_UID,
                'unixtime': TEST_TS,
                'job_id': TEST_JOB_ID,
            },
        )

    def test_start__invalid_response_status(self):
        self.faker.set_response_value_without_method(service_ok_response(status='null'))

        with pytest.raises(ServicePermanentError):
            self.builder.start(uid=TEST_UID, unixtime=TEST_TS, job_id=TEST_JOB_ID)
