# -*- coding: utf-8 -*-

from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    delivery_addresses_factors,
    delivery_addresses_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .test_base import (
    BaseCalculateFactorsMixinTestCase,
    eq_,
)


@with_settings_hosts()
class DeliveryAddressesHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, delivery_addresses=None):
        return {
            'delivery_addresses': delivery_addresses,
        }

    def test_delivery_addresses_no_match(self):
        userinfo_response = self.default_userinfo_response()
        form_values = self.form_values(delivery_addresses=[
            TEST_DELIVERY_ADDRESS_1,
            dict(TEST_DELIVERY_ADDRESS_1, city='moscoww'),
        ])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('delivery_addresses')

            expected_factors = delivery_addresses_factors(
                delivery_addresses_entered=[
                    TEST_DELIVERY_ADDRESS_1,
                    dict(TEST_DELIVERY_ADDRESS_1, city='moscoww'),
                ],
                delivery_addresses_account=[],
                delivery_addresses_matches=[],
                delivery_addresses_factor_entered_count=2,
                delivery_addresses_factor_account_count=0,
                delivery_addresses_factor_matches_count=0,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                delivery_addresses_statbox_entry(
                    delivery_addresses_factor_entered_count=2,
                    delivery_addresses_factor_account_count=0,
                    delivery_addresses_factor_matches_count=0,
                ),
                view.statbox,
            )
