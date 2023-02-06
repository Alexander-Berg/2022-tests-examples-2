# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.passport import (
    Passport,
    PassportPermanentError,
    PassportTemporaryError,
)
from passport.backend.core.builders.passport.faker import (
    FakePassport,
    passport_bundle_api_error_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 1
TEST_SID = 'mail'
TEST_TIMESTAMP = 1000
TEST_LOGIN = 'test-login'

TEST_OK_RESPONSE_RAW = '{"status": "ok"}'
TEST_OK_RESPONSE = json.loads(TEST_OK_RESPONSE_RAW)


@with_settings(
    PASSPORT_URL='http://localhost/',
    PASSPORT_CONSUMER='passport',
    PASSPORT_RETRIES=2,
    PASSPORT_TIMEOUT=1,
)
class FakePassportTestCase(TestCase):
    def setUp(self):
        self.faker = FakePassport()
        self.faker.start()
        self.passport = Passport()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_subscribe(self):
        self.faker.set_response_value('subscribe', TEST_OK_RESPONSE_RAW)
        eq_(self.passport.subscribe(TEST_UID, TEST_SID), TEST_OK_RESPONSE)

    def test_unsubscribe(self):
        self.faker.set_response_value('unsubscribe', TEST_OK_RESPONSE_RAW)
        eq_(self.passport.unsubscribe(TEST_UID, TEST_SID), TEST_OK_RESPONSE)

    def test_password_options(self):
        self.faker.set_response_value('password_options', TEST_OK_RESPONSE_RAW)
        eq_(self.passport.password_options(TEST_UID), TEST_OK_RESPONSE)

    def test_account_options(self):
        self.faker.set_response_value('account_options', TEST_OK_RESPONSE_RAW)
        eq_(self.passport.account_options(TEST_UID), TEST_OK_RESPONSE)

    def test_rfc_2fa_enable(self):
        self.faker.set_response_value('rfc_2fa_enable', TEST_OK_RESPONSE_RAW)
        eq_(self.passport.rfc_2fa_enable(TEST_LOGIN), TEST_OK_RESPONSE)

    @raises(PassportTemporaryError)
    def test_rfc_2fa_enable_error(self):
        self.faker.set_response_value(
            'rfc_2fa_enable',
            passport_bundle_api_error_response(error='backend.database_failed'),
        )
        self.passport.rfc_2fa_enable(TEST_LOGIN)

    def test_rfc_2fa_disable(self):
        self.faker.set_response_value('rfc_2fa_disable', TEST_OK_RESPONSE_RAW)
        eq_(self.passport.rfc_2fa_disable(TEST_LOGIN), TEST_OK_RESPONSE)

    @raises(PassportTemporaryError)
    def test_rfc_2fa_disable_error(self):
        self.faker.set_response_value(
            'rfc_2fa_disable',
            passport_bundle_api_error_response(error='backend.database_failed'),
        )
        self.passport.rfc_2fa_disable(TEST_LOGIN)

    def test_rfc_2fa_set_time(self):
        self.faker.set_response_value('rfc_2fa_set_time', TEST_OK_RESPONSE_RAW)
        eq_(self.passport.rfc_2fa_set_time(TEST_UID, TEST_TIMESTAMP), TEST_OK_RESPONSE)

    @raises(PassportPermanentError)
    def test_rfc_2fa_set_time_error(self):
        self.faker.set_response_value(
            'rfc_2fa_set_time',
            passport_bundle_api_error_response(error='backend.failed'),
        )
        self.passport.rfc_2fa_set_time(TEST_UID, TEST_TIMESTAMP)

    def test_takeout_start_extract(self):
        self.faker.set_response_value('takeout_start_extract', TEST_OK_RESPONSE_RAW)
        self.passport.takeout_start_extract(TEST_UID)

    def test_takeout_finish_extract(self):
        self.faker.set_response_value('takeout_finish_extract', TEST_OK_RESPONSE_RAW)
        self.passport.takeout_finish_extract(TEST_UID, 'url')

    def test_takeout_delete_extract_result(self):
        self.faker.set_response_value('takeout_delete_extract_result', TEST_OK_RESPONSE_RAW)
        self.passport.takeout_delete_extract_result(TEST_UID)
