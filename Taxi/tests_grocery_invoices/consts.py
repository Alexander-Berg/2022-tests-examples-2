import datetime

EASY_COUNT_PAYMENT = 320
EASY_COUNT_REFUND = 330
EASY_COUNT_LINK = 'https://url.pdf'
EASY_COUNT_DOC_NUMBER = '30024'
EASY_COUNT_DOC_UUID = '7aa39782-c40c-49ea-9083-03edbb5e89a4'
EASY_COUNT_USER_AGENT = 'curl/7.64.1'
# From service.yaml
EASY_COUNT_TOKEN = 'secret-easy-count'

DEFAULT_PAYMENT_METHOD_ID = 'card-xc0f55c4b0a350c74502f4e92'
DEFAULT_LAST_4_DIGITS = '2809'
DEFAULT_PAYMENT_METHOD = {'type': 'card', 'id': DEFAULT_PAYMENT_METHOD_ID}

ORDER_ADDRESS = 'some address'

DEFAULT_YANDEX_UID = '991231231'
DEFAULT_HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-Yandex-Uid': DEFAULT_YANDEX_UID,
}

CUSTOMER_NAME = 'mickey santa mouse claus'
PASSPORT_CUSTOMER_NAME = 'Козьма Прутков'
DEVELOPER_EMAIL = 'grocery@yandex-team.ru'
GROCERY_USER_UUID = 'grocery-user-uuid'

IDEMPOTENCY_TOKEN = 'xxx-token-111'

ORDER_ID = 'order_id'
SHORT_ORDER_ID = 'short_order_id'
POLLING_ID = 'polling-id'
CART_ID = '28fe4a6e-c00d-45c1-a34e-6329c4a4e329'

TYPE_PAYMENT = 'payment'
TYPE_REFUND = 'refund'

NOW_YEAR_LAST_2_DIGITS = 21
NOW_MONTH = 10
NOW_DAY = 22
NOW = f'20{NOW_YEAR_LAST_2_DIGITS}-{NOW_MONTH}-{NOW_DAY}T14:17:06+00:00'
NOW_DT = datetime.datetime(
    2000 + NOW_YEAR_LAST_2_DIGITS, NOW_MONTH, NOW_DAY, 14, 17, 6,
)

EXTERNAL_PAYMENT_ID = 'external_payment_id'

USER_PHONE = '+79160125597'

TIPS_ITEM_ID = 'tips-item-123'
SERVICE_FEE_ITEM_ID = 'service-fee-item-123'
DELIVERY_ITEM_ID = 'delivery-item-123'

COURIER_TIN_ID = 'courier-tin-id'
COURIER_TIN = 'courier-tin-from-personal'
DELIVERY_TAX = '0'
SELFEMPLOYED_TAX = '-1'
DELIVERY_RECEIPT_RU = 'русская доставка'
DELIVERY_RECEIPT_HE = 'delivery-he-title'
DELIVERY_RECEIPT_FR = 'delivery-fr-title'
DELIVERY_RECEIPT_EN = 'delivery-en-title'
TIPS_RECEIPT_RU = 'русские чаевые'
TIPS_RECEIPT_HE = 'tips-he-title'
TIPS_RECEIPT_FR = 'tips-fr-title'
TIPS_RECEIPT_EN = 'tips-en-title'
SERVICE_FEE_RECEIPT_RU = 'русский сервисный сбор'
SERVICE_FEE_RECEIPT_HE = 'service-fee-he-title'
SERVICE_FEE_RECEIPT_FR = 'service-fee-fr-title'
SERVICE_FEE_RECEIPT_EN = 'service-fee-en-title'
EXPAT_PAYMENT_COUPON_RU = 'экспатный заказ платеж'
EXPAT_REFUND_COUPON_RU = 'экспатный заказ возврат'

DEFAULT_VAT = '17'
RUSSIA_VAT = '20'
ISRAEL_VAT = '17'
FRANCE_VAT = '20'
BRITAIN_VAT = '20'
RSA_VAT = '20'
ZERO_VAT = '0'

SELF_EMPLOYED_COURIER = {
    'id': 'courier-id-1',
    'transport_type': 'pedestrian',
    'vat': DELIVERY_TAX,
    'personal_tin_id': COURIER_TIN_ID,
}

DELIVERY_SERVICE_COURIER = {
    'id': 'courier-id-1',
    'transport_type': 'pedestrian',
    'vat': DELIVERY_TAX,
    'personal_tin_id': COURIER_TIN_ID,
    'organization_name': 'test-organization',
}

EATS_CORE_SOURCE = 'eats_core'
FNS_SOURCE = 'fns'
EASY_COUNT_SOURCE = 'easy_count'
FRANCE_DOCUMENT_TEMPLATOR_SOURCE = 'france_document_templator'
GREAT_BRITAIN_DOCUMENT_TEMPLATOR_SOURCE = 'great_britain_document_templator'
RSA_DOCUMENT_TEMPLATOR_SOURCE = 'rsa_document_templator'

ORDER_RECEIPT_DATA_TYPE = 'order'
TIPS_RECEIPT_DATA_TYPE = 'tips'
DELIVERY_RECEIPT_DATA_TYPE = 'delivery'
HELPING_HAND_RECEIPT_DATA_TYPE = 'helping_hand'

TEMPLATE_VALUE_FIRST = '$VALUE$ $SIGN$'
TEMPLATE_SIGN_FIRST = '$SIGN$ $VALUE$'

EATS_CORE_RECEIPTS = 'eats_core_receipts'
EATS_RECEIPTS = 'eats_receipts'

OPERATION_ID = 'operation_id'
TERMINAL_ID = 'terminal_id'
PAYMENT_FINISHED = '1999-02-10T12:31:24.123+00:00'

TASK_ID = 'task_id'
PAIRED_TASK_ID = 'paired_task_id'


PRODUCTS = [
    {'item_id': 'item-id-1', 'price': 10, 'quantity': 1},
    {'item_id': 'item-id-2', 'price': 15, 'quantity': 2},
    {'item_id': 'item-id-3', 'price': 20.51, 'quantity': 4},
]

DELIVERY_AMOUNT = 5
TIPS_AMOUNT = 6
SERVICE_FEE_AMOUNT = 29

EXPAT_FLOW_VERSION = 'exchange_currency'

DEPOT_ID = '60287'
GROCERY_TIN = '9718101499'
