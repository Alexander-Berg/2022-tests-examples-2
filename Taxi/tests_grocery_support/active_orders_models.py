import dataclasses
import datetime
import decimal
import uuid


SHORT_ORDER_ID = '222222-1212321'

UTC_TZ = datetime.timezone.utc

CREATED_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=UTC_TZ)
PICKUPED_DT = datetime.datetime(2020, 3, 13, 7, 25, 00, tzinfo=UTC_TZ)

ORDER_STATE = 'created'

INSERT_ACTIVE_ORDER = """
INSERT INTO grocery_support.active_orders
(
order_id,
order_state,
short_order_id,
order_created_date,
order_promise,
order_pickuped_date,
delivery_eta,
cart_total_price,
city_name,
depot_id,
yandex_uid,
personal_phone_id,
proactive_support_type,
country_iso3,
ticket_id,
ticket_key,
order_finished_date,
cancel_reason_type,
cancel_reason_message,
vip_type
)
VALUES (%s,
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
;
"""

SELECT_ACTIVE_ORDER = """
SELECT
    order_state,
    short_order_id,
    order_created_date,
    order_promise,
    order_pickuped_date,
    delivery_eta,
    cart_total_price,
    city_name,
    depot_id,
    yandex_uid,
    personal_phone_id,
    proactive_support_type,
    country_iso3,
    ticket_id,
    ticket_key,
    order_finished_date,
    cancel_reason_type,
    cancel_reason_message,
    vip_type
FROM grocery_support.active_orders
WHERE order_id = %s
"""

GET_NUMBER_OF_CREATED_TICKETS = """
SELECT count
FROM grocery_support.proactive_supported_orders_counter
WHERE proactive_support_type = %s AND country_iso3 = %s;
"""

SET_NUMBER_OF_CREATED_TICKETS = """
UPDATE grocery_support.proactive_supported_orders_counter
SET count = %s
WHERE proactive_support_type = %s AND country_iso3 = %s;
"""

CREATE_COUNTERS = """
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('late_order', 0, 'RUS');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('expensive_order', 0, 'RUS');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('vip_order', 0, 'RUS');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('canceled_order', 0, 'RUS');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('first_order', 0, 'RUS');

INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('late_order', 0, 'ISR');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('expensive_order', 0, 'ISR');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('vip_order', 0, 'ISR');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('canceled_order', 0, 'ISR');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('first_order', 0, 'ISR');

INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('late_order', 0, 'GBR');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('expensive_order', 0, 'GBR');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('vip_order', 0, 'GBR');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('canceled_order', 0, 'GBR');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('first_order', 0, 'GBR');

INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('late_order', 0, 'FRA');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('expensive_order', 0, 'FRA');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('vip_order', 0, 'FRA');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('canceled_order', 0, 'FRA');
INSERT INTO grocery_support.proactive_supported_orders_counter
(proactive_support_type, count, country_iso3)
VALUES ('first_order', 0, 'FRA');
"""


# actually, don't know why V003_insert_default_counters.sql doesn't fill
# grocery_support.proactive_supported_orders_counter table
# so, this function fills it
def prepare_counter_table(pgsql):
    cursor = pgsql['grocery_support'].cursor()

    cursor.execute(CREATE_COUNTERS)


def set_number_of_created_tickets(
        pgsql, proactive_support_type, count, country_iso3,
):
    cursor = pgsql['grocery_support'].cursor()

    cursor.execute(
        SET_NUMBER_OF_CREATED_TICKETS,
        [count, proactive_support_type, country_iso3],
    )


def get_number_of_created_tickets(
        pgsql, proactive_support_type, country_iso3='RUS',
):
    cursor = pgsql['grocery_support'].cursor()

    cursor.execute(
        GET_NUMBER_OF_CREATED_TICKETS, [proactive_support_type, country_iso3],
    )
    result = cursor.fetchone()
    assert result
    (count,) = result
    return count


@dataclasses.dataclass
class ActiveOrder:
    def __init__(
            self,
            pgsql,
            order_id=str(uuid.uuid4()),
            order_state=ORDER_STATE,
            short_order_id=SHORT_ORDER_ID,
            order_created_date=CREATED_DT,
            order_promise=15,
            order_pickuped_date=PICKUPED_DT,
            delivery_eta=10,
            cart_total_price='333',
            currency='RUB',
            city_name='Moscow',
            depot_id='test_depot_id',
            yandex_uid='super_user',
            personal_phone_id='personal',
            update_db=True,
            proactive_support_type=None,
            country_iso3=None,
            ticket_id=None,
            ticket_key=None,
            order_finished_date=None,
            cancel_reason_type=None,
            cancel_reason_message=None,
            vip_type=None,
    ):
        self.pg_db = pgsql['grocery_support']
        self.order_id = order_id
        self.order_state = order_state
        self.short_order_id = short_order_id
        self.order_created_date = order_created_date
        self.order_promise = order_promise
        self.order_pickuped_date = order_pickuped_date
        self.delivery_eta = delivery_eta
        self.cart_total_price = cart_total_price
        self.city_name = city_name
        self.depot_id = depot_id
        self.yandex_uid = yandex_uid
        self.personal_phone_id = personal_phone_id
        self.proactive_support_type = proactive_support_type
        self.country_iso3 = country_iso3
        self.ticket_id = ticket_id
        self.ticket_key = ticket_key
        self.order_finished_date = order_finished_date
        self.cancel_reason_type = cancel_reason_type
        self.cancel_reason_message = cancel_reason_message
        self.vip_type = vip_type
        if update_db:
            self.update_db()

    def update_db(self):
        cursor = self.pg_db.cursor()

        cursor.execute(
            INSERT_ACTIVE_ORDER,
            [
                self.order_id,
                self.order_state,
                self.short_order_id,
                self.order_created_date,
                self.order_promise,
                self.order_pickuped_date,
                self.delivery_eta,
                self.cart_total_price,
                self.city_name,
                self.depot_id,
                self.yandex_uid,
                self.personal_phone_id,
                self.proactive_support_type,
                self.country_iso3,
                self.ticket_id,
                self.ticket_key,
                self.order_finished_date,
                self.cancel_reason_type,
                self.cancel_reason_message,
                self.vip_type,
            ],
        )

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_ACTIVE_ORDER, [self.order_id])
        result = cursor.fetchone()
        assert result
        (
            order_state,
            short_order_id,
            order_created_date,
            order_promise,
            order_pickuped_date,
            delivery_eta,
            cart_total_price,
            city_name,
            depot_id,
            yandex_uid,
            personal_phone_id,
            proactive_support_type,
            country_iso3,
            ticket_id,
            ticket_key,
            order_finished_date,
            cancel_reason_type,
            cancel_reason_message,
            vip_type,
        ) = result

        self.order_state = order_state
        self.short_order_id = short_order_id
        self.order_created_date = order_created_date
        self.order_promise = order_promise
        self.order_pickuped_date = order_pickuped_date
        self.delivery_eta = delivery_eta
        self.cart_total_price = cart_total_price
        self.city_name = city_name
        self.depot_id = depot_id
        self.yandex_uid = yandex_uid
        self.personal_phone_id = personal_phone_id
        self.proactive_support_type = proactive_support_type
        self.country_iso3 = country_iso3
        self.ticket_id = ticket_id
        self.ticket_key = ticket_key
        self.order_finished_date = order_finished_date
        self.cancel_reason_type = cancel_reason_type
        self.cancel_reason_message = cancel_reason_message
        self.vip_type = vip_type

    def compare_with_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_ACTIVE_ORDER, [self.order_id])
        result = cursor.fetchone()
        assert result
        (
            order_state,
            short_order_id,
            order_created_date,
            order_promise,
            order_pickuped_date,
            delivery_eta,
            cart_total_price,
            city_name,
            depot_id,
            yandex_uid,
            personal_phone_id,
            proactive_support_type,
            country_iso3,
            ticket_id,
            ticket_key,
            order_finished_date,
            cancel_reason_type,
            cancel_reason_message,
            vip_type,
        ) = result

        assert self.order_state == order_state
        assert self.short_order_id == short_order_id
        assert self.order_created_date == order_created_date
        assert self.order_promise == order_promise
        if order_pickuped_date is not None:
            assert self.order_pickuped_date == order_pickuped_date
        if delivery_eta is not None:
            assert self.delivery_eta == delivery_eta
        assert decimal.Decimal(self.cart_total_price) == cart_total_price
        assert self.city_name == city_name
        assert self.depot_id == depot_id
        assert self.yandex_uid == yandex_uid
        assert self.personal_phone_id == personal_phone_id
        assert self.proactive_support_type == proactive_support_type
        assert self.country_iso3 == country_iso3
        assert self.ticket_id == ticket_id
        assert self.ticket_key == ticket_key
        assert self.order_finished_date == order_finished_date
        assert self.cancel_reason_type == cancel_reason_type
        assert self.cancel_reason_message == cancel_reason_message
        assert self.vip_type == vip_type

    def assert_db_is_empty(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_ACTIVE_ORDER, [self.order_id])
        result = cursor.fetchone()
        assert result is None


def get_tracker_request(
        order,
        ticket_queue,
        ticket_summary,
        ticket_tags=None,
        send_chatterbox=False,
):
    request = {
        'unique': order.order_id,
        'queue': ticket_queue,
        'summary': ticket_summary,
        'tags': ticket_tags,
    }
    if send_chatterbox:
        request['sendChatterbox'] = 'Да'

    return request
