import datetime

UTC_TZ = datetime.timezone.utc
NOW_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=UTC_TZ)
NOW = NOW_DT.isoformat()

CART_ID = '28fe4a6e-c00d-45c1-a34e-6329c4a4e329'
ORDER_ID = 'some-order-id'
YANDEX_UID = 'some-yandex-uid'
APPLICATION_ID = 'D7120EAA-75D6-48F6-A95A-977E0ACC72F7'
CIBUS_API_SECRET = 'cibus-secret-key'

TRANSACTION_ID = 'transaction-id'

REDIRECT_URL = 'https://qav1.mysodexo.co.il/Auth.aspx'
DEFAULT_TOKEN = '61f185ff2195edcd8cf3318a_GBRsSIY8d845u2rHKRz1'
DEAL_ID = 12345678

ERROR_TECH = 'payment_gateway_technical_error'
ERROR_LOGIC = 'logical_error'
