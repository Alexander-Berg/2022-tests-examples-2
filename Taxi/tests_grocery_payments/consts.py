# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error

import datetime
import typing

from grocery_mocks.models import country as country_models
from grocery_payments_shared import transactions as transactions_lib
import psycopg2.tz

UTZ_TZ = psycopg2.tz.FixedOffsetTimezone(offset=0)
NOW = '2020-03-13T07:19:00+00:00'
NOW_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=UTZ_TZ)

ORDER_ID = 'order-id-123'
CARD_ID = 'card-x0c0cab13124063123e35406e'
PAYMENT_ID = 'payment-id-x123'
PERSONAL_WALLET_ID = 'w/28c44321-16a3-5221-a0b1-3f823998bdff'
WALLET_SERVICE = '32'
SERVICE = 'grocery'
PASS_PARAMS: typing.Dict[str, typing.Any] = {}
TRANSACTIONS_ORIGINATOR = 'grocery_payments'
TERMINAL_ID = '95426005'
EXTERNAL_PAYMENT_ID = transactions_lib.EXTERNAL_PAYMENT_ID
REFUND_EXTERNAL_PAYMENT_ID = transactions_lib.REFUND_EXTERNAL_PAYMENT_ID

RUSSIA_CASHBACK_SERVICE = 'lavka'
ISRAEL_CASHBACK_SERVICE = 'yango_deli'
CASHBACK_SERVICE_ID = '662'
RUSSIA_CASHBACK_TICKET = 'NEWSERVICE-1322'
ISRAEL_CASHBACK_TICKET = 'NEWSERVICE-1636'

STAFF_LOGIN = 'yandex staff'

OPERATION_DONE = 'done'
OPERATION_FAILED = 'failed'
OPERATION_OBSOLETE = 'obsolete'
OPERATION_PROCESSING = 'processing'
OPERATION_INIT = 'init'
OPERATION_CREATE = 'create'

OPERATION_ID = '123'

OPERATION_FINISH = 'operation_finish'
TRANSACTION_CLEAR = 'transaction_clear'

X3DS_NOTIFICATION_TYPE = '3ds_user_action_required'
SBP_NOTIFICATION_TYPE = 'sbp_user_action_required'

CLEAR_SUCCESS = 'clear_success'
CLEAR_FAILED = 'clear_fail'

REFUND_SUCCESS = 'refund_success'
REFUND_FAILED = 'refund_fail'

DEFAULT_TRANSACTION = transactions_lib.DEFAULT_TRANSACTION
DEFAULT_OPERATION = transactions_lib.DEFAULT_OPERATION
DEFAULT_REFUND = transactions_lib.DEFAULT_REFUND

COUNTRIES = [
    country_models.Country.Russia,
    country_models.Country.Israel,
    country_models.Country.France,
    country_models.Country.GreatBritain,
]

MERCHANT_ANDROID = 'merchant-android'
MERCHANT_IPHONE = 'merchant-iphone'

ORDER_RECEIPT_DATA_TYPE = 'order'

DEFAULT_WALLET_PAYLOAD = {'wallet_id': PERSONAL_WALLET_ID}

DEBT_PREFIX = 'debt/collect'

REGION_ID = 222

PAYTURE_TERMINAL_ID = '425634875962435'
PAYTURE_NAME = 'payture'

SBERBANK_TERMINAL_ID = '734265732845'
SBERBANK_NAME = 'sberbank'
