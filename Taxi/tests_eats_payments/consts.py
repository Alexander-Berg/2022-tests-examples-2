TRANSACTION_TERMINATE_STATUSES = [
    'hold_success',
    'hold_fail',
    'clear_success',
    'clear_fail',
]

OPERATION_STATUSES = ['done', 'failed']

CARD_PAYMENT_TYPE = 'card'
CASH_PAYMENT_TYPE = 'cash'

CLIENT_PAYMENT_TYPES = ['card', 'applepay', 'googlepay', 'corp']
PAYMENT_TYPES = ['card', 'applepay', 'googlepay', 'corp', 'badge', 'sbp']

DEFAULT_SERVICE = 'eats'
EDA_CORE_ORIGINATOR = 'eda_core'
CORP_ORDER_ORIGINATOR = 'eats-corp-orders'
INTEGRATION_OFFLINE_ORDERS_ORIGINATOR = 'eats-integration-offline-orders'
PERSEY_ORIGINATOR = 'persey-payments'
DEFAULT_ORIGINATOR = EDA_CORE_ORIGINATOR
SERVICE_NAME = 'eats-payments'
FALLBACK_TO_ORIGINATOR_SETTINGS = False

PERSONAL_WALLET = 'personal_wallet'

TEST_ORDER_ID = 'test_order'
TEST_PAYMENT_ID = '123'

# Generated via `tvmknife unittest service -s 110 -d 2345`
MOCK_EDA_CORE_TICKET = '3:serv:CBAQ__________9_IgUIbhCpEg:SUPYimePFwHymiD8DoNqwElNlgVl2kRwwBFRQo69TrUbJA_gMhowtZ5NkYvMfmMtkEnFZ-WqYrzWUxjPx4hZaqkOaAQzkagDtq2CtYkuQTGKsbCGWeJ7NmM2VDqoIvLRMhC2wsYQhXsZvumzgw0VfZHAhO_umo0riTyPA_5GZn4'

# Generated via `tvmknife unittest service -s 111 -d 2021618`
MOCK_EATS_CORP_ORDERS_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxCpEg:OVnJaXrr4'
    'ipvnQywUhlKsMyixVP0TnZQYAosaOkaTwtBzb41fl9BW'
    'HTiyJPXt4lrHCpHWya2WKsErZU0jm-ThF4ZZlqjitbhbD'
    'UZKdVFMuQ-4NGINltUZqSjGLEiEje-3aP73zRK_J9x8vR3'
    '72A4S7XKNa-MKj2rHF-9Wbj40yg'
)

BASE_HEADERS = {
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Uid': '100500',
    'Accept-Language': '',
    'X-Remote-IP': '127.0.0.1',
    'X-Login-Id': 'test_login_id',
}

LONG_ITEM_TITLE = (
    'Очень длинный текст, который специально написан так '
    'и занимает немного больше, чем 128 символов, чтобы '
    'посмотреть как оно обрежется'
)

LONG_ITEM_TITLE_TRIMMED = (
    'Очень длинный текст, который специально написан так '
    'и занимает немного больше, чем 128 символов, чтобы '
    'посмотреть как оно обр...'
)

NOT_LONG_ITEM_TITLE = (
    'Не очень длинный текст, который специально написан так, '
    'что занимает ровно 128 символов, чтобы посмотреть, что '
    'оно не обрежется.'
)

EATS_CASHBACK_SERVICE_ID = '645'
GROCERY_CASHBACK_SERVICE_ID = '662'

BUSINESS = 'restaurant'
DEFAULT_BUSINESS_CONFIG = {
    'is_enabled': True,
    'businesses': [
        {
            'business': 'restaurant',
            'terminal_business': 'restaurant',
            'billing_service': 'food_payment',
            'specification': [],
        },
        {
            'business': 'shop',
            'terminal_business': 'retail',
            'billing_service': 'food_payment',
            'specification': [],
        },
        {
            'business': 'store',
            'terminal_business': 'retail',
            'billing_service': 'food_payment',
            'specification': [],
        },
        {
            'business': 'test',
            'terminal_business': 'retail',
            'billing_service': 'food_payment_test',
            'specification': [],
        },
        {
            'business': 'zapravki',
            'terminal_business': 'retail',
            'billing_service': 'food_payment',
            'specification': [],
        },
        {
            'business': 'zapravki',
            'terminal_business': 'retail',
            'billing_service': 'food_fuel_payment',
            'specification': ['rosneft'],
        },
    ],
}
