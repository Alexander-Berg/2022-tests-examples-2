import pytest
from . import consts


PERSONAL_WALLET_SERVICE = {'eats': '1', 'grocery': '2'}

PERSONAL_WALLET_FIRM_BY_SERVICE = pytest.mark.config(
    PERSONAL_WALLET_FIRM_BY_SERVICE={
        'eats': {'RUB': PERSONAL_WALLET_SERVICE['eats']},
        'grocery': {'RUB': PERSONAL_WALLET_SERVICE['grocery']},
    },
)

CASHBACK_CONFIG = pytest.mark.config(
    EATS_PAYMENTS_ORIGINATOR_SETTINGS={
        'default_originator_config': {
            'cashback_enabled': True,
            'debt_enabled': True,
            'maintenance_available': False,
            'name': 'default',
            'stq_postback': 'eda_order_processing_payment_events_callback',
            'unavailable_payment_types': [],
        },
        'originators': [
            {
                'cashback_enabled': True,
                'debt_enabled': False,
                'maintenance_available': True,
                'name': 'eats-corp-orders',
                'need_to_send_billing_notification': False,
                'stq_postback': 'eats_corp_orders_payment_callback',
                'unavailable_payment_types': [],
            },
        ],
    },
    EATS_PAYMENTS_ORIGINATORS={
        'fallback_to_originator_settings': (
            consts.FALLBACK_TO_ORIGINATOR_SETTINGS
        ),
        'originators': [
            {
                'name': 'eats-corp-orders',
                'allowed_complement_payment_types': ['personal_wallet'],
                'allowed_payment_types': [
                    'card',
                    'applepay',
                    'googlepay',
                    'corp',
                    'personal_wallet',
                    'postpayment',
                    'sbp',
                ],
                'postback_stq_name': 'eats_corp_orders_payment_callback',
            },
        ],
    },
)

COMPLEMENT_CONFIG = pytest.mark.config(
    EATS_PAYMENTS_ORIGINATOR_SETTINGS={
        'default_originator_config': {
            'cashback_enabled': True,
            'debt_enabled': True,
            'maintenance_available': False,
            'name': 'default',
            'stq_postback': 'eda_order_processing_payment_events_callback',
            'unavailable_payment_types': [],
        },
        'originators': [
            {
                'available_complement_payment_types': [
                    'corp',
                    'personal_wallet',
                ],
                'cashback_enabled': False,
                'debt_enabled': False,
                'maintenance_available': True,
                'name': 'eats-corp-orders',
                'need_to_send_billing_notification': False,
                'stq_postback': 'eats_corp_orders_payment_callback',
                'unavailable_payment_types': [],
            },
        ],
    },
    EATS_PAYMENTS_ORIGINATORS={
        'fallback_to_originator_settings': (
            consts.FALLBACK_TO_ORIGINATOR_SETTINGS
        ),
        'originators': [
            {
                'name': 'eats-corp-orders',
                'allowed_complement_payment_types': [
                    'corp',
                    'personal_wallet',
                ],
                'allowed_payment_types': [
                    'card',
                    'applepay',
                    'googlepay',
                    'corp',
                    'personal_wallet',
                    'postpayment',
                    'sbp',
                ],
                'postback_stq_name': 'eats_corp_orders_payment_callback',
            },
        ],
    },
)

NO_COMPLEMENT_CONFIG = pytest.mark.config(
    EATS_PAYMENTS_ORIGINATOR_SETTINGS={
        'default_originator_config': {
            'cashback_enabled': True,
            'debt_enabled': True,
            'maintenance_available': False,
            'name': 'default',
            'stq_postback': 'eda_order_processing_payment_events_callback',
            'unavailable_payment_types': [],
        },
        'originators': [
            {
                'available_complement_payment_types': [],
                'cashback_enabled': False,
                'debt_enabled': False,
                'maintenance_available': True,
                'name': 'eats-corp-orders',
                'need_to_send_billing_notification': False,
                'stq_postback': 'eats_corp_orders_payment_callback',
                'unavailable_payment_types': [],
            },
        ],
    },
    EATS_PAYMENTS_ORIGINATORS={
        'fallback_to_originator_settings': (
            consts.FALLBACK_TO_ORIGINATOR_SETTINGS
        ),
        'originators': [
            {
                'name': 'eats-corp-orders',
                'allowed_payment_types': [
                    'card',
                    'applepay',
                    'googlepay',
                    'corp',
                    'personal_wallet',
                    'postpayment',
                    'sbp',
                ],
                'postback_stq_name': 'eats_corp_orders_payment_callback',
            },
        ],
    },
)

DEBT_CONFIG = pytest.mark.config(
    EATS_PAYMENTS_ORIGINATOR_SETTINGS={
        'default_originator_config': {
            'cashback_enabled': True,
            'debt_enabled': True,
            'maintenance_available': False,
            'name': 'default',
            'stq_postback': 'eda_order_processing_payment_events_callback',
            'unavailable_payment_types': [],
        },
        'originators': [
            {
                'cashback_enabled': False,
                'debt_enabled': True,
                'maintenance_available': True,
                'name': 'eats-corp-orders',
                'need_to_send_billing_notification': False,
                'stq_postback': 'eats_corp_orders_payment_callback',
                'unavailable_payment_types': [],
            },
        ],
    },
    EATS_PAYMENTS_ORIGINATORS={
        'fallback_to_originator_settings': (
            consts.FALLBACK_TO_ORIGINATOR_SETTINGS
        ),
        'originators': [
            {
                'name': 'eats-corp-orders',
                'allowed_payment_types': [
                    'card',
                    'applepay',
                    'googlepay',
                    'corp',
                    'personal_wallet',
                    'postpayment',
                    'sbp',
                ],
                'enable_debt': True,
                'postback_stq_name': 'eats_corp_orders_payment_callback',
            },
        ],
    },
)

CASH_CONFIG = pytest.mark.config(
    EATS_PAYMENTS_ORIGINATOR_SETTINGS={
        'default_originator_config': {
            'cashback_enabled': True,
            'debt_enabled': False,
            'maintenance_available': False,
            'name': 'default',
            'stq_postback': 'eda_order_processing_payment_events_callback',
            'unavailable_payment_types': ['cash'],
        },
        'originators': [
            {
                'cashback_enabled': False,
                'debt_enabled': False,
                'maintenance_available': True,
                'name': 'eats-corp-orders',
                'need_to_send_billing_notification': False,
                'stq_postback': 'eats_corp_orders_payment_callback',
                'unavailable_payment_types': [
                    'card',
                    'applepay',
                    'googlepay',
                    'corp',
                    'personal_wallet',
                    'postpayment',
                    'sbp',
                ],
            },
        ],
    },
    EATS_PAYMENTS_ORIGINATORS={
        'fallback_to_originator_settings': (
            consts.FALLBACK_TO_ORIGINATOR_SETTINGS
        ),
        'originators': [
            {
                'name': 'eats-corp-orders',
                'allowed_payment_types': ['cash'],
                'postback_stq_name': 'eats_corp_orders_payment_callback',
            },
        ],
    },
)

DISABLED_CONFIG = pytest.mark.config(
    EATS_PAYMENTS_ORIGINATOR_SETTINGS={
        'default_originator_config': {
            'cashback_enabled': True,
            'debt_enabled': True,
            'maintenance_available': True,
            'name': 'default',
            'stq_postback': 'eda_order_processing_payment_events_callback',
            'unavailable_payment_types': [],
        },
        'originators': [
            {
                'cashback_enabled': False,
                'debt_enabled': True,
                'maintenance_available': False,
                'name': 'eats-corp-orders',
                'need_to_send_billing_notification': False,
                'stq_postback': 'eats_corp_orders_payment_callback',
                'unavailable_payment_types': [],
            },
        ],
    },
    EATS_PAYMENTS_ORIGINATORS={
        'fallback_to_originator_settings': (
            consts.FALLBACK_TO_ORIGINATOR_SETTINGS
        ),
        'originators': [
            {
                'name': 'eats-corp-orders',
                'allowed_payment_types': [
                    'card',
                    'applepay',
                    'googlepay',
                    'corp',
                    'personal_wallet',
                    'postpayment',
                    'sbp',
                ],
                'enable_create_order': False,
                'postback_stq_name': 'eats_corp_orders_payment_callback',
            },
        ],
    },
)

MAPPING_CONFIG = pytest.mark.config(
    EATS_PAYMENTS_ORIGINATORS={
        'fallback_to_originator_settings': False,
        'originators': [
            {
                'name': 'persey-payments',
                'allowed_payment_types': [
                    'card',
                    'applepay',
                    'googlepay',
                    'postpayment',
                    'sbp',
                ],
                'postback_stq_name': 'persey_payments_eats_callback',
            },
        ],
        'name_mappings': [
            {'from_name': 'eats-corp-orders', 'to_name': 'persey-payments'},
        ],
    },
)

DISABLE_BADGE_CONFIG = pytest.mark.config(
    EATS_PAYMENTS_ORIGINATORS={
        'fallback_to_originator_settings': False,
        'originators': [
            {
                'name': 'eats-corp-orders',
                'allowed_payment_types': [
                    'card',
                    'applepay',
                    'googlepay',
                    'corp',
                    'personal_wallet',
                    'postpayment',
                    'sbp',
                ],
                'enable_billing_notification': False,
                'postback_stq_name': 'eats_corp_orders_payment_callback',
            },
        ],
    },
)
