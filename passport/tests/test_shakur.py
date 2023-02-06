# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.shakur import Shakur
from passport.backend.core.builders.shakur.exceptions import (
    ShakurPermanentError,
    ShakurTemporaryError,
)
from passport.backend.core.builders.shakur.faker.fake_shakur import (
    FakeShakur,
    shakur_check_password,
)
from passport.backend.core.test.test_utils import with_settings


TEST_SHA_PREFIX = '11111111'
TEST_SERVICE_TICKET = 'service-ticket'
TEST_SHAKUR_LIMIT = 100


@with_settings(
    SHAKUR_LIMIT=TEST_SHAKUR_LIMIT,
    SHAKUR_URL='http://localhost/',
    SHAKUR_RETRIES=2,
    SHAKUR_TIMEOUT=3,
    SHAKUR_USE_TVM=False,
    IS_SHAKUR_CHECK_DISABLED=False,
)
class TestShakurCommon(unittest.TestCase):
    def setUp(self):
        self.shakur = Shakur()

        self.response = mock.Mock()
        self.shakur.useragent.request = mock.Mock()
        self.shakur.useragent.request.return_value = self.response
        self.response.content = json.dumps({})
        self.response.status_code = 200

    def tearDown(self):
        del self.shakur
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 400
        self.response.content = b'not a json'
        with assert_raises(ShakurPermanentError):
            self.shakur.check_password(TEST_SHA_PREFIX)

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = b'"server is down"'
        with assert_raises(ShakurTemporaryError):
            self.shakur.check_password(TEST_SHA_PREFIX)

    def test_response_not_valid_no_found_attribute(self):
        self.response.content = json.dumps({'passwords': []})
        with assert_raises(ShakurPermanentError):
            self.shakur.check_password(TEST_SHA_PREFIX)

    def test_response_not_valid_no_passwords_attribute(self):
        self.response.content = json.dumps({'found': True})
        with assert_raises(ShakurPermanentError):
            self.shakur.check_password(TEST_SHA_PREFIX)

    def test_response_not_valid_no_sha_attribute(self):
        self.response.content = json.dumps(
            {
                'found': True,
                'passwords': [
                    {'sha1': 'sha_password', 'source': 'haveibeenpwned', 'freq': 1},
                    {'source': 'haveibeenpwned', 'freq': 1},
                    {'sha1': 'sha_password1', 'source': 'haveibeenpwned', 'freq': 2},
                ],
            }
        )
        with assert_raises(ShakurPermanentError):
            self.shakur.check_password(TEST_SHA_PREFIX)

    def test_passport_default_initialization(self):
        shakur = Shakur()
        ok_(shakur.useragent is not None)
        eq_(shakur.url, 'http://localhost/')


@with_settings(
    SHAKUR_LIMIT=TEST_SHAKUR_LIMIT,
    SHAKUR_URL='http://localhost/',
    SHAKUR_RETRIES=2,
    SHAKUR_TIMEOUT=3,
    SHAKUR_USE_TVM=False,
    IS_SHAKUR_CHECK_DISABLED=False,
)
class TestShakurMethods(unittest.TestCase):
    def setUp(self):
        self.fake_shakur = FakeShakur()
        self.fake_shakur.start()
        self.shakur = Shakur()

    def tearDown(self):
        self.fake_shakur.stop()
        del self.fake_shakur

    def test_check_password_ok(self):
        self.fake_shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password(TEST_SHA_PREFIX)),
        )
        response = self.shakur.check_password(TEST_SHA_PREFIX)

        eq_(
            response,
            shakur_check_password(TEST_SHA_PREFIX),
        )
        eq_(len(self.fake_shakur.requests), 1)

        self.fake_shakur.requests[0].assert_url_starts_with('http://localhost/api/shakur/checkpassword')
        self.fake_shakur.requests[0].assert_query_equals({
            'sha1': TEST_SHA_PREFIX,
            'length': str(TEST_SHAKUR_LIMIT),
        })

    def test_with_tvm_ok(self):
        tvm_mock = mock.Mock()
        tvm_mock.get_ticket_by_alias.return_value = TEST_SERVICE_TICKET
        shakur = Shakur(use_tvm=True, tvm_credentials_manager=tvm_mock)
        self.fake_shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password(TEST_SHA_PREFIX)),
        )

        response = shakur.check_password(TEST_SHA_PREFIX)

        eq_(
            response,
            shakur_check_password(TEST_SHA_PREFIX),
        )

        self.fake_shakur.requests[0].assert_properties_equal(
            headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        )
