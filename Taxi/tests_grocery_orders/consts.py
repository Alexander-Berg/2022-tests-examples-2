import datetime

# pylint: disable=import-error
from grocery_mocks.models import country as country_models
import pytest

from . import headers


ITEM_ID = 'item-id'
PARSEL_ITEM_ID = f'{ITEM_ID}:st-pa'

UTC_TZ = datetime.timezone.utc
NOW = '2020-03-13T07:19:00+00:00'
NOW_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=UTC_TZ)

APP_IPHONE = 'lavka_iphone'
APP_WEB = 'web'
DELI_IPHONE = 'yangodeli_iphone'
DELI_ANDROID = 'yangodeli_android'
YANGO_IPHONE = 'mobileweb_yango_iphone'
YANGO_ANDROID = 'mobileweb_yango_android'

DEFAULT_DISPATCH_ID = '1234'

ISR_TIPS_PROPOSALS = ['5', '7', '10']
RUS_TIPS_PROPOSALS = ['49', '99', '149']

ISR_TIPS_PROPOSAL_TEMPLATES = [
    '5 $SIGN$$CURRENCY$',
    '7 $SIGN$$CURRENCY$',
    '10 $SIGN$$CURRENCY$',
]
RUS_TIPS_PROPOSAL_TEMPLATES = [
    '49 $SIGN$$CURRENCY$',
    '99 $SIGN$$CURRENCY$',
    '149 $SIGN$$CURRENCY$',
]

TIPS_AMOUNT = 149.00
TIPS_AMOUNT_STR = '149'

COUNTRIES = pytest.mark.parametrize(
    'country', [country_models.Country.Russia, country_models.Country.Israel],
)

DEFAULT_DEPOT_PERSONAL_TIN_ID = 'personal-tin-123'

RETRY_INTERVAL_MINUTES = 7
ERROR_AFTER_MINUTES = 30
STOP_AFTER_MINUTES = 60

RUSSIA_VAT = '20'

VIP_TYPE = 'slivki'
OTHER_VIP_TYPE = 'celebrate'

WMS_RESERVE_TIMEOUT_SECONDS = 400
PAYMENT_TIMEOUT_SECONDS = 500

TIPS_WITH_ORDER_FLOW = 'with_order'
TIPS_SEPARATE_FLOW = 'separate'

TIPS_FLOW_MARK = pytest.mark.parametrize(
    'tips_payment_flow', [TIPS_WITH_ORDER_FLOW, TIPS_SEPARATE_FLOW],
)

TICKET_QUEUE = 'test_queue'
TICKET_TAGS = ['test_tag', 'another_test_tag']

AUTH_CONTEXT = {
    'headers': {
        'X-Request-Language': 'ru',
        'X-Request-Application': headers.APP_INFO,
        'X-YaTaxi-User': headers.USER_INFO,
        'X-Yandex-UID': headers.YANDEX_UID,
        'X-Remote-IP': headers.USER_IP,
        'X-Login-Id': headers.LOGIN_ID,
        'X-YaTaxi-Session': headers.DEFAULT_SESSION,
        'X-YaTaxi-PhoneId': headers.PHONE_ID,
        'X-AppMetrica-DeviceId': headers.APPMETRICA_DEVICE_ID,
    },
}
