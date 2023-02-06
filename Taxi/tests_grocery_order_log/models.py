import dataclasses
import datetime
import decimal
import json
import random
import uuid


UTC_TZ = datetime.timezone.utc
NOW = '2020-03-13T07:19:00+00:00'
NOW_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=UTC_TZ)

NOT_NOW = '2020-03-13T06:19:00+00:00'
NOT_NOW_DT = datetime.datetime(2020, 3, 13, 6, 19, 00, tzinfo=UTC_TZ)

DELIVERY_TIN = '123456789'
DELIVERY_TIN_ID = 'personal_tin_id'

SELECT_ORDER_LOG_SQL = """
SELECT
   order_id,
   short_order_id,
   order_created_date,
   order_finished_date,
   updated,
   order_state,
   order_source,

   cart_id,
   cart_total_price,
   cashback_gain,
   cashback_charge,
   cart_total_discount,
   delivery_cost,
   refund,
   currency,
   cart_items,

   depot_id,
   legal_entities,
   destination,
   courier,

   receipts,

   yandex_uid,
   eats_user_id,
   appmetrica_device_id,
   geo_id,
   country_iso3,

   can_be_archived,
   anonym_id
FROM order_log.order_log
WHERE order_id = %s
"""

SELECT_ORDER_LOG_INDEX_SQL = """
SELECT
    order_id,
    short_order_id,
    order_created_date,
    personal_phone_id,
    personal_email_id,
    yandex_uid,
    eats_user_id,
    cart_id,
    order_state,
    order_type
FROM order_log.index
WHERE order_id = %s
"""

INSERT_ORDER_LOG_SQL = """
INSERT INTO order_log.order_log (
     order_id,
     short_order_id,
     order_created_date,
     order_finished_date,
     order_state,
     order_source,
     cart_id,
     cart_total_price,
     cashback_gain,
     cashback_charge,
     cart_total_discount,
     delivery_cost,
     refund,
     currency,
     cart_items,
     depot_id,
     legal_entities,
     destination,
     courier,
     receipts,
     yandex_uid,
     eats_user_id,
     appmetrica_device_id,
     geo_id,
     country_iso3,
     can_be_archived,
     anonym_id
)
VALUES (
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s,
     %s)
ON CONFLICT(order_id)
DO UPDATE SET
order_id = EXCLUDED.order_id,
short_order_id = EXCLUDED.short_order_id,
order_created_date = EXCLUDED.order_created_date,
order_finished_date = EXCLUDED.order_finished_date,
order_state = EXCLUDED.order_state,
order_source = EXCLUDED.order_source,
cart_id = EXCLUDED.cart_id,
cart_total_price = EXCLUDED.cart_total_price,
cashback_gain = EXCLUDED.cashback_gain,
cashback_charge = EXCLUDED.cashback_charge,
cart_total_discount = EXCLUDED.cart_total_discount,
delivery_cost = EXCLUDED.delivery_cost,
refund = EXCLUDED.refund,
currency = EXCLUDED.currency,
cart_items = EXCLUDED.cart_items,
depot_id = EXCLUDED.depot_id,
legal_entities = EXCLUDED.legal_entities,
destination = EXCLUDED.destination,
courier = EXCLUDED.courier,
receipts = EXCLUDED.receipts,
yandex_uid = EXCLUDED.yandex_uid,
eats_user_id = EXCLUDED.eats_user_id,
appmetrica_device_id = EXCLUDED.appmetrica_device_id,
geo_id = EXCLUDED.geo_id,
country_iso3 = EXCLUDED.country_iso3,
can_be_archived = EXCLUDED.can_be_archived,
anonym_id = EXCLUDED.anonym_id
"""

INSERT_ORDER_LOG_INDEX_SQL = """
INSERT INTO order_log.index (
    order_id,
    short_order_id,
    order_created_date,
    personal_phone_id,
    personal_email_id,
    yandex_uid,
    eats_user_id,
    cart_id,
    order_state,
    order_type
)
VALUES (
     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT(order_id)
DO UPDATE SET
    order_id = EXCLUDED.order_id,
    short_order_id = EXCLUDED.short_order_id,
    order_created_date = EXCLUDED.order_created_date,
    personal_phone_id = EXCLUDED.personal_phone_id,
    personal_email_id = EXCLUDED.personal_email_id,
    yandex_uid = EXCLUDED.yandex_uid,
    eats_user_id = EXCLUDED.eats_user_id,
    cart_id = EXCLUDED.cart_id,
    order_state = EXCLUDED.order_state,
    order_type = EXCLUDED.order_type
"""


def check_cart_items(pg_cart_items, request_cart_items):
    for pg_item, request_item in zip(pg_cart_items, request_cart_items):
        assert pg_item['id'] == request_item['id']
        assert pg_item['item_name'] == request_item['item_name']
        assert decimal.Decimal(pg_item['price']) == decimal.Decimal(
            request_item['price'],
        )
        assert decimal.Decimal(pg_item['quantity']) == decimal.Decimal(
            request_item['quantity'],
        )
        assert cmp_decimal(
            pg_item.get('cashback_gain'), request_item.get('cashback_gain'),
        )
        assert cmp_decimal(
            pg_item.get('cashback_charge'),
            request_item.get('cashback_charge'),
        )
        assert pg_item.get('parcel_vendor') == request_item.get(
            'parcel_vendor',
        )
        assert pg_item.get('parcel_ref_order') == request_item.get(
            'parcel_ref_order',
        )
        assert cmp_decimal(
            pg_item.get('gross_weight'), request_item.get('gross_weight'),
        )


def check_legal_entities(pg_legal_entities, request_legal_entities):
    for pg_item, request_item in zip(
            pg_legal_entities, request_legal_entities,
    ):
        assert pg_item['type'] == request_item['type']
        assert pg_item['title'] == request_item['title']
        assert (
            pg_item['additional_properties']
            == request_item['additional_properties']
        )


@dataclasses.dataclass
class OrderLog:
    def __init__(
            self,
            pgsql,
            order_id=str(uuid.uuid4()),
            *,
            short_order_id=None,
            order_created_date=NOW_DT,
            order_finished_date=NOW_DT + datetime.timedelta(minutes=10),
            order_state='closed',
            order_source=None,
            cart_id=str(uuid.uuid4()),
            depot_id='test_depot_id',
            legal_entities=None,
            cart_total_price=None,
            cashback_gain=None,
            cashback_charge=None,
            cart_total_discount=None,
            delivery_cost=None,
            refund=None,
            currency=None,
            cart_items=None,
            destination=None,
            courier=None,
            receipts=None,
            yandex_uid='super_uid',
            eats_user_id=None,
            appmetrica_device_id=None,
            geo_id=None,
            country_iso3=None,
            updated=NOW_DT + datetime.timedelta(minutes=11),
            can_be_archived=None,
            anonym_id=None,
    ):
        self.pg_db = pgsql['grocery_order_log']

        self.order_id = order_id

        if short_order_id is None:
            self.short_order_id = (
                f'280920-a-{random.randint(1000000, 9999999)}'
            )
        else:
            self.short_order_id = short_order_id
        self.order_created_date = order_created_date
        self.order_finished_date = order_finished_date
        self.updated = updated
        self.order_state = order_state
        self.order_source = order_source

        self.cart_id = cart_id
        self.cart_total_price = cart_total_price
        self.cashback_gain = cashback_gain
        self.cashback_charge = cashback_charge
        self.cart_total_discount = cart_total_discount
        self.delivery_cost = delivery_cost
        self.refund = refund
        self.currency = currency

        if cart_items is not None:
            self.cart_items = cart_items
        else:
            self.cart_items = []

        self.depot_id = depot_id
        if legal_entities is not None:
            self.legal_entities = legal_entities
        else:
            self.legal_entities = {}

        if destination is not None:
            self.destination = destination
        else:
            self.destination = {}

        self.courier = courier

        if receipts is not None:
            self.receipts = receipts
        else:
            self.receipts = []

        self.yandex_uid = yandex_uid
        self.eats_user_id = eats_user_id
        self.appmetrica_device_id = appmetrica_device_id
        self.geo_id = geo_id
        self.country_iso3 = country_iso3

        self.can_be_archived = can_be_archived
        self.anonym_id = anonym_id

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_ORDER_LOG_SQL,
            [
                self.order_id,
                self.short_order_id,
                self.order_created_date,
                self.order_finished_date,
                self.order_state,
                self.order_source,
                self.cart_id,
                self.cart_total_price,
                self.cashback_gain,
                self.cashback_charge,
                self.cart_total_discount,
                self.delivery_cost,
                self.refund,
                self.currency,
                json.dumps(self.cart_items),
                self.depot_id,
                json.dumps(self.legal_entities),
                json.dumps(self.destination),
                self.courier,
                json.dumps(self.receipts),
                self.yandex_uid,
                self.eats_user_id,
                self.appmetrica_device_id,
                self.geo_id,
                self.country_iso3,
                self.can_be_archived,
                self.anonym_id,
            ],
        )

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_ORDER_LOG_SQL, [self.order_id])
        result = cursor.fetchone()
        assert result
        (
            order_id,
            short_order_id,
            order_created_date,
            order_finished_date,
            updated,
            order_state,
            order_source,
            cart_id,
            cart_total_price,
            cashback_gain,
            cashback_charge,
            cart_total_discount,
            delivery_cost,
            refund,
            currency,
            cart_items,
            depot_id,
            legal_entities,
            destination,
            courier,
            receipts,
            yandex_uid,
            eats_user_id,
            appmetrica_device_id,
            geo_id,
            country_iso3,
            can_be_archived,
            anonym_id,
        ) = result

        self.order_id = order_id
        self.short_order_id = short_order_id
        self.order_created_date = order_created_date
        self.order_finished_date = order_finished_date
        self.updated = updated
        self.order_state = order_state
        self.order_source = order_source

        self.cart_id = cart_id
        self.cart_total_price = cart_total_price
        self.cashback_gain = cashback_gain
        self.cashback_charge = cashback_charge
        self.cart_total_discount = cart_total_discount
        self.delivery_cost = delivery_cost
        self.refund = refund
        self.currency = currency
        self.cart_items = cart_items

        self.depot_id = depot_id
        self.legal_entities = legal_entities
        self.destination = destination
        self.courier = courier

        self.receipts = receipts

        self.yandex_uid = yandex_uid
        self.eats_user_id = eats_user_id
        self.appmetrica_device_id = appmetrica_device_id
        self.geo_id = geo_id
        self.country_iso3 = country_iso3

        self.can_be_archived = can_be_archived
        self.anonym_id = anonym_id


@dataclasses.dataclass
class OrderLogIndex:
    def __init__(
            self,
            pgsql,
            order_id=str(uuid.uuid4()),
            short_order_id=None,
            order_created_date=NOW_DT,
            personal_phone_id=None,
            personal_email_id=None,
            yandex_uid=None,
            eats_user_id=None,
            cart_id=None,
            order_state=None,
            order_type=None,
    ):
        self.pg_db = pgsql['grocery_order_log']
        self.order_id = order_id
        self.short_order_id = short_order_id
        self.order_created_date = order_created_date
        self.personal_phone_id = personal_phone_id
        self.personal_email_id = personal_email_id
        self.yandex_uid = yandex_uid
        self.eats_user_id = eats_user_id
        self.cart_id = cart_id
        self.order_state = order_state
        self.order_type = order_type

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_ORDER_LOG_INDEX_SQL, [self.order_id])
        result = cursor.fetchone()
        assert result
        (
            order_id,
            short_order_id,
            order_created_date,
            personal_phone_id,
            personal_email_id,
            yandex_uid,
            eats_user_id,
            cart_id,
            order_state,
            order_type,
        ) = result

        assert self.order_id == order_id
        self.short_order_id = short_order_id
        self.order_created_date = order_created_date
        self.personal_phone_id = personal_phone_id
        self.personal_email_id = personal_email_id
        self.yandex_uid = yandex_uid
        self.eats_user_id = eats_user_id
        self.cart_id = cart_id
        self.order_state = order_state
        self.order_type = order_type

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_ORDER_LOG_INDEX_SQL,
            [
                self.order_id,
                self.short_order_id,
                self.order_created_date,
                self.personal_phone_id,
                self.personal_email_id,
                self.yandex_uid,
                self.eats_user_id,
                self.cart_id,
                self.order_state,
                self.order_type,
            ],
        )


def cmp_decimal(lhs, rhs):
    if lhs is None:
        return rhs is None
    return decimal.Decimal(lhs) == decimal.Decimal(rhs)
