# pylint: disable=invalid-name

import pytest

from .. import consts
from .. import models


class Context:
    def __init__(self, experiments3, taxi_config):
        self.experiments3 = experiments3
        self.taxi_config = taxi_config

        self.balance_client_id()
        self.courier_balance_client_id()

        taxi_config.set_values(
            dict(
                GROCERY_PAYMENTS_BILLING_AGGLOMERATIONS={
                    '213': consts.AGGLOMERATION,
                },
                GROCERY_PAYMENTS_BILLING_OEBS_ID_IN_PAYLOAD_ENABLED={
                    'all': True,
                },
            ),
        )

    def balance_client_id(self, name=None, **kwargs):
        name = name or 'grocery_balance_client_id'
        clauses = [
            {
                'title': f'Settings for {country.name}',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'value': country.country_iso3,
                        'arg_name': 'country_iso3',
                        'arg_type': 'string',
                    },
                },
                'value': {
                    'balance_client_id': get_balance_client_id(country),
                    **kwargs,
                },
            }
            for country in consts.COUNTRIES
        ]

        self.experiments3.add_config(
            name=name,
            consumers=['grocery-payments-billing/client_id'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=clauses,
        )

    def courier_balance_client_id(self, modification_type='nope', **kwargs):
        self.balance_client_id(
            name='grocery_courier_balance_client_id',
            modification_type=modification_type,
            **kwargs,
        )

    def tlog_enabled(self, enabled: bool):
        self.experiments3.add_config(
            name='grocery_tlog_enabled',
            consumers=['grocery-payments-billing/client_id'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
        )

    def tlog_params(self):
        self.experiments3.add_config(
            name='grocery_tlog_params',
            consumers=['grocery-payments-billing/client_id'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {
                        'company_type': consts.COMPANY_TYPE,
                        'contract_id': consts.CONTRACT_ID,
                        'firm_id': consts.FIRM_ID,
                        'ignore_in_balance': consts.IGNORE_IN_BALANCE,
                    },
                },
            ],
        )

    def service_id_mapping(self):
        self.experiments3.add_config(
            name='grocery_service_id_mapping',
            consumers=['grocery-payments-billing/client_id'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'service_id': consts.SERVICE_ID},
                },
            ],
        )

    def products_settings(self, settings: list):
        self.experiments3.add_config(
            name='grocery_tlog_products_settings_extra',
            consumers=['grocery-payments-billing/client_id'],
            clauses=[],
            default_value={'settings0': settings[0:2]},
            merge_values_by=[
                {
                    'consumer': 'grocery-payments-billing/client_id',
                    'merge_method': 'dicts_recursive_merge',
                    'tag': 'grocery_tlog_products_settings',
                },
            ],
        )

        self.experiments3.add_config(
            name='grocery_tlog_products_settings',
            consumers=['grocery-payments-billing/client_id'],
            clauses=[],
            default_value={'settings': settings[1::]},
            merge_values_by=[
                {
                    'consumer': 'grocery-payments-billing/client_id',
                    'merge_method': 'dicts_recursive_merge',
                    'tag': 'grocery_tlog_products_settings',
                },
            ],
        )

    def products_settings_default(self):
        self.products_settings(
            [
                {
                    'type': 'product_full_price',
                    'detailed_product': 'gross_sales_b2c',
                    'payment_kind': 'grocery_gross_sales_b2c_agent',
                },
                {
                    'type': 'discount',
                    'detailed_product': 'incentives_b2c_discount',
                    'payment_kind': 'grocery_incentives_b2c_discount_agent',
                },
                {
                    'type': 'coupon_plus',
                    'detailed_product': 'grocery_coupon_plus',
                    'payment_kind': 'grocery_coupon_plus_agent',
                },
                {
                    'type': 'tips',
                    'detailed_product': 'tips_b2c_agent',
                    'payment_kind': 'grocery_tips_b2c_agent',
                },
                {
                    'type': 'delivery',
                    'detailed_product': 'delivery_fee_b2c_agent',
                    'payment_kind': 'grocery_delivery_fee_b2c_agent',
                },
                {
                    'type': 'marketing_coupon',
                    'detailed_product': 'incentives_b2c_marketing_coupon',
                    'payment_kind': (
                        'grocery_incentives_b2c_marketing_coupon_agent'
                    ),
                },
                {
                    'type': 'support_coupon',
                    'detailed_product': 'incentives_b2c_support_coupon',
                    'payment_kind': (
                        'grocery_incentives_b2c_support_coupon_agent'
                    ),
                },
                {
                    'type': 'service_fee',
                    'detailed_product': 'service_fee_b2c_agent',
                    'payment_kind': 'grocery_service_fee_b2c_agent',
                },
            ],
        )

    def tlog_eats_settings(self, *, v2_flow_from):
        self.experiments3.add_config(
            name='grocery_tlog_eats_settings',
            consumers=['grocery-payments-billing/client_id'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'v2_flow_from': v2_flow_from},
                },
            ],
        )


@pytest.fixture(name='grocery_payments_billing_configs', autouse=True)
def grocery_payments_billing_configs(experiments3, taxi_config):
    return Context(experiments3, taxi_config)


def get_balance_client_id(country: models.Country):
    return f'{country.name}-client-id'
