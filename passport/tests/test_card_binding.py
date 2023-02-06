# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.trust_api import TrustBinding
from passport.backend.core.builders.trust_api.exceptions import (
    TrustBadDataError,
    TrustPermanentError,
)
from passport.backend.core.builders.trust_api.faker import (
    FakeTrustBinding,
    trust_bind,
    trust_check_payment,
    trust_verify,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID_2,
)


TEST_SERVICE_TICKET = 'service-ticket'
TEST_CARD_DATA_ENCRYPTED = 'XNJBoHEdegPGgqw=='
TEST_BINDING_ID = 'card-x5a699b31f78dba7d27c4f7ab'
TEST_VERIFICATION_ID = 'a1dba3b2b31439dc258d859964ce7243'
TEST_TOKEN = 'oauth-token'


@with_settings(
    TRUST_BINDINGS_URL='http://localhost/',
    TRUST_BINDINGS_RETRIES=1,
    TRUST_BINDINGS_TIMEOUT=1,
)
class TestTrustBindingCommon(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID_2): {
                    'alias': 'trust_binding_api',
                    'ticket': TEST_SERVICE_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.trust_binding = TrustBinding()

        self.response = mock.Mock()
        self.trust_binding.useragent.request = mock.Mock()
        self.trust_binding.useragent.request.return_value = self.response
        self.response.content = json.dumps({})
        self.response.status_code = 200

    def tearDown(self):
        del self.trust_binding
        del self.response
        self.fake_tvm_credentials_manager.stop()

    def test_failed_input_data_validation_response(self):
        self.response.status_code = 400
        self.response.content = b'Input payload validation failed'
        with assert_raises(TrustBadDataError):
            self.trust_binding.bind(TEST_CARD_DATA_ENCRYPTED, TEST_TOKEN)

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = b'Server is down'
        with assert_raises(TrustPermanentError):
            self.trust_binding.bind(TEST_CARD_DATA_ENCRYPTED, TEST_TOKEN)

    def test_bind_response_not_valid_no_binding_id_attribute(self):
        self.response.content = json.dumps({'binding': {'type': 'card'}})
        with assert_raises(TrustPermanentError):
            self.trust_binding.bind(
                card_data_encrypted=TEST_CARD_DATA_ENCRYPTED,
                oauth_token=TEST_TOKEN,
            )

    def test_check_payment_not_valid_no_status_attribute(self):
        self.response.content = json.dumps({})
        with assert_raises(TrustPermanentError):
            self.trust_binding.check_payment(
                purchase_token=TEST_VERIFICATION_ID,
                oauth_token=TEST_TOKEN,
            )

    def test_passport_default_initialization(self):
        trust_binding = TrustBinding()
        ok_(trust_binding.useragent is not None)
        eq_(trust_binding.url, 'http://localhost/')


@with_settings(
    TRUST_BINDINGS_URL='http://localhost/',
    TRUST_BINDINGS_RETRIES=1,
    TRUST_BINDINGS_TIMEOUT=1,
)
class TestTrustBindingMethods(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID_2): {
                    'alias': 'trust_binding_api',
                    'ticket': TEST_SERVICE_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.fake_trust_binding = FakeTrustBinding()
        self.fake_trust_binding.start()
        self.trust_binding = TrustBinding()

    def tearDown(self):
        self.fake_trust_binding.stop()
        del self.fake_trust_binding

        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_bind_ok(self):
        self.fake_trust_binding.set_response_value(
            'bind',
            json.dumps(trust_bind()),
        )
        response = self.trust_binding.bind(
            card_data_encrypted=TEST_CARD_DATA_ENCRYPTED,
            oauth_token=TEST_TOKEN,
        )

        eq_(
            response,
            trust_bind()
        )
        eq_(len(self.fake_trust_binding.requests), 1)
        self.fake_trust_binding.requests[0].assert_url_starts_with('http://localhost/bindings/v2.0/bindings')

    def test_verify_ok(self):
        self.fake_trust_binding.set_response_value(
            'verify',
            json.dumps(trust_verify()),
        )
        response = self.trust_binding.verify(
            card_data_encrypted=TEST_CARD_DATA_ENCRYPTED,
            binding_id=TEST_BINDING_ID,
            oauth_token=TEST_TOKEN,
        )

        eq_(
            response,
            trust_verify()
        )
        eq_(len(self.fake_trust_binding.requests), 1)
        self.fake_trust_binding.requests[0].assert_url_starts_with(
            'http://localhost/bindings/v2.0/bindings/%s/verify' % TEST_BINDING_ID
        )

    def test_check_payment_ok(self):
        self.fake_trust_binding.set_response_value(
            'check_payment',
            json.dumps(trust_check_payment()),
        )
        response = self.trust_binding.check_payment(
            purchase_token=TEST_VERIFICATION_ID,
            oauth_token=TEST_TOKEN,
        )

        eq_(
            response,
            trust_check_payment()
        )
        eq_(len(self.fake_trust_binding.requests), 1)

        self.fake_trust_binding.requests[0].assert_url_starts_with('http://localhost/check_payment')

    def test_tvm_ok(self):
        tvm_mock = mock.Mock()
        tvm_mock.get_ticket_by_alias.return_value = TEST_SERVICE_TICKET
        trust = TrustBinding(tvm_credentials_manager=tvm_mock)
        self.fake_trust_binding.set_response_value(
            'bind',
            json.dumps(trust_bind()),
        )
        response = trust.bind(
            card_data_encrypted=TEST_CARD_DATA_ENCRYPTED,
            oauth_token=TEST_TOKEN,
        )

        eq_(
            response,
            trust_bind(),
        )

        self.fake_trust_binding.requests[0].assert_properties_equal(
            headers={
                'Content-Type': 'application/json',
                'X-OAuth-Token': TEST_TOKEN,
                'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
                'Accept': 'application/json',
            },
        )
