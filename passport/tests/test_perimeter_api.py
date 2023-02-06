# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.perimeter_api import PerimeterApi
from passport.backend.core.builders.perimeter_api.exceptions import (
    PerimeterApiPermanentError,
    PerimeterApiTemporaryError,
)
from passport.backend.core.builders.perimeter_api.faker import (
    FakePerimeterApi,
    perimeter_error_response,
    perimeter_recreate_totp_secret_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.useragent.sync import RequestError


TEST_LOGIN = 'username'


class BasePerimeterApiTestCase(unittest.TestCase):

    def setUp(self):
        self.fake_perimeter = FakePerimeterApi()
        self.fake_perimeter.start()

        self.perimeter = PerimeterApi()

    def tearDown(self):
        self.fake_perimeter.stop()
        del self.fake_perimeter


@with_settings(
    PERIMETER_API_URL='http://localhost/',
    PERIMETER_API_TIMEOUT=0.5,
    PERIMETER_API_RETRIES=10,
    PERIMETER_API_CLIENT_CERT='',
    PERIMETER_API_CLIENT_CERT_KEY='',
)
class TestPerimeterApi(BasePerimeterApiTestCase):
    def test_failed_to_parse_response(self):
        self.fake_perimeter.set_response_value('recreate_totp_secret', u'плохой_json'.encode('utf-8'))
        with assert_raises(PerimeterApiPermanentError):
            self.perimeter.recreate_totp_secret(TEST_LOGIN)
        eq_(len(self.fake_perimeter.requests), 1)

    def test_no_retries_on_500(self):
        self.fake_perimeter.set_response_value('recreate_totp_secret', 'Server error', 500)
        with assert_raises(PerimeterApiPermanentError):
            self.perimeter.recreate_totp_secret(TEST_LOGIN)
        eq_(len(self.fake_perimeter.requests), 1)

    def test_request_error(self):
        self.fake_perimeter.set_response_side_effect('recreate_totp_secret', RequestError)
        with assert_raises(PerimeterApiTemporaryError):
            self.perimeter.recreate_totp_secret(TEST_LOGIN)
        eq_(len(self.fake_perimeter.requests), 10)


@with_settings(
    PERIMETER_API_URL='http://localhost/',
    PERIMETER_API_TIMEOUT=0.5,
    PERIMETER_API_RETRIES=2,
    PERIMETER_API_CLIENT_CERT='',
    PERIMETER_API_CLIENT_CERT_KEY='',
)
class TestRecreateTotpSecretPerimeterApi(BasePerimeterApiTestCase):
    def test_unknown_login(self):
        self.fake_perimeter.set_response_value(
            'recreate_totp_secret',
            perimeter_error_response('passport.permanent_error'),
        )
        with assert_raises(PerimeterApiPermanentError):
            self.perimeter.recreate_totp_secret(TEST_LOGIN)

    def test_passport_failed(self):
        self.fake_perimeter.set_response_value(
            'recreate_totp_secret',
            perimeter_error_response('passport.failed'),
        )
        with assert_raises(PerimeterApiTemporaryError):
            self.perimeter.recreate_totp_secret(TEST_LOGIN)

    def test_database_failed(self):
        self.fake_perimeter.set_response_value(
            'recreate_totp_secret',
            perimeter_error_response('database.failed'),
        )
        with assert_raises(PerimeterApiTemporaryError):
            self.perimeter.recreate_totp_secret(TEST_LOGIN)

    def test_unknown_error(self):
        self.fake_perimeter.set_response_value(
            'recreate_totp_secret',
            perimeter_error_response('unknown.error'),
        )
        with assert_raises(PerimeterApiPermanentError):
            self.perimeter.recreate_totp_secret(TEST_LOGIN)

    def test_error_but_no_error(self):
        self.fake_perimeter.set_response_value(
            'recreate_totp_secret',
            {'status': 'error'},
        )
        with assert_raises(PerimeterApiPermanentError):
            self.perimeter.recreate_totp_secret(TEST_LOGIN)

    def test_ok(self):
        self.fake_perimeter.set_response_value(
            'recreate_totp_secret',
            perimeter_recreate_totp_secret_response('SECRET'),
        )
        response = self.perimeter.recreate_totp_secret(TEST_LOGIN)
        eq_(response, {'status': 'ok', 'secret': 'SECRET'})

    def test_ok_empty_secret(self):
        self.fake_perimeter.set_response_value(
            'recreate_totp_secret',
            {'status': 'ok', 'secret': ''},
        )
        with assert_raises(PerimeterApiPermanentError):
            self.perimeter.recreate_totp_secret(TEST_LOGIN)
        eq_(len(self.fake_perimeter.requests), 1)

    def test_ok_no_secret(self):
        self.fake_perimeter.set_response_value(
            'recreate_totp_secret',
            {'status': 'ok'},
        )
        with assert_raises(PerimeterApiPermanentError):
            self.perimeter.recreate_totp_secret(TEST_LOGIN)
        eq_(len(self.fake_perimeter.requests), 1)
