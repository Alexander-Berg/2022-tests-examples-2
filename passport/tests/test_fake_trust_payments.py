# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import eq_
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.trust_api import TrustPayments
from passport.backend.core.builders.trust_api.faker import (
    cancel_payment_response,
    create_basket_response,
    FakeTrustPayments,
    get_basket_status_response,
    get_payment_methods_response,
    start_payment_response,
    TEST_PURCHASE_TOKEN,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID_2,
)


TEST_UID = 123
TEST_SERVICE_TICKET = 'service-ticket'


@with_settings(
    TRUST_PAYMENTS_URL='http://localhost/',
    TRUST_PAYMENTS_RETRIES=2,
    TRUST_PAYMENTS_TIMEOUT=3,
)
class FakeTrustPaymentsTestCase(TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID_2): {
                    'alias': 'trust_payment_api',
                    'ticket': TEST_SERVICE_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.faker = FakeTrustPayments()
        self.faker.start()
        self.trust_payments = TrustPayments()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.trust_payments

        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_get_payment_methods(self):
        self.faker.set_response_value(
            'get_payment_methods',
            json.dumps(get_payment_methods_response()),
        )
        eq_(
            self.trust_payments.get_payment_methods(uid=TEST_UID),
            get_payment_methods_response()['bound_payment_methods'],
        )
        assert_builder_requested(self.faker, 1)

    def test_create_basket(self):
        self.faker.set_response_value(
            'create_basket',
            json.dumps(create_basket_response()),
        )
        eq_(
            self.trust_payments.create_basket(
                uid=TEST_UID,
                paymethod_id='card-123',
                product_id='product-123',
                return_path='https://ya.ru',
            ),
            TEST_PURCHASE_TOKEN,
        )
        assert_builder_requested(self.faker, 1)

    def test_start_payment(self):
        self.faker.set_response_value(
            'start_payment',
            json.dumps(start_payment_response()),
        )
        eq_(
            self.trust_payments.start_payment(TEST_UID, TEST_PURCHASE_TOKEN),
            start_payment_response(),
        )
        assert_builder_requested(self.faker, 1)

    def test_basket_status(self):
        self.faker.set_response_value(
            'get_basket_status',
            json.dumps(get_basket_status_response()),
        )
        eq_(
            self.trust_payments.get_basket_status(TEST_UID, TEST_PURCHASE_TOKEN),
            get_basket_status_response(),
        )
        assert_builder_requested(self.faker, 1)

    def test_cancel_payment(self):
        self.faker.set_response_value(
            'cancel_payment',
            json.dumps(cancel_payment_response()),
        )
        eq_(
            self.trust_payments.cancel_payment(TEST_UID, TEST_PURCHASE_TOKEN),
            cancel_payment_response(),
        )
        assert_builder_requested(self.faker, 1)
