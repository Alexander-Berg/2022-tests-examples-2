import datetime

NOW_TZ = datetime.timezone.utc
NOW_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=NOW_TZ)
NOW = NOW_DT.isoformat()

ORDER_ID = 'order_id'
DEBT_ID = 'debt_id'
INVOICE_ID = ORDER_ID
YANDEX_UID = '123456789'
PERSONAL_PHONE_ID = 'personal_phone_id'
SERVICE = 'grocery'
CURRENCY = 'RUB'
COUNTRY = 'Russia'
COUNTRY_ISO3 = 'RUS'

SATURN_SERVICE_RUSSIA = 'grocery'
SATURN_SERVICE_ISRAEL = 'lavka_isr'

SATURN_FORMULA_THRESHOLD = 0.5

DEBT_IDEMPOTENCY_TOKEN = 'debt_idempotency_token'
DEBT_OPERATION_ID = 'debt/collect/1/2'

USER_INFO = dict(yandex_uid=YANDEX_UID, personal_phone_id=PERSONAL_PHONE_ID)
ORDER_INFO = dict(order_id=ORDER_ID, country_iso3=COUNTRY_ISO3)

INVOICE_INFO = {
    'id': INVOICE_ID,
    'id_namespace': 'grocery',
    'transactions_installation': 'eda',
    'originator': 'grocery',
}

OPERATION_TYPE = 'create'
OPERATION_ID = 'operation_id'
OPERATION_PRIORITY = 1

DEBT_REASON_CODE = 'some debt reason code'
DEBT_NULL_STRATEGY = dict(kind='null', metadata={})

SATURN_FORMULA_ID = '2447857274_66'
