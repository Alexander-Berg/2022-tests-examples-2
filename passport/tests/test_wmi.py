# -*- coding: utf-8 -*-

import json
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.mail_apis import (
    WMI,
    WMIInvalidResponseError,
    WMITemporaryError,
)
from passport.backend.core.builders.mail_apis.faker import (
    FakeWMI,
    wmi_folders_item,
    wmi_folders_response,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.useragent.sync import RequestError


TEST_UID = 1
TEST_SUID = 2
TEST_MDB = 'pg'
WMI_ERROR_RESPONSE = '''{"error":{"code":0,"message":"Unknown error","reason":"reason"}}'''


@with_settings_hosts(
    WMI_API_URL='http://localhost/',
    WMI_API_RETRIES=10,
    WMI_API_TIMEOUT=1,
)
class TestWMI(TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'wmi_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.wmi = WMI()

        self.fake_wmi = FakeWMI()
        self.fake_wmi.start()

        self.methods = [
            ('folders', self.wmi.folders),
        ]

    def tearDown(self):
        self.fake_wmi.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager
        del self.fake_wmi
        del self.wmi
        del self.methods

    def test_folders(self):
        response = wmi_folders_response([wmi_folders_item()])
        self.fake_wmi.set_response_value(
            'folders',
            response,
        )

        addresses = self.wmi.folders(TEST_UID, TEST_SUID, TEST_MDB)

        eq_(addresses, json.loads(response))

        requests = self.fake_wmi.requests
        eq_(len(requests), 1)
        requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/folders?uid=%s&suid=%s&mdb=%s' % (TEST_UID, TEST_SUID, TEST_MDB),
            headers={
                'X-Ya-Service-Ticket': TEST_TICKET,
            },
        )

    def test_retries_error(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_wmi.set_response_side_effect(method_name, RequestError)
            with assert_raises(WMITemporaryError):
                method(TEST_UID, TEST_SUID, TEST_MDB)
        eq_(len(self.fake_wmi.requests), 10 * (i + 1))

    def test_bad_status_code(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_wmi.set_response_value(method_name, b'{}', status=500)
            with assert_raises(WMIInvalidResponseError):
                method(TEST_UID, TEST_SUID, TEST_MDB)
        eq_(len(self.fake_wmi.requests), i + 1)

    def test_error_in_response(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_wmi.set_response_value(method_name, WMI_ERROR_RESPONSE)
            with assert_raises(WMIInvalidResponseError):
                method(TEST_UID, TEST_SUID, TEST_MDB)
        eq_(len(self.fake_wmi.requests), i + 1)

    def test_invalid_json(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_wmi.set_response_value(method_name, b'invalid json')
            with assert_raises(WMIInvalidResponseError):
                method(TEST_UID, TEST_SUID, TEST_MDB)
        eq_(len(self.fake_wmi.requests), i + 1)
