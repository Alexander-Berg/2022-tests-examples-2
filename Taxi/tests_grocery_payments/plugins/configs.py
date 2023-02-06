# pylint: disable=invalid-name
import pytest

from .. import consts
from .. import headers
from .. import models

BILLING_SETTINGS_VERSION = 'settings-version'
PROCESSING_NAME_CONFIG = 'grocery_payments_processing_name'
CASHBACK_EVENT_DELAY_SECONDS = 60

POLLING_INTERVAL = 10


class Context:
    def __init__(self, experiments3, taxi_config):
        self.experiments3 = experiments3
        self.taxi_config = taxi_config

        self.experiments3.add_config(
            name='grocery_trust_service_settings',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=_get_trust_service_settings_clauses(),
        )
        self.cashback_notification_available(True)
        self.set_receipt_division(['order'])
        self.grocery_service_token('service_token')
        self.debt_request(True)
        self.cashback_event_delay(CASHBACK_EVENT_DELAY_SECONDS)

        taxi_config.set_values(
            {
                'PERSONAL_WALLET_FIRM_BY_SERVICE': {
                    'grocery': {
                        'RUB': consts.WALLET_SERVICE,
                        'ILS': consts.WALLET_SERVICE,
                    },
                },
                'GROCERY_PAYMENTS_ORIGINATOR_HANDLES': {},
            },
        )

    def without_trust_orders(self, enabled):
        self.experiments3.add_config(
            name='grocery_payments_without_trust_orders',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
        )

    def cashback_event_delay(self, delay_seconds):
        self.experiments3.add_config(
            name='grocery_payments_cashback_event_delay',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'delay_seconds': delay_seconds},
                },
            ],
        )

    def invoice_modification_policy(self, enabled):
        self.experiments3.add_config(
            name='grocery_invoice_modification_policy',
            consumers=['grocery-payments/modification-policy'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
        )

    def set_sbp_flow(self, flow):
        self.experiments3.add_config(
            name='grocery_payments_sbp_flow',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'flow': flow},
                },
            ],
        )

    def set_sbp_banks_meta(self, meta_list):
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

    def drop_unavailable_payment_methods(self, enabled):
        self.experiments3.add_config(
            name='grocery_filter_unavailable_payment_methods',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
        )

    def set_originator(self, originator):
        self.experiments3.add_config(
            name='grocery_payments_originator',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'originator': originator},
                },
            ],
        )

    def set_force_3ds(self, enabled=False):
        self.experiments3.add_config(
            name='grocery_payments_force_3ds',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
        )

    def set_operation_timeout(self, ttl_seconds):
        self.experiments3.add_config(
            name='grocery_payments_operation_timeout',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'ttl_seconds': ttl_seconds},
                },
            ],
        )

    def cashback_notification_available(self, enabled):
        self.experiments3.add_config(
            name='grocery_cashback_notification_available',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always true',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
        )

    def deferred_invoice_modification(self, enabled):
        self.experiments3.add_config(
            name='grocery_payments_deferred_invoice_modification',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always true',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
        )

    def deferred_invoice_clear(self, delta_minutes):
        self.experiments3.add_config(
            name='grocery_payments_deferred_invoice_clear',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always true',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': True, 'delta_minutes': delta_minutes},
                },
            ],
        )

    def set_receipt_division(self, receipt_types: list):
        self.experiments3.add_config(
            name='grocery_receipt_division_settings',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'receipt_types': receipt_types},
                },
            ],
        )

    def grocery_service_token(self, token):
        self.experiments3.add_config(
            name='grocery_service_token',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'token': token},
                },
            ],
        )

    def grocery_merchants(self, merchant_ids: list):
        self.experiments3.add_config(
            name='grocery_merchants',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'merchant_ids': merchant_ids},
                },
            ],
        )

    def debt_request(self, enabled: bool):
        self.experiments3.add_config(
            name='grocery_payments_debt_request',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
        )

    def processing_name(self, processing_name: str):
        self.experiments3.add_config(
            name=PROCESSING_NAME_CONFIG,
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'processing_name': processing_name},
                },
            ],
        )

    def disable_eda_route_data(self, enabled: bool):
        self.experiments3.add_config(
            name='grocery_payments_disable_eda_route_data',
            consumers=['grocery-payments'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
        )

    def add_payments_fallbacks(self, fallbacks, country_iso3=None):
        predicate = {'type': 'true'}
        if country_iso3 is not None:
            predicate = {
                'type': 'eq',
                'init': {
                    'value': country_iso3,
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
            }

        self.experiments3.add_config(
            name='grocery_payments_fallback',
            consumers=['grocery-payments/payments-fallback'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': predicate,
                    'value': {'fallbacks': fallbacks},
                },
            ],
            default_value={'fallbacks': []},
        )

    def grocery_payments_composite_payments_order(self, desired_order):
        self.experiments3.add_config(
            name='grocery_payments_composite_payments_order',
            consumers=['grocery-payments/payment-types-order'],
            default_value={'payment_types_order': desired_order},
        )


@pytest.fixture(name='grocery_payments_configs', autouse=True)
def grocery_payments_configs(experiments3, taxi_config):
    return Context(experiments3, taxi_config)


def trust_settings_payload(country):
    return {
        'billing_service': f'{country.name}-billing-service',
        'product_id': f'{country.name}-product-id',
    }


def trust_settings_versioned(country):
    payload = trust_settings_payload(country)
    payload['billing_service'] += f'_{BILLING_SETTINGS_VERSION}'
    payload['product_id'] += f'_{BILLING_SETTINGS_VERSION}'

    return payload


def _get_trust_settings_default_clauses():
    clauses = []
    for country in consts.COUNTRIES:
        clauses.append(
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
                'value': trust_settings_payload(country),
            },
        )
    return clauses


def _get_trust_service_settings_clauses():
    return [
        {
            'title': 'Settings for Russia with version',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'RUS',
                                'arg_name': 'country_iso3',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': BILLING_SETTINGS_VERSION,
                                'arg_name': 'settings_version',
                                'arg_type': 'string',
                            },
                        },
                    ],
                },
            },
            'value': trust_settings_versioned(models.Country.Russia),
        },
        *_get_trust_settings_default_clauses(),
    ]


GROCERY_MERCHANTS = pytest.mark.experiments3(
    name='grocery_merchants',
    consumers=['grocery-payments'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Settings for android',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': headers.ANDROID_APP_NAME,
                    'arg_name': 'application.name',
                    'arg_type': 'string',
                },
            },
            'value': {'merchant_ids': [consts.MERCHANT_ANDROID]},
        },
        {
            'title': 'Settings for Iphone',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': headers.IPHONE_APP_NAME,
                    'arg_name': 'application.name',
                    'arg_type': 'string',
                },
            },
            'value': {'merchant_ids': [consts.MERCHANT_IPHONE]},
        },
    ],
    default_value={'merchant_ids': []},
    is_config=True,
)

AVS_POST_CODE = 'avs post code'
AVS_STREET_ADDRESS = 'avs street address'

PASS_PARAMS = {
    'avs_data': {
        'avs_post_code': AVS_POST_CODE,
        'avs_street_address': AVS_STREET_ADDRESS,
    },
}

CARDSTORAGE_AVS_DATA = pytest.mark.experiments3(
    name='cardstorage_avs_data',
    consumers=['grocery-payments'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'avs_post_code': AVS_POST_CODE,
                'avs_street_address': AVS_STREET_ADDRESS,
            },
        },
    ],
    is_config=True,
)

TERMINAL_PASS_PARAMS_ENABLED = pytest.mark.experiments3(
    name='terminal_pass_params',
    consumers=['grocery-payments/terminal-pass-params'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'terminal_pass_params_enabled': True},
        },
    ],
)

GROCERY_CURRENCY = pytest.mark.config(
    CURRENCY_ROUNDING_RULES={'RUB': {'grocery-admin': 0.001}},
    CURRENCY_FORMATTING_RULES={'RUB': {'grocery-admin': 2}},
    CURRENCY_KEEP_TRAILING_ZEROS={'RUB': {'grocery-admin': True}},
)


PROCESSING_META = pytest.mark.config(
    GROCERY_PAYMENTS_PROCESSING_META={
        consts.PAYTURE_TERMINAL_ID: {'name': consts.PAYTURE_NAME},
        consts.SBERBANK_TERMINAL_ID: {'name': consts.SBERBANK_NAME},
    },
)
