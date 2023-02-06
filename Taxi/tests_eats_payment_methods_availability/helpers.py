import copy
import typing

from . import consts

DEFAULT_EXTERNAL_PAYMENT_ID = 'c964a582b3b4b3dcd514ab1914a7d2a8'

DEFAULT_TRANSACTION = {
    'created': '2020-08-14T17:39:50.265000+03:00',
    'external_payment_id': DEFAULT_EXTERNAL_PAYMENT_ID,
    'cleared': '2020-08-14T17:39:50.265000+03:00',
    'fiscal_receipt_url': (
        'https://trust.yandex.ru/checks/abc/receipts/def?mode=mobile'
    ),
    'held': '2020-08-14T17:40:01.053000+03:00',
    'initial_sum': [{'amount': '5.00', 'item_id': 'big_mac'}],
    'operation_id': 'foo:12345',
    'payment_method_id': '123',
    'payment_type': 'card',
    'refunds': [],
    'status': 'hold_success',
    'sum': [{'amount': '5.00', 'item_id': 'big_mac'}],
    'technical_error': False,
    'terminal_id': '57000176',
    'updated': '2020-08-14T17:40:01.053000+03:00',
}

DEFAULT_OPERATION = {
    'created': '2020-08-14T17:39:49.663000+03:00',
    'id': 'create:12345',
    'status': 'done',
    'sum_to_pay': [
        {
            'items': [{'amount': '5.00', 'item_id': 'big_mac'}],
            'payment_type': 'card',
        },
    ],
}

EATS_PAYMENT_SERVICE = '645'
GROCERY_PAYMENT_SERVICE = '662'
TEST_CURRENCY = 'RUB'


def sort_items(items_by_payment_type):
    return [
        {
            'payment_type': payment_items['payment_type'],
            'items': sorted(
                payment_items['items'], key=lambda item: item['item_id'],
            ),
        }
        for payment_items in items_by_payment_type
    ]


def make_operation(**extra) -> dict:
    return {**DEFAULT_OPERATION, **extra}


def make_callback_transaction(status: str, **extra) -> dict:
    return {
        'external_payment_id': DEFAULT_EXTERNAL_PAYMENT_ID,
        'payment_type': 'card',
        'status': status,
        **extra,
    }


def make_wallet_payload(
        cashback_service: str,
        order_id: str,
        wallet_id: str,
        service_id=consts.EATS_CASHBACK_SERVICE_ID,
) -> dict:

    result = {
        'service_id': service_id,
        'cashback_service': cashback_service,
        'order_id': order_id,
        'has_plus': 'true',
        'wallet_id': wallet_id,
    }

    if (
            cashback_service == 'lavka'
            and service_id == consts.GROCERY_CASHBACK_SERVICE_ID
    ):
        result['ticket'] = 'NEWSERVICE-1322'

    return result


def map_service_to_wallet_service(service: str) -> str:
    if service == 'eats':
        return 'eda'

    if service == 'grocery':
        return 'lavka'

    raise RuntimeError('unknown service')


def make_refund(refund_sum: typing.List[dict], operation_id: str, **kwargs):
    return {
        'created': '2020-08-14T17:39:50.265000+03:00',
        'updated': '2020-08-14T17:39:50.265000+03:00',
        'sum': refund_sum,
        'status': 'refund_success',
        'operation_id': operation_id,
        **kwargs,
    }


def _get_item_id(idx):
    return f'item_id_{idx}'


def get_originator_config(
        unavailable_payment_types=None,
        debt_enabled=True,
        cashback_enabled=True,
        maintenance_available=True,
        stq_postback='eda_order_processing_payment_events_callback',
        originator_name=None,
        originator_debt_enabled=None,
):
    if unavailable_payment_types is None:
        unavailable_payment_types = []

    result = {
        'originators': [],
        'default_originator_config': {
            'name': 'default',
            'stq_postback': stq_postback,
            'unavailable_payment_types': unavailable_payment_types,
            'debt_enabled': debt_enabled,
            'cashback_enabled': cashback_enabled,
            'maintenance_available': maintenance_available,
        },
    }

    if originator_name is not None and originator_debt_enabled is not None:
        config = copy.deepcopy(result['default_originator_config'])
        config['name'] = originator_name
        config['debt_enabled'] = originator_debt_enabled
        result['originators'].append(config)
    return result


# pylint: disable=invalid-name
def make_terminal_pass_params_experiment(enabled) -> dict:
    return {
        'name': 'terminal_pass_params',
        'consumers': ['eats-payments/terminal-pass-params'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {'terminal_pass_params_enabled': enabled},
            },
        ],
    }


def make_terminal_pass_params_experiment2(enabled) -> dict:
    return {
        'name': 'terminal_pass_params',
        'consumers': ['eats-payments/terminal-pass-params'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'value': {'terminal_pass_params_enabled': enabled},
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'yandex_uid',
                                    'arg_type': 'string',
                                    'value': '100500',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'merchant',
                                    'arg_type': 'string',
                                    'value': 'eda',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'business',
                                    'arg_type': 'string',
                                    'value': 'restaurant',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'currency',
                                    'arg_type': 'string',
                                    'value': 'RUB',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'payment_type',
                                    'arg_type': 'string',
                                    'value': 'card',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
            },
        ],
    }


def make_pass_afs_params_experiment(  # pylint: disable=invalid-name
        pass_afs_params, clause_predicate=None,
) -> dict:
    return {
        'name': 'eats_payments_pass_afs_params',
        'consumers': ['eats-payments/pass_afs_params'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': clause_predicate or {'type': 'true'},
                'value': {'pass_afs_params': pass_afs_params},
            },
        ],
        'default_value': {'pass_afs_params': False},
    }


def make_pass_3ds_params_experiment(  # pylint: disable=invalid-name
        pass_3ds_availability_true, clause_predicate=None,
) -> dict:
    return {
        'name': 'eats_payments_pass_3ds_params',
        'consumers': ['eats-payments/pass_3ds_params'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': clause_predicate or {'type': 'true'},
                'value': {
                    'pass_3ds_availability_true': pass_3ds_availability_true,
                    'pass_3ds_availability_true_for_not_available_card_only': (
                        False
                    ),
                    'show_not_available_cards_if_available_cards_exists': True,
                    'pass_developer_payload': pass_3ds_availability_true,
                },
            },
        ],
        'default_value': {'pass_3ds_availability_true': False},
    }


def make_card_service_tokens_experiment() -> dict:
    return {
        'name': 'eats_payment_methods_availability_card_service_tokens',
        'consumers': ['eats-payment-methods-availability/card-service-tokens'],
        'clauses': [],
        'default_value': {
            'service_token': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
            'binding_service_token': (
                'taxifee_8c7078d6b3334e03c1b4005b02da30f4'
            ),
        },
    }


def make_card_attributes_overwrite_experiment() -> dict:
    return {
        'name': 'eats_payment_methods_availability_card_attributes_overwrite',
        'consumers': [
            'eats-payment-methods-availability/card-attributes-overwrite',
        ],
        'clauses': [],
        'default_value': {
            'name': 'yandex-bank',
            'system': 'YandexBank',
            'number': 'yandex-bank-number-overwrite',
            'short_title': 'yandex-bank',
        },
    }


def make_payment_tracking_experiment() -> dict:
    return {
        'name': 'eats_payment_methods_availability_payment_tracking',
        'consumers': ['eats-payment-methods-availability/payment-tracking'],
        'clauses': [],
        'default_value': {
            'card': {'enabled': True, 'errorDelay': 5},
            'sbp': {
                'sbpSettings': {
                    'members': [
                        {
                            'schema': 'bank100000000111',
                            'logoURL': 'https://logo.ru/logo.png',
                            'bankName': 'Сбербанк',
                            'packageName': 'ru.sberbankmobile',
                        },
                    ],
                    'continueButtonDelay': 10,
                },
                'enabled': True,
                'errorDelay': 6,
            },
        },
    }


def make_apple_pay_tokens_experiment(  # pylint: disable=invalid-name
        merchant_ids,
) -> dict:
    result = {
        'merchant_ids': merchant_ids,
        'service_token': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
    }

    return {
        'name': 'eats_payment_methods_availability_apple_pay_tokens',
        'consumers': ['eats-payment-methods-availability/apple-pay-tokens'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': result,
            },
        ],
    }


def make_google_pay_tokens_experiment(  # pylint: disable=invalid-name
        merchant_id=None, service_token=None,
) -> dict:
    result = {}
    if merchant_id is not None:
        result['merchant_id'] = merchant_id

    if service_token is not None:
        result['service_token'] = service_token

    return {
        'name': 'eats_payment_methods_availability_google_pay_tokens',
        'consumers': ['eats-payment-methods-availability/google-pay-tokens'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': result,
            },
        ],
        'default_value': result,
    }
