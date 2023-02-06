TRANSACTION_TERMINATE_STATUSES = [
    'hold_success',
    'hold_fail',
    'clear_success',
    'clear_fail',
]

OPERATION_STATUSES = ['done', 'failed']

CARD_PAYMENT_TYPE = 'card'

DEFAULT_LOC_POINT = [37.534301, 55.750001]

CLIENT_PAYMENT_TYPES = ['card', 'applepay', 'googlepay', 'corp']
PAYMENT_TYPES = ['card', 'applepay', 'googlepay', 'corp', 'badge']

DEFAULT_SERVICE = 'eats'
DEFAULT_ORIGINATOR = 'eda_core'

PERSONAL_WALLET = 'personal_wallet'

BASE_HEADERS = {
    'X-Yandex-Uid': '100500',
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
