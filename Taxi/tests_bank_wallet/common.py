MCC_CATEGORIES = {'4321': 'TRANSPORT'}

MERCHANT_NAMES = {'Yandex.Eda': 'Яндекс.Еда'}

LONG_KEY = (
    'transactions.card_description_template.with_payment_system_and_number'
)

TANKER_KEYS = {
    'transaction_status_message': {
        'clear': 'transactions.status_message.clear',
        'hold': 'transactions.status_message.hold',
        'cancel': 'transactions.status_message.cancel',
        'fail': 'transactions.status_message.fail',
    },
    'transaction_type_message': {
        'purchase': 'transactions.type_name.purchase',
        'refund': 'transactions.type_name.refund',
        'transfer': 'transactions.type_name.transfer',
    },
    'payment_system_name': {
        'mir': 'transactions.payment_system_name.mir',
        'mastercard': 'transactions.payment_system_name.mastercard',
        'visa': 'transactions.payment_system_name.visa',
        'american_express': (
            'transactions.payment_system_name.american_express'
        ),
    },
    'card_description_template': {
        'without_params': (
            'transactions.card_description_template.without_params'
        ),
        'with_payment_system': (
            'transactions.card_description_template.with_payment_system'
        ),
        'with_payment_system_and_number': LONG_KEY,
        'with_number': 'transactions.card_description_template.with_number',
        'number_arg_name': 'number',
        'payment_system_arg_name': 'payment_type',
    },
    'extra_mcc_category': 'transactions.extra_mcc_category',
}


def get_headers():
    return {
        'X-Yandex-BUID': '1',
        'X-Yandex-UID': '1',
        'X-YaBank-PhoneID': 'phone_id1',
        'X-YaBank-SessionUUID': '1',
        'X-Ya-User-Ticket': '1',
        'X-Request-Language': 'ru',
    }


def get_support_headers():
    return {'X-Bank-Token': 'allow'}


def build_balance(amount, currency):
    return {'amount': amount, 'currency': currency}


def build_limit(threshold, currency, remaining, period):
    return {
        'period_start': '2020-08-01T00:00:00+00:00',
        'period': period,
        'threshold': {'amount': threshold, 'currency': currency},
        'remaining': {'amount': remaining, 'currency': currency},
    }


def build_wallet(wallet_id, balance, debit_limit, credit_limit):
    return {
        'id': wallet_id,
        'public_agreement_id': 'test_agreement_id',
        'balance': balance,
        'debit_limit': debit_limit,
        'credit_limit': credit_limit,
    }


def build_wallet_balance(wallet_id, balance, payment_methods):
    if payment_methods:
        result = {
            'wallet_id': wallet_id,
            'public_agreement_id': 'test_agreement_id',
            'balance': balance,
            'payment_method_ids': payment_methods,
        }
    else:
        result = {
            'wallet_id': wallet_id,
            'public_agreement_id': 'test_agreement_id',
            'balance': balance,
        }
    return result
