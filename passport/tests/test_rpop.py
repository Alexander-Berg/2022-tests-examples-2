# -*- coding: utf-8 -*-

import json
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.mail_apis import (
    RPOP,
    RPOPInvalidResponseError,
    RPOPTemporaryError,
)
from passport.backend.core.builders.mail_apis.faker import (
    FakeRPOP,
    rpop_list_item,
    rpop_list_response,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.useragent.sync import RequestError


TEST_SUID = 1
TEST_MDB = 'pg'
RPOP_ERROR_RESPONSE = '''{"error":{"code":0,"message":"Unknown error","reason":"reason"}}'''


@with_settings_hosts(
    RPOP_API_URL='http://localhost/',
    RPOP_API_RETRIES=10,
    RPOP_API_TIMEOUT=1,
)
class TestRPOP(TestCase):
    def setUp(self):
        self.rpop = RPOP()

        self.fake_rpop = FakeRPOP()
        self.fake_rpop.start()

        self.methods = [
            ('list', self.rpop.list),
        ]

    def tearDown(self):
        self.fake_rpop.stop()
        del self.fake_rpop
        del self.rpop
        del self.methods

    def test_list(self):
        response = rpop_list_response([rpop_list_item()])
        self.fake_rpop.set_response_value(
            'list',
            response,
        )

        addresses = self.rpop.list(TEST_SUID, TEST_MDB)

        eq_(addresses, json.loads(response))

        requests = self.fake_rpop.requests
        eq_(len(requests), 1)
        requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/api/list?suid=%s&mdb=%s&json=1' % (TEST_SUID, TEST_MDB),
        )

    def test_retries_error(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_rpop.set_response_side_effect(method_name, RequestError)
            with assert_raises(RPOPTemporaryError):
                method(TEST_SUID, TEST_MDB)
        eq_(len(self.fake_rpop.requests), 10 * (i + 1))

    def test_bad_status_code(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_rpop.set_response_value(method_name, b'{}', status=500)
            with assert_raises(RPOPInvalidResponseError):
                method(TEST_SUID, TEST_MDB)
        eq_(len(self.fake_rpop.requests), i + 1)

    def test_error_in_response(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_rpop.set_response_value(method_name, RPOP_ERROR_RESPONSE)
            with assert_raises(RPOPInvalidResponseError):
                method(TEST_SUID, TEST_MDB)
        eq_(len(self.fake_rpop.requests), i + 1)

    def test_invalid_json(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_rpop.set_response_value(method_name, b'invalid json')
            with assert_raises(RPOPInvalidResponseError):
                method(TEST_SUID, TEST_MDB)
        eq_(len(self.fake_rpop.requests), i + 1)
