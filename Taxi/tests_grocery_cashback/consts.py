# pylint: disable=import-error
from grocery_mocks.models import country as counties

from . import helpers
from . import models

ITEM1_ID = 'some_item_id_1'
ITEM1_QUANTITY = '2'
ITEM1_AMOUNT = '50'

ITEM2_ID = 'some_item_id_2'
ITEM2_QUANTITY = '4'
ITEM2_AMOUNT = '70'

ITEM3_ID = 'some_item_id_3'
ITEM3_QUANTITY = '8'
ITEM3_AMOUNT = '88'

ONE_PRODUCT = [models.Product(ITEM1_ID, ITEM1_QUANTITY, ITEM1_AMOUNT)]

PRODUCTS = [
    models.Product(ITEM1_ID, ITEM1_QUANTITY, ITEM1_AMOUNT),
    models.Product(ITEM2_ID, ITEM2_QUANTITY, ITEM2_AMOUNT),
]

PAYLOAD = helpers.create_payload(PRODUCTS)

CASHBACK_AMOUNT = helpers.get_order_amount(PRODUCTS)

EXTRA_PRODUCT = [models.Product(ITEM3_ID, ITEM3_QUANTITY, ITEM3_AMOUNT)]

SERVICE = 'grocery-cashback-compensation'
TRACKING_GAME_SERVICE = 'grocery-tracking-game'
COMPENSATION_ID = 'compensation_123'
TRACKING_GAME_COMPENSATION_ID = 'tracking_game_reward'
ORDER_ID = 'order_456'
SHORT_ORDER_ID = 'short_order_456'
INVOICE_ID = helpers.make_invoice_id(COMPENSATION_ID)
BASIC_FLOW_VERSION = 'grocery_flow_v3'
TRISTERO_FLOW_VERSION = 'tristero_flow_v1'


COUNTRY = counties.Country.Russia

COUNTRY_ISO3 = COUNTRY.country_iso3
CURRENCY = COUNTRY.currency

CASHBACK_SERVICE_ID = '662'

TICKET = 'NEWSERVICE-1322'
