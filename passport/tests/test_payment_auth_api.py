# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.money_api import MoneyPaymentAuthApi
from passport.backend.core.builders.money_api.exceptions import (
    MoneyApiInvalidResponseError,
    MoneyApiPermanentError,
    MoneyApiTemporaryError,
    MoneyApiUnknownSchemeError,
)
from passport.backend.core.builders.money_api.faker import (
    FakeMoneyPaymentAuthApi,
    money_payment_api_auth_context_response,
    money_payment_api_error_response,
    TEST_AUTH_CONTEXT_ID,
)
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 123
TEST_CLIENT_ID = '456'
TEST_SCOPES = ['test:foo', 'test:bar']
TEST_RETPATH = 'https://oauth.yandex.ru'
TEST_REQUEST_ID = 'rid'
TEST_SCHEME = 'scheme'


@with_settings(
    MONEY_PAYMENT_AUTH_API_URL='http://localhost/api/',
    MONEY_PAYMENT_AUTH_API_TIMEOUT=0.5,
    MONEY_PAYMENT_AUTH_API_RETRIES=2,
)
class TestMoneyPaymentAuthApiCommon(unittest.TestCase):
    def setUp(self):
        self.money_api = MoneyPaymentAuthApi()
        self.money_api.useragent = mock.Mock()

        self.response = mock.Mock()
        self.money_api.useragent.request_error_class = MoneyApiTemporaryError
        self.money_api.useragent.request.return_value = self.response
        self.response.content = json.dumps({})
        self.response.status_code = 200

    def tearDown(self):
        del self.money_api
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 200
        self.response.content = b'not a json'
        with assert_raises(MoneyApiInvalidResponseError):
            self.money_api.check_auth_context(TEST_AUTH_CONTEXT_ID)

    def test_server_error(self):
        self.response.status_code = 503
        self.response.content = money_payment_api_error_response('ServerError').encode('utf8')
        with assert_raises(MoneyApiPermanentError):
            self.money_api.check_auth_context(TEST_AUTH_CONTEXT_ID)

    def test_unknown_scheme(self):
        self.response.status_code = 404
        self.response.content = money_payment_api_error_response('Scheme not found').encode('utf8')
        with assert_raises(MoneyApiUnknownSchemeError):
            self.money_api.check_auth_context(TEST_AUTH_CONTEXT_ID)

    def test_bad_status_code(self):
        self.response.status_code = 418
        self.response.content = b''
        with assert_raises(MoneyApiPermanentError):
            self.money_api.check_auth_context(TEST_AUTH_CONTEXT_ID)


@with_settings(
    MONEY_PAYMENT_AUTH_API_URL='http://localhost/api/',
    MONEY_PAYMENT_AUTH_API_TIMEOUT=0.5,
    MONEY_PAYMENT_AUTH_API_RETRIES=2,
)
class TestMoneyPaymentAuthApiMethods(unittest.TestCase):
    def setUp(self):
        self.fake_money_api = FakeMoneyPaymentAuthApi()
        self.fake_money_api.start()
        self.money_api = MoneyPaymentAuthApi()

    def tearDown(self):
        self.fake_money_api.stop()
        del self.fake_money_api

    def test_check_auth_context_ok(self):
        self.fake_money_api.set_response_value(
            'check_auth_context',
            money_payment_api_auth_context_response(),
        )
        response = self.money_api.check_auth_context(TEST_AUTH_CONTEXT_ID)
        eq_(
            response,
            json.loads(money_payment_api_auth_context_response()),
        )
        eq_(len(self.fake_money_api.requests), 1)
        self.fake_money_api.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/api/v1/context?authContextId=%s' % TEST_AUTH_CONTEXT_ID,
        )

    def test_check_auth_context_with_scheme_ok(self):
        self.fake_money_api.set_response_value(
            'check_auth_context',
            money_payment_api_auth_context_response(),
        )
        response = self.money_api.check_auth_context(TEST_AUTH_CONTEXT_ID, scheme=TEST_SCHEME)
        eq_(
            response,
            json.loads(money_payment_api_auth_context_response()),
        )
        eq_(len(self.fake_money_api.requests), 1)
        self.fake_money_api.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/api/v1/context?authContextId=%s&scheme=%s' % (
                TEST_AUTH_CONTEXT_ID,
                TEST_SCHEME,
            ),
        )

    def test_create_auth_context_ok(self):
        self.fake_money_api.set_response_value(
            'create_auth_context',
            money_payment_api_auth_context_response(),
        )
        response = self.money_api.create_auth_context(
            uid=TEST_UID,
            client_id=TEST_CLIENT_ID,
            scopes=TEST_SCOPES,
            retpath=TEST_RETPATH,
            request_id=TEST_REQUEST_ID,
        )
        eq_(
            response,
            json.loads(money_payment_api_auth_context_response()),
        )
        eq_(len(self.fake_money_api.requests), 1)
        self.fake_money_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/api/v1/context',
            json_data={
                'uid': str(TEST_UID),
                'clientId': TEST_CLIENT_ID,
                'scope': ' '.join(TEST_SCOPES),
                'returnUri': TEST_RETPATH,
                'passportRequestId': TEST_REQUEST_ID,
            },
            headers={
                'Content-Type': 'application/json',
            },
        )

    def test_create_auth_context_with_scheme_ok(self):
        self.fake_money_api.set_response_value(
            'create_auth_context',
            money_payment_api_auth_context_response(),
        )
        response = self.money_api.create_auth_context(
            uid=TEST_UID,
            client_id=TEST_CLIENT_ID,
            scopes=TEST_SCOPES,
            retpath=TEST_RETPATH,
            request_id=TEST_REQUEST_ID,
            scheme=TEST_SCHEME,
        )
        eq_(
            response,
            json.loads(money_payment_api_auth_context_response()),
        )
        eq_(len(self.fake_money_api.requests), 1)
        self.fake_money_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/api/v1/context?scheme=%s' % TEST_SCHEME,
            json_data={
                'uid': str(TEST_UID),
                'clientId': TEST_CLIENT_ID,
                'scope': ' '.join(TEST_SCOPES),
                'returnUri': TEST_RETPATH,
                'passportRequestId': TEST_REQUEST_ID,
            },
            headers={
                'Content-Type': 'application/json',
            },
        )
