# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.trust_api import (
    TrustBinding,
    TrustPermanentError,
)
from passport.backend.core.builders.trust_api.faker import (
    FakeTrustBinding,
    trust_check_payment,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID_2,
)


TEST_SERVICE_TICKET = 'service-ticket'


@with_settings(
    TRUST_BINDINGS_URL='http://localhost/',
    TRUST_BINDINGS_RETRIES=2,
    TRUST_BINDINGS_TIMEOUT=3,
)
class FakeTrustBindingTestCase(TestCase):
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

        self.faker = FakeTrustBinding()
        self.faker.start()
        self.trust_binding = TrustBinding()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.trust_binding

        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_check_payment(self):
        self.faker.set_response_value(
            'check_payment',
            json.dumps(trust_check_payment()),
        )
        eq_(
            self.trust_binding.check_payment(
                purchase_token='a1dba3b2b31439dc258d859964ce7243',
                oauth_token='token',
            ),
            trust_check_payment(),
        )
        assert_builder_requested(self.faker, 1)

    @raises(TrustPermanentError)
    def test_check_payment_error(self):
        self.faker.set_response_side_effect('check_payment', TrustPermanentError)
        self.trust_binding.check_payment(
            purchase_token='a1dba3b2b31439dc258d859964ce7243',
            oauth_token='token',
        ),
