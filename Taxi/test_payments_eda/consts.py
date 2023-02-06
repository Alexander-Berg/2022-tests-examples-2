from taxi.clients import experiments3

DEFAULT_YANDEX_UID = 'default_yandex_uid'
DEFAULT_USER_ID = 'default_user_id'
DEFAULT_CLIENT_APPLICATION = experiments3.ClientApplication(
    application='web', version='2.0.0',
)
USER_ORIGIN_TAXI = 'taxi'

DEFAULT_COMPLEMENTS = [
    {
        'payment_method': 'personal_wallet',
        'payment_method_id': 'wallet_id/1234567890',
    },
]
LOCATION = [30.313119, 59.931513]
USER_IP = '1.1.1.1'
VALID_WALLET_ID = 'wallet_id/1234567890'
DEFAULT_UUID = '00000000-0000-0000-0000-000000000002'
DEFAULT_AMOUNT = '123.43'

PERSONAL_TIN_ID = 'b9bce8b7f41d4b7d8b27cb588121a9f0'

GROCERY_ORDER_ID = 'bfd7526fa5d74eae9e5c034d40235be0-grocery'

INVOICE_VERSION = 10
DEFAULT_RETRIEVE_RESPONSE = {
    'cleared': [],
    'currency': 'RUB',
    'debt': [],
    'held': [],
    'id': 'order-id',
    'invoice_due': '2018-07-20T14:00:00.0000+0000',
    'created': '2018-07-20T14:00:00.0000+0000',
    'operation_info': {
        'originator': 'processing',
        'priority': 1,
        'version': INVOICE_VERSION,
    },
    'operations': [],
    'payment_types': ['card'],
    'status': 'init',
    'sum_to_pay': [
        {
            'items': [
                {'amount': '100.23', 'item_id': 'item-id-1'},
                {'amount': '100.27', 'item_id': 'item-id-2'},
            ],
            'payment_type': 'card',
        },
    ],
    'transactions': [],
    'yandex_uid': DEFAULT_YANDEX_UID,
}

EATS_CASHBACK_SERVICE_ID = '645'
GROCERY_CASHBACK_SERVICE_ID = '662'
