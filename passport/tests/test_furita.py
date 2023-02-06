# -*- coding: utf-8 -*-

import json
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.mail_apis import (
    Furita,
    FuritaInvalidResponseError,
    FuritaTemporaryError,
)
from passport.backend.core.builders.mail_apis.faker import (
    FakeFurita,
    furita_blackwhite_response,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.useragent.sync import RequestError


TEST_UID = 123
TEST_SUID = 1
TEST_MDB = 'pg'
FURITA_ERROR_RESPONSE = '''{"session":"DBV20003CGk1", "status":"error", "report":"No enough parameters"}'''


@with_settings_hosts(
    FURITA_API_URL='http://localhost/',
    FURITA_API_RETRIES=10,
    FURITA_API_TIMEOUT=1,
)
class TestFurita(TestCase):
    def setUp(self):
        self.furita = Furita()

        self.fake_furita = FakeFurita()
        self.fake_furita.start()

        self.methods = [
            ('blackwhite', self.furita.blackwhite),
        ]

    def tearDown(self):
        self.fake_furita.stop()
        del self.fake_furita
        del self.furita
        del self.methods

    def test_blackwhite(self):
        response = furita_blackwhite_response(['black@black.ru'])
        self.fake_furita.set_response_value(
            'blackwhite',
            response,
        )

        addresses = self.furita.blackwhite(TEST_UID)

        eq_(addresses, json.loads(response))

        requests = self.fake_furita.requests
        eq_(len(requests), 1)
        requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/api/blackwhitelist?uid=%s' % TEST_UID,
        )

    def test_retries_error(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_furita.set_response_side_effect(method_name, RequestError)
            with assert_raises(FuritaTemporaryError):
                method(TEST_UID)
        eq_(len(self.fake_furita.requests), 10 * (i + 1))

    def test_bad_status_code(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_furita.set_response_value(method_name, b'{}', status=500)
            with assert_raises(FuritaInvalidResponseError):
                method(TEST_UID)
        eq_(len(self.fake_furita.requests), i + 1)

    def test_error_in_response(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_furita.set_response_value(method_name, FURITA_ERROR_RESPONSE)
            with assert_raises(FuritaInvalidResponseError):
                method(TEST_UID)
        eq_(len(self.fake_furita.requests), i + 1)

    def test_invalid_json(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_furita.set_response_value(method_name, b'invalid json')
            with assert_raises(FuritaInvalidResponseError):
                method(TEST_UID)
        eq_(len(self.fake_furita.requests), i + 1)
