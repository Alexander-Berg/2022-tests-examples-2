# pylint: disable=C0103

import typing

import pytest

from tests_grocery_payments_methods import consts
from tests_grocery_payments_methods import models


class Context:
    def __init__(self, experiments3):
        self.experiments3 = experiments3

        self.sbp_banks(banks=consts.BANKS)
        self.sbp_banks_meta(meta_list=consts.BANKS_META)
        self.merchants(merchant_ids=consts.MERCHANTS)
        self.service_token()

    def grocery_binding_currency(self, currency):
        self.experiments3.add_config(
            name='grocery_binding_currency',
            consumers=['grocery-payments-methods/binding'],
            default_value={'currency': 'RUB'},
        )

    def sbp_banks(self, banks: typing.List[models.SbpBankInfo]):
        self.experiments3.add_config(
            name='grocery_payments_sbp_banks',
            consumers=['grocery-payments/sbp-banks'],
            default_value={'banks': [bank.to_raw() for bank in banks]},
        )

    def merchants(
            self, merchant_ids: typing.Optional[typing.List[str]] = None,
    ):
        if merchant_ids is None:
            merchant_ids = consts.MERCHANTS

        self.experiments3.add_config(
            name='grocery_merchants',
            consumers=['grocery-payments-methods/lpm'],
            default_value={'merchant_ids': merchant_ids},
        )

    def sbp_banks_meta(self, meta_list):
        self.experiments3.add_config(
            name='grocery_payments_sbp_banks_meta',
            consumers=['grocery-payments/sbp-banks'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'value': meta['bank_name'],
                            'arg_name': 'bank_name',
                            'arg_type': 'string',
                        },
                    },
                    'value': meta,
                }
                for meta in meta_list
            ],
        )

    def service_token(self, token=consts.SERVICE_TOKEN):
        self.experiments3.add_config(
            name='grocery_service_token',
            consumers=['grocery-payments-methods/lpm'],
            default_value={'token': token},
        )

    def methods_fallbacks(self):
        self.experiments3.add_config(
            name='grocery_payments_methods_fallbacks',
            consumers=['grocery-payments/methods_fallbacks'],
            default_value={'fallback_name': consts.METHODS_FALLBACK_NAME},
        )

    def filter_unavailable_methods(self, enabled):
        self.experiments3.add_config(
            name='grocery_filter_unavailable_payment_methods',
            consumers=['grocery-payments-methods/filter'],
            clauses=[
                {
                    'title': 'enabled for unavailable methods',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'value': False,
                            'arg_name': 'is_available',
                            'arg_type': 'bool',
                        },
                    },
                    'value': {'enabled': enabled},
                },
            ],
            default_value={'enabled': False},
        )

    def grocery_binding_billing_service(self, service_name):
        self.experiments3.add_config(
            name='grocery_binding_billing_service',
            consumers=['grocery-payments-methods'],
            default_value={'service_name': service_name},
        )

    def can_pay_unverified_cards(self, enabled):
        self.experiments3.add_config(
            name='grocery_can_pay_unverified_cards',
            consumers=['grocery-payments-methods/filter'],
            default_value={'enabled': enabled},
        )


@pytest.fixture(name='grocery_payments_methods_configs', autouse=True)
def grocery_payments_methods_configs(experiments3):
    return Context(experiments3)
