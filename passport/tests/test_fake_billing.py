# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.billing import (
    BaseBillingError,
    BillingXMLRPC,
)
from passport.backend.core.builders.billing.faker.billing import (
    billing_check_binding_response,
    billing_create_binding_response,
    billing_do_binding_response,
    billing_list_payment_methods_response,
    billing_unbind_card_response,
    FakeBillingXMLRPC,
)
from passport.backend.core.test.test_utils import with_settings


TEST_TOKEN = 'token'


@with_settings(
    BILLING_XMLRPC_URL='http://yandex.ru',
    BILLING_XMLRPC_RETRIES=2,
    BILLING_XMLRPC_TIMEOUT=1,
    BILLING_TOKEN=TEST_TOKEN,
    DOMAIN_KEYSPACES=(
        ('yandex.ru', 'yandex.ru'),
    ),
)
class FakeBillingXMLRPCTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_billing = FakeBillingXMLRPC()
        self.fake_billing.start()

    def tearDown(self):
        self.fake_billing.stop()
        del self.fake_billing

    def test_set_response_side_effect(self):
        ok_(not self.fake_billing._mock.request.called)

        builder = BillingXMLRPC()
        for method, params in (
            ('list_payment_methods', (12354, '127.0.0.1')),
            ('create_binding', (12354, 'http://retpath')),
            ('do_binding', ('purchase_token',)),
            ('check_binding', ('purchase_token',)),
            ('unbind_card', ('sessionid', '127.0.0.1', 'yandex.ru', 'card_id')),
        ):
            self.fake_billing.set_response_side_effect(method, BaseBillingError())
            with assert_raises(BaseBillingError):
                getattr(builder, method)(*params)
        assert_builder_requested(self.fake_billing, times=5)

    def test_set_response_value(self):
        ok_(not self.fake_billing._mock.request.called)

        builder = BillingXMLRPC()
        for method, params, response_getter in (
            ('list_payment_methods', (12354, '127.0.0.1'), billing_list_payment_methods_response),
            ('create_binding', (12354, 'http://retpath'), billing_create_binding_response),
            ('do_binding', ('purchase_token',), billing_do_binding_response),
            ('check_binding', ('purchase_token',), billing_check_binding_response),
            ('unbind_card', ('sessionid', '127.0.0.1', 'yandex.ru', 'card_id'), billing_unbind_card_response),
        ):
            self.fake_billing.set_response_value(method, response_getter())
            result = getattr(builder, method)(*params)
            eq_(result, response_getter(serialize=False))
        assert_builder_requested(self.fake_billing, times=5)

    def test_set_response_value_for_unknown_method(self):
        with assert_raises(ValueError):
            self.fake_billing.set_response_value('unknown_method', tuple())

    def test_set_response_side_effect_for_unknown_method(self):
        with assert_raises(ValueError):
            self.fake_billing.set_response_side_effect('unknown_method', ValueError)
