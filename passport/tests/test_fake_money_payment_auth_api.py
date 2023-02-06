# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import eq_
from passport.backend.core.builders.money_api import get_money_payment_auth_api
from passport.backend.core.builders.money_api.faker import (
    FakeMoneyPaymentAuthApi,
    money_payment_api_auth_context_response,
    TEST_AUTH_CONTEXT_ID,
)
from passport.backend.core.test.test_utils import with_settings


@with_settings(
    MONEY_PAYMENT_AUTH_API_URL='http://localhost/',
    MONEY_PAYMENT_AUTH_API_TIMEOUT=0.5,
    MONEY_PAYMENT_AUTH_API_RETRIES=2,
)
class FakeMoneyPaymentAuthApiTestCase(TestCase):
    def setUp(self):
        self.faker = FakeMoneyPaymentAuthApi()
        self.faker.start()
        self.money_api = get_money_payment_auth_api()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.money_api

    def test_check_auth_context(self):
        self.faker.set_response_value(
            'check_auth_context',
            money_payment_api_auth_context_response(),
        )
        eq_(
            self.money_api.check_auth_context(TEST_AUTH_CONTEXT_ID),
            json.loads(money_payment_api_auth_context_response()),
        )

    def test_create_auth_context(self):
        self.faker.set_response_value(
            'create_auth_context',
            money_payment_api_auth_context_response(),
        )
        eq_(
            self.money_api.create_auth_context(uid=1, client_id='2', scopes=['3', '4'], retpath='5', request_id='6'),
            json.loads(money_payment_api_auth_context_response()),
        )
