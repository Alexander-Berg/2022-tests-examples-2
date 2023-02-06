# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.trust_api import TrustPayments
from passport.backend.core.builders.trust_api.exceptions import (
    TrustBadDataError,
    TrustPermanentError,
    TrustTemporaryError,
)
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


TEST_SERVICE_TICKET = 'service-ticket'
TEST_PAYMETHOD_ID = 'card-x5a699b31f78dba7d27c4f7ab'
TEST_UID = 123


@with_settings(
    TRUST_PAYMENTS_URL='http://localhost/',
    TRUST_PAYMENTS_RETRIES=1,
    TRUST_PAYMENTS_TIMEOUT=1,
)
class TestTrustPaymentsCommon(unittest.TestCase):
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

        self.trust_payments = TrustPayments()

        self.response = mock.Mock()
        self.trust_payments.useragent.request = mock.Mock()
        self.trust_payments.useragent.request.return_value = self.response
        self.response.content = json.dumps({})
        self.response.status_code = 200

    def tearDown(self):
        del self.trust_payments
        del self.response
        self.fake_tvm_credentials_manager.stop()

    def test_failed_input_data_validation_response(self):
        self.response.status_code = 400
        self.response.content = b'Input payload validation failed'
        with assert_raises(TrustBadDataError):
            self.trust_payments.start_payment(TEST_UID, TEST_PURCHASE_TOKEN)

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = b'Server is down'
        with assert_raises(TrustTemporaryError):
            self.trust_payments.start_payment(TEST_UID, TEST_PURCHASE_TOKEN)

    def test_create_basket_response_not_valid_no_purchase_token(self):
        self.response.content = json.dumps({'status': 'success'})
        with assert_raises(TrustPermanentError):
            self.trust_payments.create_basket(TEST_UID, 'test-paymethod', 'test-product', 'https://retpath')

    def test_get_basket_status_response_not_valid_no_payment_resp_code(self):
        self.response.content = json.dumps(
            {'status': 'success', 'payment_status': 'not_authorized'},
        )
        with assert_raises(TrustPermanentError):
            self.trust_payments.get_basket_status(TEST_UID, TEST_PURCHASE_TOKEN)

    def test_get_basket_status_response_not_valid_no_3ds_url(self):
        self.response.content = json.dumps({'status': 'success', 'payment_status': 'started'})
        with assert_raises(TrustTemporaryError):
            self.trust_payments.get_basket_status(TEST_UID, TEST_PURCHASE_TOKEN)


@with_settings(
    TRUST_PAYMENTS_URL='http://localhost/',
    TRUST_PAYMENTS_RETRIES=1,
    TRUST_PAYMENTS_TIMEOUT=1,
)
class TestTrustPaymentsMethods(unittest.TestCase):
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

        self.fake_trust_payments = FakeTrustPayments()
        self.fake_trust_payments.start()
        self.trust_payments = TrustPayments()

    def tearDown(self):
        self.fake_trust_payments.stop()
        del self.fake_trust_payments

        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_get_payment_methods_ok(self):
        self.fake_trust_payments.set_response_value(
            'get_payment_methods',
            json.dumps(get_payment_methods_response()),
        )
        response = self.trust_payments.get_payment_methods(uid=TEST_UID)

        eq_(
            response,
            get_payment_methods_response()['bound_payment_methods'],
        )
        eq_(len(self.fake_trust_payments.requests), 1)
        self.fake_trust_payments.requests[0].assert_properties_equal(
            url='http://localhost/payment-methods',
        )

    def test_get_payment_methods_empty_ok(self):
        self.fake_trust_payments.set_response_value(
            'get_payment_methods',
            json.dumps(get_payment_methods_response(is_empty=True)),
        )
        response = self.trust_payments.get_payment_methods(uid=TEST_UID)

        eq_(
            response,
            [],
        )
        eq_(len(self.fake_trust_payments.requests), 1)
        self.fake_trust_payments.requests[0].assert_properties_equal(
            url='http://localhost/payment-methods',
        )

    def test_create_basket_ok(self):
        self.fake_trust_payments.set_response_value(
            'create_basket',
            json.dumps(create_basket_response()),
        )
        response = self.trust_payments.create_basket(
            uid=TEST_UID,
            paymethod_id=TEST_PAYMETHOD_ID,
            product_id='product-123',
            return_path='https://ya.ru',
        )

        eq_(
            response,
            TEST_PURCHASE_TOKEN,
        )
        eq_(len(self.fake_trust_payments.requests), 1)
        self.fake_trust_payments.requests[0].assert_properties_equal(
            url='http://localhost/payments',
            json_data={
                'paymethod_id': TEST_PAYMETHOD_ID,
                'product_id': 'product-123',
                'amount': 1,
                'currency': 'RUB',
                'return_path': 'https://ya.ru',
                'pass_params': {
                    'terminal_route_data': {
                        'service_force_3ds': 1,
                    },
                },
                'template_tag': 'desktop/form',
            },
        )

    def test_create_basket_with_new_form_and_params_ok(self):
        self.fake_trust_payments.set_response_value(
            'create_basket',
            json.dumps(create_basket_response()),
        )
        response = self.trust_payments.create_basket(
            uid=TEST_UID,
            paymethod_id=TEST_PAYMETHOD_ID,
            product_id='product-123',
            amount=11,
            return_path='https://ya.ru',
            use_new_trust_form=True,
            use_mobile_layout=True,
            login_id='login-id',
            is_chaas=True,
        )

        eq_(
            response,
            TEST_PURCHASE_TOKEN,
        )
        eq_(len(self.fake_trust_payments.requests), 1)
        self.fake_trust_payments.requests[0].assert_properties_equal(
            url='http://localhost/payments',
            json_data={
                'product_id': 'product-123',
                'amount': 11,
                'currency': 'RUB',
                'return_path': 'https://ya.ru',
                'afs_params': {
                    'login_id': 'login-id',
                    'chaas': True,
                },
                'pass_params': {
                    'terminal_route_data': {
                        'service_force_3ds': 1,
                    },
                },
                'template_tag': 'mobile/form',
                'developer_payload': json.dumps({
                    'selected_card_id': TEST_PAYMETHOD_ID,
                    'auto_start_payment': True,
                    'template': 'checkout',
                    'blocks_visibility': {
                        'cardSelector': False,
                    },
                }),
            },
        )

    def test_get_basket_status_ok(self):
        self.fake_trust_payments.set_response_value(
            'get_basket_status',
            json.dumps(get_basket_status_response()),
        )
        response = self.trust_payments.get_basket_status(TEST_UID, TEST_PURCHASE_TOKEN)

        eq_(
            response,
            get_basket_status_response()
        )
        eq_(len(self.fake_trust_payments.requests), 1)
        self.fake_trust_payments.requests[0].assert_url_starts_with(
            'http://localhost/payments/%s' % TEST_PURCHASE_TOKEN,
        )

    def test_start_payment_ok(self):
        self.fake_trust_payments.set_response_value(
            'start_payment',
            json.dumps(start_payment_response()),
        )
        response = self.trust_payments.start_payment(TEST_UID, TEST_PURCHASE_TOKEN)

        eq_(
            response,
            start_payment_response()
        )
        eq_(len(self.fake_trust_payments.requests), 1)
        self.fake_trust_payments.requests[0].assert_url_starts_with(
            'http://localhost/payments/%s/start' % TEST_PURCHASE_TOKEN,
        )

    def test_cancel_payment_ok(self):
        self.fake_trust_payments.set_response_value(
            'cancel_payment',
            json.dumps(cancel_payment_response()),
        )
        response = self.trust_payments.cancel_payment(TEST_UID, TEST_PURCHASE_TOKEN)

        eq_(
            response,
            cancel_payment_response()
        )
        eq_(len(self.fake_trust_payments.requests), 1)
        self.fake_trust_payments.requests[0].assert_url_starts_with(
            'http://localhost/payments/%s/unhold' % TEST_PURCHASE_TOKEN,
        )
