# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.tvm import (
    TVM,
    TVM_STATUS_INVALID_CREDENTIALS,
    TVM_STATUS_OK,
    TVM_STATUS_TEMPORARY_ERROR,
    TVMPermanentError,
    TVMTemporaryError,
)
from passport.backend.core.builders.tvm.faker import (
    FakeTVM,
    tvm_error_response,
    tvm_ok_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


TEST_UID = 123
TEST_CYRILLIC_LOGIN = u'логин'


@with_settings(
    TVM_URL='http://localhost/',
    TVM_TIMEOUT=1,
    TVM_RETRIES=2,
)
class TestTVMCommon(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.start()

        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'tvm_api',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )

        self.tvm = TVM()
        self.tvm.useragent = mock.Mock()

        self.response = mock.Mock()
        self.tvm.useragent.request_error_class = TVMTemporaryError
        self.tvm.useragent.request.return_value = self.response

        self.response.content = tvm_ok_response()
        self.response.status_code = 200

    def tearDown(self):
        del self.tvm
        del self.response
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_failed_to_parse_response(self):
        self.response.status_code = 400
        self.response.content = b'not a json'
        with assert_raises(TVMPermanentError):
            self.tvm.verify_ssh(
                uid=TEST_UID,
                string_to_sign='foo',
                signed_string='bar',
            )

    def test_server_temporary_error(self):
        self.response.status_code = 400
        self.response.content = tvm_error_response(status=TVM_STATUS_TEMPORARY_ERROR)
        with assert_raises(TVMTemporaryError):
            self.tvm.verify_ssh(
                uid=TEST_UID,
                string_to_sign='foo',
                signed_string='bar',
            )

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = b'"server is down"'
        with assert_raises(TVMPermanentError):
            self.tvm.verify_ssh(
                uid=TEST_UID,
                string_to_sign='foo',
                signed_string='bar',
            )

    def test_default_initialization(self):
        tvm = TVM()
        ok_(tvm.useragent is not None)
        eq_(tvm.url, 'http://localhost/')


@with_settings(
    TVM_URL='http://localhost/',
    TVM_TIMEOUT=1,
    TVM_RETRIES=2,
)
class TestTVMMethods(unittest.TestCase):
    def setUp(self):
        self.fake_tvm = FakeTVM()
        self.fake_tvm.start()
        self.fake_tvm.set_response_value('verify_ssh', tvm_ok_response(message=json.dumps({'status': TVM_STATUS_OK})))

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.start()

        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'tvm_api',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )

        self.tvm = TVM()

    def tearDown(self):
        self.fake_tvm.stop()
        del self.fake_tvm
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_verify_ssh_ok(self):
        response = self.tvm.verify_ssh(
            uid=TEST_UID,
            string_to_sign='foo',
            signed_string='bar',
        )
        eq_(
            response,
            {'status': TVM_STATUS_OK},
        )
        self.fake_tvm.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/2/verify_ssh',
        )
        self.fake_tvm.requests[0].assert_post_data_contains(
            dict(
                uid=TEST_UID,
                to_sign='foo',
                ssh_sign='bar',
            ),
        )

    def test_verify_ssh_by_login_ok(self):
        response = self.tvm.verify_ssh(
            login=TEST_CYRILLIC_LOGIN,
            string_to_sign='foo',
            signed_string='bar',
        )
        eq_(
            response,
            {'status': TVM_STATUS_OK},
        )
        self.fake_tvm.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/2/verify_ssh',
        )
        self.fake_tvm.requests[0].assert_post_data_contains(
            dict(
                login=TEST_CYRILLIC_LOGIN,
                to_sign='foo',
                ssh_sign='bar',
            ),
        )

    def test_verify_ssh_with_optional_params_ok(self):
        response = self.tvm.verify_ssh(
            uid=TEST_UID,
            string_to_sign='foo',
            signed_string='bar',
            public_cert='zar',
        )
        eq_(
            response,
            {'status': TVM_STATUS_OK},
        )
        self.fake_tvm.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/2/verify_ssh',
        )
        self.fake_tvm.requests[0].assert_post_data_contains(
            dict(
                uid=TEST_UID,
                to_sign='foo',
                ssh_sign='bar',
                public_cert='zar',
            ),
        )

    def test_verify_ssh_failed(self):
        self.fake_tvm.set_response_value(
            'verify_ssh',
            json.dumps(tvm_error_response(status=TVM_STATUS_INVALID_CREDENTIALS, error='BB_REJECT')),
            status=400,
        )
        response = self.tvm.verify_ssh(
            uid=TEST_UID,
            string_to_sign='foo',
            signed_string='bar',
        )
        eq_(
            response,
            {
                'status': TVM_STATUS_INVALID_CREDENTIALS,
                'error': 'BB_REJECT',
                'desc': 'Something went wrong',
            },
        )

    @raises(ValueError)
    def test_verify_ssh_uid_and_login_missing(self):
        self.tvm.verify_ssh(
            string_to_sign='foo',
            signed_string='bar',
        )

    def test_verify_ssh_error(self):
        self.fake_tvm.set_response_value(
            'verify_ssh',
            json.dumps(tvm_error_response('INCORRECT.ts')),
            status=400,
        )
        with assert_raises(TVMPermanentError):
            self.tvm.verify_ssh(
                uid=TEST_UID,
                string_to_sign='foo',
                signed_string='bar',
            )
