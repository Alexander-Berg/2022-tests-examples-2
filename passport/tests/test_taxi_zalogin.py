# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose_parameterized import parameterized
from passport.backend.core.builders.taxi_zalogin import (
    EVENT_TYPE,
    TaxiZalogin,
)
from passport.backend.core.builders.taxi_zalogin.exceptions import (
    TaxiZaloginAuthEror,
    TaxiZaloginPermanentZaloginError,
    TaxiZaloginTemporaryZaloginError,
)
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 1
TEST_UID2 = 2
TEST_UNIXTIME = 100000


def taxi_zalogin_response(code, message):
    return json.dumps({'code': str(code), 'message': message})


@with_settings(
    TAXI_ZALOGIN_URL='http://localhost/',
    TAXI_ZALOGIN_RETRIES=2,
    TAXI_ZALOGIN_TIMEOUT=1,
)
class TestTaxiZalogin(unittest.TestCase):
    def setUp(self):
        self.taxi = TaxiZalogin(use_tvm=False)
        self.taxi.useragent = mock.Mock()

        self.response = mock.Mock()
        self.taxi.useragent.request.return_value = self.response
        self.taxi.useragent.request_error_class = self.taxi.temporary_error_class
        self.response.content = json.dumps(taxi_zalogin_response('200', 'hello'))
        self.response.status_code = 200

    def tearDown(self):
        del self.taxi
        del self.response

    def test_ok(self):
        self.response.status_code = 200
        self.response.content = b'{}'
        assert self.taxi.uid_notify(TEST_UID, TEST_UID2, EVENT_TYPE.BIND) == dict()

    def test_error_empty_json(self):
        self.response.status_code = 400
        self.response.content = b'{}'
        self.assertRaises(TaxiZaloginTemporaryZaloginError, self.taxi.uid_notify, TEST_UID, TEST_UID2, EVENT_TYPE.BIND)

    @parameterized.expand([
        (401,),
        (403,),
    ])
    def test_invalid_auth(self, status_code):
        self.response.status_code = status_code
        self.response.content = taxi_zalogin_response(status_code, 'invalid auth')
        self.assertRaises(TaxiZaloginAuthEror, self.taxi.uid_notify, TEST_UID, TEST_UID2, EVENT_TYPE.BIND)

    def test_failed_to_parse_response(self):
        self.response.status_code = 400
        self.response.content = b'not a json'
        self.assertRaises(TaxiZaloginPermanentZaloginError, self.taxi.uid_notify, TEST_UID, TEST_UID2, EVENT_TYPE.BIND)

    def test_server_temporary_error(self):
        self.response.status_code = 503
        self.response.content = b'"server temporarily unavailable"'
        self.assertRaises(TaxiZaloginTemporaryZaloginError, self.taxi.uid_notify, TEST_UID, TEST_UID2, EVENT_TYPE.BIND)

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = taxi_zalogin_response(500, 'server error')
        self.assertRaises(TaxiZaloginTemporaryZaloginError, self.taxi.uid_notify, TEST_UID, TEST_UID2, EVENT_TYPE.BIND)
