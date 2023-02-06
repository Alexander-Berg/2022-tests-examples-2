# pylint: disable=too-many-lines

import ast
import dataclasses
import datetime
import json
import random
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
import uuid

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks.models import cart
# pylint: enable=import-error

from tests_grocery_orders_tracking import headers


DEFAULT_CREATED = datetime.datetime(
    year=2021, month=9, day=27, tzinfo=datetime.timezone.utc,
)

DEFAULT_DEPOT_ID = cart.DEFAULT_DEPOT_ID

DEFAULT_REGION_ID = 102

UPSERT_ADDITIONAL_SQL = """
INSERT INTO orders.orders_additional (
    order_id,
    appmetrica_device_id,
    app_name,
    order_settings,
    timeslot_start,
    timeslot_end,
    timeslot_request_kind,
    is_dispatch_request_started
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT(order_id)
DO UPDATE SET
    order_id = EXCLUDED.order_id,
    appmetrica_device_id = EXCLUDED.appmetrica_device_id,
    app_name = EXCLUDED.app_name,
    order_settings = EXCLUDED.order_settings,
    timeslot_start = EXCLUDED.timeslot_start,
    timeslot_end = EXCLUDED.timeslot_end,
    timeslot_request_kind = EXCLUDED.timeslot_request_kind,
    is_dispatch_request_started = EXCLUDED.is_dispatch_request_started
;
"""

UPSERT_PERFORMER_SQL = """
INSERT INTO orders.orders_dispatch_performer (
    order_id,
    driver_id,
    eats_courier_id,
    courier_full_name,
    first_name,
    organization_name,
    legal_address,
    ogrn,
    work_schedule,
    personal_tin_id,
    tin,
    vat,
    balance_client_id,
    billing_type,
    car_number,
    car_model,
    car_color,
    car_color_hex
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT(order_id)
DO UPDATE SET
    order_id = EXCLUDED.order_id,
    driver_id = EXCLUDED.driver_id,
    eats_courier_id = EXCLUDED.eats_courier_id,
    courier_full_name = EXCLUDED.courier_full_name,
    first_name = EXCLUDED.first_name,
    organization_name = EXCLUDED.organization_name,
    legal_address = EXCLUDED.legal_address,
    ogrn = EXCLUDED.ogrn,
    work_schedule = EXCLUDED.work_schedule,
    personal_tin_id = EXCLUDED.personal_tin_id,
    tin = EXCLUDED.tin,
    vat = EXCLUDED.vat,
    balance_client_id = EXCLUDED.balance_client_id,
    billing_type = EXCLUDED.billing_type,
    car_number = EXCLUDED.car_number,
    car_model = EXCLUDED.car_model,
    car_color = EXCLUDED.car_color,
    car_color_hex = EXCLUDED.car_color_hex
;
"""

UPSERT_SQL = """
INSERT INTO orders.orders (
    order_id,
    eats_order_id,
    order_version,
    status,
    status_updated,
    desired_status,
    idempotency_token,
    cart_id,
    child_cart_id,
    cart_version,
    offer_id,
    taxi_user_id,
    eats_user_id,
    locale,
    user_info,
    phone_id,
    personal_phone_id,
    app_info,
    created,
    updated,
    due,
    location,
    place_id,
    country,
    city,
    street,
    house,
    floor,
    flat,
    doorcode,
    doorcode_extra,
    building_name,
    doorbell_name,
    left_at_door,
    meet_outside,
    no_door_call,
    postal_code,
    user_ip,
    user_agent,
    yandex_uid,
    session,
    bound_sessions,
    wms_reserve_status,
    hold_money_status,
    close_money_status,
    assembling_status,
    tips_status,
    edit_status,
    correcting_type,
    depot_id,
    region_id,
    client_price,
    currency,
    cancel_reason_type,
    cancel_reason_message,
    short_order_id,
    grocery_flow_version,
    entrance,
    comment,
    promocode,
    promocode_valid,
    promocode_sum,
    dispatch_id,
    dispatch_status,
    dispatch_cargo_status,
    dispatch_delivery_eta,
    dispatch_start_delivery_ts,
    dispatch_courier_name,
    dispatch_courier_first_name,
    dispatch_courier_id,
    dispatch_delivered_eta_ts,
    dispatch_pickuped_eta_ts,
    dispatch_track_version,
    dispatch_transport_type,
    dispatch_driver_id,
    dispatch_car_number,
    dispatch_car_model,
    dispatch_car_color,
    dispatch_car_color_hex,
    tips,
    finished,
    finish_started,
    feedback_status,
    evaluation,
    billing_flow,
    order_revision,
    dispatch_cargo_revision,
    billing_settings_version,
    dispatch_flow,
    dispatch_status_meta,
    manual_update_enabled,
    informer_key,
    cancel_reason_meta,
    vip_type,
    wms_logistic_tags,
    push_notification_enabled,
    personal_email_id
)
VALUES (
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT(depot_id, short_order_id)
DO UPDATE SET
    order_id = EXCLUDED.order_id,
    eats_order_id = EXCLUDED.eats_order_id,
    order_version = EXCLUDED.order_version,
    status = EXCLUDED.status,
    status_updated = EXCLUDED.status_updated,
    desired_status = EXCLUDED.desired_status,
    idempotency_token = EXCLUDED.idempotency_token,
    cart_id = EXCLUDED.cart_id,
    child_cart_id = EXCLUDED.child_cart_id,
    cart_version = EXCLUDED.cart_version,
    offer_id = EXCLUDED.offer_id,
    taxi_user_id = EXCLUDED.taxi_user_id,
    eats_user_id = EXCLUDED.eats_user_id,
    locale = EXCLUDED.locale,
    user_info = EXCLUDED.user_info,
    phone_id = EXCLUDED.phone_id,
    personal_phone_id = EXCLUDED.personal_phone_id,
    app_info = EXCLUDED.app_info,
    created = EXCLUDED.created,
    updated = EXCLUDED.updated,
    due = EXCLUDED.due,
    location = EXCLUDED.location,
    place_id = EXCLUDED.place_id,
    country = EXCLUDED.country,
    city = EXCLUDED.city,
    street = EXCLUDED.street,
    house = EXCLUDED.house,
    floor = EXCLUDED.floor,
    flat = EXCLUDED.flat,
    doorcode = EXCLUDED.doorcode,
    doorcode_extra = EXCLUDED.doorcode_extra,
    building_name = EXCLUDED.building_name,
    doorbell_name = EXCLUDED.doorbell_name,
    left_at_door = EXCLUDED.left_at_door,
    meet_outside = EXCLUDED.meet_outside,
    no_door_call = EXCLUDED.no_door_call,
    postal_code = EXCLUDED.postal_code,
    user_ip = EXCLUDED.user_ip,
    user_agent = EXCLUDED.user_agent,
    yandex_uid = EXCLUDED.yandex_uid,
    session = EXCLUDED.session,
    bound_sessions = EXCLUDED.bound_sessions,
    wms_reserve_status = EXCLUDED.wms_reserve_status,
    hold_money_status = EXCLUDED.hold_money_status,
    close_money_status = EXCLUDED.close_money_status,
    assembling_status = EXCLUDED.assembling_status,
    tips_status = EXCLUDED.tips_status,
    edit_status = EXCLUDED.edit_status,
    correcting_type = EXCLUDED.correcting_type,
    depot_id = EXCLUDED.depot_id,
    region_id = EXCLUDED.region_id,
    client_price = EXCLUDED.client_price,
    currency = EXCLUDED.currency,
    cancel_reason_type = EXCLUDED.cancel_reason_type,
    cancel_reason_message = EXCLUDED.cancel_reason_message,
    short_order_id = EXCLUDED.short_order_id,
    grocery_flow_version = EXCLUDED.grocery_flow_version,
    entrance = EXCLUDED.entrance,
    comment = EXCLUDED.comment,
    promocode = EXCLUDED.promocode,
    promocode_valid = EXCLUDED.promocode_valid,
    promocode_sum = EXCLUDED.promocode_sum,
    dispatch_id = EXCLUDED.dispatch_id,
    dispatch_status = EXCLUDED.dispatch_status,
    dispatch_cargo_status = EXCLUDED.dispatch_cargo_status,
    dispatch_delivery_eta = EXCLUDED.dispatch_delivery_eta,
    dispatch_start_delivery_ts = EXCLUDED.dispatch_start_delivery_ts,
    dispatch_courier_name = EXCLUDED.dispatch_courier_name,
    dispatch_courier_first_name = EXCLUDED.dispatch_courier_first_name,
    dispatch_courier_id = EXCLUDED.dispatch_courier_id,
    dispatch_delivered_eta_ts = EXCLUDED.dispatch_delivered_eta_ts,
    dispatch_pickuped_eta_ts = EXCLUDED.dispatch_pickuped_eta_ts,
    dispatch_track_version = EXCLUDED.dispatch_track_version,
    dispatch_transport_type = EXCLUDED.dispatch_transport_type,
    dispatch_driver_id = EXCLUDED.dispatch_driver_id,
    dispatch_car_number = EXCLUDED.dispatch_car_number,
    dispatch_car_model = EXCLUDED.dispatch_car_model,
    dispatch_car_color = EXCLUDED.dispatch_car_color,
    dispatch_car_color_hex = EXCLUDED.dispatch_car_color_hex,
    tips = EXCLUDED.tips,
    finished = EXCLUDED.finished,
    finish_started = EXCLUDED.finish_started,
    feedback_status = EXCLUDED.feedback_status,
    evaluation = EXCLUDED.evaluation,
    billing_flow = EXCLUDED.billing_flow,
    order_revision = EXCLUDED.order_revision,
    dispatch_cargo_revision = EXCLUDED.dispatch_cargo_revision,
    billing_settings_version = EXCLUDED.billing_settings_version,
    dispatch_flow = EXCLUDED.dispatch_flow,
    dispatch_status_meta = EXCLUDED.dispatch_status_meta,
    manual_update_enabled = EXCLUDED.manual_update_enabled,
    informer_key = EXCLUDED.informer_key,
    cancel_reason_meta = EXCLUDED.cancel_reason_meta,
    vip_type = EXCLUDED.vip_type,
    wms_logistic_tags = EXCLUDED.wms_logistic_tags,
    push_notification_enabled = EXCLUDED.push_notification_enabled,
    personal_email_id = EXCLUDED.personal_email_id
;
"""

SELECT_SQL = """
SELECT
    order_id,
    eats_order_id,
    order_version,
    status,
    status_updated,
    desired_status,
    idempotency_token,
    cart_id,
    child_cart_id,
    cart_version,
    offer_id,
    taxi_user_id,
    eats_user_id,
    locale,
    user_info,
    phone_id,
    personal_phone_id,
    app_info,
    created,
    updated,
    due,
    location,
    place_id,
    country,
    city,
    street,
    house,
    floor,
    flat,
    doorcode,
    doorcode_extra,
    building_name,
    doorbell_name,
    left_at_door,
    meet_outside,
    no_door_call,
    postal_code,
    user_ip,
    user_agent,
    yandex_uid,
    session,
    bound_sessions,
    wms_reserve_status,
    hold_money_status,
    close_money_status,
    assembling_status,
    tips_status,
    edit_status,
    correcting_type,
    feedback_status,
    evaluation,
    depot_id,
    region_id,
    client_price,
    currency,
    cancel_reason_type,
    cancel_reason_message,
    short_order_id,
    grocery_flow_version,
    entrance,
    comment,
    promocode,
    promocode_valid,
    promocode_sum,
    dispatch_id,
    dispatch_status,
    dispatch_cargo_status,
    dispatch_delivery_eta,
    dispatch_start_delivery_ts,
    dispatch_courier_name,
    dispatch_courier_first_name,
    dispatch_courier_id,
    dispatch_delivered_eta_ts,
    dispatch_pickuped_eta_ts,
    dispatch_track_version,
    dispatch_transport_type,
    dispatch_driver_id,
    dispatch_car_number,
    dispatch_car_model,
    dispatch_car_color,
    dispatch_car_color_hex,
    tips,
    finished,
    finish_started,
    billing_flow,
    order_revision,
    dispatch_cargo_revision,
    billing_settings_version,
    dispatch_flow,
    dispatch_status_meta,
    manual_update_enabled,
    informer_key,
    cancel_reason_meta,
    vip_type,
    wms_logistic_tags,
    push_notification_enabled,
    personal_email_id
FROM orders.orders WHERE order_id = %s
;
"""

SELECT_CONTACTS_SQL = """
SELECT
    order_id,
    gift_personal_phone_id,
    gift_name
FROM orders.orders_contacts
WHERE order_id = %s;
"""

SELECT_ADDITIONAL_SQL = """
SELECT
    order_id,
    appmetrica_device_id,
    app_name,
    order_settings,
    timeslot_start,
    timeslot_end,
    timeslot_request_kind,
    is_dispatch_request_started
FROM
    orders.orders_additional
WHERE order_id = %s
"""

SELECT_PERFORMER_SQL = """
SELECT
    order_id,
    driver_id,
    eats_courier_id,
    courier_full_name,
    first_name,
    organization_name,
    legal_address,
    ogrn,
    work_schedule,
    COALESCE(personal_tin_id, tin),
    vat,
    balance_client_id,
    billing_type,
    car_number,
    car_model,
    car_color,
    car_color_hex
FROM orders.orders_dispatch_performer
WHERE order_id = %s
"""

SELECT_PAYMENTS_SQL = """
SELECT
    order_id,
    operation_id,
    operation_type,
    status,
    items,
    errors,
    compensation_id
FROM orders.orders_payments
WHERE order_id = %s
"""

UPSERT_CONTACTS_SQL = """
INSERT INTO orders.orders_contacts (
    order_id,
    gift_personal_phone_id,
    gift_name
)
VALUES (%s,%s,%s)
ON CONFLICT (order_id)
DO UPDATE SET
    order_id = EXCLUDED.order_id,
    gift_personal_phone_id = EXCLUDED.gift_personal_phone_id,
    gift_name = EXCLUDED.gift_name
;
"""

UPSERT_PAYMENTS_SQL = """
INSERT INTO orders.orders_payments (
    order_id,
    operation_id,
    operation_type,
    status,
    items,
    errors,
    compensation_id
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT(order_id, operation_id, operation_type)
DO UPDATE SET
    order_id = EXCLUDED.order_id,
    operation_id = EXCLUDED.operation_id,
    operation_type = EXCLUDED.operation_type,
    status = EXCLUDED.status,
    items = EXCLUDED.items,
    errors = EXCLUDED.errors,
    compensation_id = EXCLUDED.compensation_id
;
"""

REMOVE_SQL = """
DELETE FROM orders.orders WHERE
order_id = %s
;
"""

FETCH_HISTORY_SQL = """
SELECT event_type, event_data
FROM orders.orders_history
WHERE order_id = %s
;
"""

INSERT_INFORMER_SQL = """
INSERT INTO orders_tracking.informers
(
    order_id,
    informer_type,
    created,
    compensation_type,
    situation_code,
    cancel_reason,
    raw_compensation_info
)
VALUES
(
    %s, %s, %s, %s, %s, %s, %s
)
"""

SELECT_INFORMER_SQL = """
SELECT
    order_id,
    informer_type,
    created,
    compensation_type,
    situation_code,
    cancel_reason,
    raw_compensation_info
FROM orders_tracking.informers
WHERE order_id = %s
"""

SELECT_INFORMER_TYPE_SQL = """
SELECT informer_type
FROM orders_tracking.informers
WHERE order_id = %s
"""


def _asdict(value):
    if value is None:
        return None
    return json.dumps(value)


@dataclasses.dataclass
class PaymentOperation:
    order_id: str
    operation_id: str
    operation_type: str
    status: str
    items: Optional[List[Dict]] = None
    errors: Optional[List[Dict]] = None
    compensation_id: Optional[str] = None


@dataclasses.dataclass
class GiftInfo:
    name: Optional[str] = None
    phone_id: Optional[str] = None


@dataclasses.dataclass
class OrderState:
    wms_reserve_status: Optional[str] = None
    hold_money_status: Optional[str] = None
    close_money_status: Optional[str] = None
    assembling_status: Optional[str] = None
    tips_status: Optional[str] = None


@dataclasses.dataclass
class DispatchStatusInfo:
    dispatch_id: Optional[str] = None
    dispatch_status: Optional[str] = None
    dispatch_cargo_status: Optional[str] = None
    dispatch_delivery_eta: Optional[int] = None
    dispatch_start_delivery_ts: Optional[str] = None
    dispatch_courier_name: Optional[str] = None
    dispatch_courier_first_name: Optional[str] = None
    dispatch_courier_id: Optional[str] = None
    dispatch_delivered_eta_ts: Optional[str] = None
    dispatch_pickuped_eta_ts: Optional[str] = None
    dispatch_track_version: Optional[int] = None
    dispatch_transport_type: Optional[str] = None
    dispatch_driver_id: Optional[str] = None
    dispatch_cargo_revision: Optional[int] = None
    dispatch_status_meta: Optional[Dict] = None
    failure_reason_type: Optional[str] = None
    dispatch_car_number: Optional[str] = None
    dispatch_car_model: Optional[str] = None
    dispatch_car_color: Optional[str] = None
    dispatch_car_color_hex: Optional[str] = None


@dataclasses.dataclass
class DispatchPerformer:
    driver_id: Optional[str] = None
    eats_courier_id: Optional[str] = None
    courier_full_name: Optional[str] = None
    first_name: Optional[str] = None
    organization_name: Optional[str] = None
    legal_address: Optional[str] = None
    ogrn: Optional[str] = None
    work_schedule: Optional[str] = None
    personal_tin_id: Optional[str] = None
    vat: Optional[str] = None
    balance_client_id: Optional[str] = None
    billing_type: Optional[str] = None
    car_number: Optional[str] = None
    car_model: Optional[str] = None
    car_color: Optional[str] = None
    car_color_hex: Optional[str] = None


class Order:
    def __init__(
            self,
            pgsql,
            order_id=None,
            eats_order_id=None,
            order_version=0,
            status='draft',
            status_updated=DEFAULT_CREATED,
            desired_status=None,
            idempotency_token=None,
            cart_id=None,
            child_cart_id=None,
            cart_version=1,
            offer_id='offer-id',
            taxi_user_id=headers.USER_ID,
            eats_user_id=headers.EATS_USER_ID,
            locale='RU',
            user_info=headers.USER_INFO,
            phone_id=headers.PHONE_ID,
            personal_phone_id=headers.PERSONAL_PHONE_ID,
            app_info=headers.APP_INFO,
            appmetrica_device_id=headers.APPMETRICA_DEVICE_ID,
            app_name=headers.APP_NAME,
            created=DEFAULT_CREATED,
            updated=datetime.datetime.now().isoformat() + '+03:00',
            due=DEFAULT_CREATED + datetime.timedelta(hours=1),
            location='(10.0, 20.0)',
            place_id='place-id',
            country='order_country',
            city='order_city',
            street='order_street',
            house='order_building',
            floor='order_floor',
            flat='order_flat',
            doorcode='order_doorcode',
            doorcode_extra='doorcode_extra',
            building_name='building_name',
            doorbell_name='doorbell_name',
            left_at_door=False,
            meet_outside=False,
            no_door_call=False,
            postal_code=None,
            user_ip=headers.USER_IP,
            user_agent='testsuite',
            yandex_uid=headers.YANDEX_UID,
            session=headers.DEFAULT_SESSION,
            bound_sessions=None,
            state=OrderState(None, None, None, None, None),
            edit_status=None,
            correcting_type=None,
            depot_id=DEFAULT_DEPOT_ID,
            region_id=DEFAULT_REGION_ID,
            client_price=0,
            currency='RUB',
            short_order_id=None,
            insert_in_pg=True,
            cancel_reason_type=None,
            cancel_reason_message=None,
            grocery_flow_version='grocery_flow_v1',
            entrance=None,
            comment=None,
            promocode=None,
            promocode_valid=None,
            promocode_sum=None,
            dispatch_status_info=DispatchStatusInfo(),
            dispatch_performer=DispatchPerformer(),
            tips=None,
            gift_info=None,
            finished=None,
            finish_started=None,
            billing_flow='grocery_payments',
            payment_operations=None,
            order_revision=1,
            billing_settings_version=None,
            dispatch_flow='cargo_claims',
            manual_update_enabled=None,
            cancel_reason_description=None,
            informer_key=None,
            cancel_reason_meta=None,
            vip_type=None,
            wms_logistic_tags=None,
            push_notification_enabled=None,
            personal_email_id=None,
            order_settings=None,
            timeslot_start=None,
            timeslot_end=None,
            timeslot_request_kind=None,
            is_dispatch_request_started=None,
    ):
        self.pg_db = pgsql['grocery_orders']

        if order_id is None:
            order_id = str(uuid.uuid4())
        if eats_user_id is None:
            eats_order_id = str(uuid.uuid4())
        if cart_id is None:
            cart_id = str(uuid.uuid4())
        if idempotency_token is None:
            idempotency_token = str(uuid.uuid4())
        if short_order_id is None:
            short_order_id = f'280920-a-{random.randint(1000000, 9999999)}'
        if payment_operations is None:
            payment_operations = []

        self.order_id = order_id
        self.eats_order_id = (eats_order_id,)
        self.order_version = order_version
        self.status = status
        self.status_updated = status_updated
        self.desired_status = desired_status
        self.idempotency_token = idempotency_token
        self.cart_id = cart_id
        self.child_cart_id = child_cart_id
        self.cart_version = cart_version
        self.offer_id = offer_id
        self.taxi_user_id = taxi_user_id
        self.eats_user_id = eats_user_id
        self.locale = locale
        self.user_info = user_info
        self.phone_id = phone_id
        self.personal_phone_id = personal_phone_id
        self.app_info = app_info
        self.appmetrica_device_id = appmetrica_device_id
        self.app_name = app_name
        self.created = created
        self.updated = updated
        self.due = due
        self.location = location
        self.place_id = place_id
        self.country = country
        self.city = city
        self.street = street
        self.house = house
        self.floor = floor
        self.flat = flat
        self.doorcode = doorcode
        self.doorcode_extra = doorcode_extra
        self.building_name = building_name
        self.doorbell_name = doorbell_name
        self.left_at_door = left_at_door
        self.meet_outside = meet_outside
        self.no_door_call = no_door_call
        self.postal_code = postal_code
        self.user_ip = user_ip
        self.user_agent = user_agent
        self.yandex_uid = yandex_uid
        self.state = state
        self.edit_status = edit_status
        self.correcting_type = correcting_type
        self.depot_id = depot_id
        self.region_id = region_id
        self.client_price = client_price
        self.currency = currency
        self.cancel_reason_type = cancel_reason_type
        self.cancel_reason_message = cancel_reason_message
        self.short_order_id = short_order_id
        self.grocery_flow_version = grocery_flow_version
        self.entrance = entrance
        self.comment = comment
        self.promocode = promocode
        self.promocode_valid = promocode_valid
        self.promocode_sum = promocode_sum
        self.dispatch_status_info = dispatch_status_info
        self.dispatch_performer = dispatch_performer
        self.tips = tips
        self.gift_info = gift_info
        self.finished = finished
        self.finish_started = finish_started
        self.feedback_status = None
        self.evaluation = None
        self.session = (session,)
        if bound_sessions is None:
            bound_sessions = ['taxi:456', 'eats:' + headers.EATS_USER_ID]
        self.bound_sessions = ', '.join(bound_sessions)
        self.billing_flow = billing_flow
        self.payment_operations = payment_operations
        self.order_revision = order_revision
        self.billing_settings_version = billing_settings_version
        self.dispatch_flow = dispatch_flow
        self.manual_update_enabled = manual_update_enabled
        self.cancel_reason_description = cancel_reason_description
        self.informer_key = informer_key
        self.cancel_reason_meta = cancel_reason_meta
        self.vip_type = vip_type
        self.wms_logistic_tags = wms_logistic_tags
        self.push_notification_enabled = push_notification_enabled
        self.personal_email_id = personal_email_id
        self.order_settings = order_settings
        self.timeslot_start = timeslot_start
        self.timeslot_end = timeslot_end
        self.timeslot_request_kind = timeslot_request_kind
        self.is_dispatch_request_started = is_dispatch_request_started

        if insert_in_pg:
            self._update_db()

    def _update_db(self):
        cursor = self.pg_db.cursor()

        if self.gift_info:
            cursor.execute(
                UPSERT_CONTACTS_SQL,
                [self.order_id, self.gift_info.phone_id, self.gift_info.name],
            )

        cursor.execute(
            UPSERT_ADDITIONAL_SQL,
            [
                self.order_id,
                self.appmetrica_device_id,
                self.app_name,
                _asdict(self.order_settings),
                self.timeslot_start,
                self.timeslot_end,
                self.timeslot_request_kind,
                self.is_dispatch_request_started,
            ],
        )

        for operation in self.payment_operations:
            cursor.execute(
                UPSERT_PAYMENTS_SQL,
                [
                    self.order_id,
                    operation.operation_id,
                    operation.operation_type,
                    operation.status,
                    json.dumps(operation.items),
                    operation.errors,
                    operation.compensation_id,
                ],
            )

        cursor.execute(
            UPSERT_PERFORMER_SQL,
            [
                self.order_id,
                self.dispatch_performer.driver_id,
                self.dispatch_performer.eats_courier_id,
                self.dispatch_performer.courier_full_name,
                self.dispatch_performer.first_name,
                self.dispatch_performer.organization_name,
                self.dispatch_performer.legal_address,
                self.dispatch_performer.ogrn,
                self.dispatch_performer.work_schedule,
                self.dispatch_performer.personal_tin_id,
                self.dispatch_performer.personal_tin_id,
                self.dispatch_performer.vat,
                self.dispatch_performer.balance_client_id,
                self.dispatch_performer.billing_type,
                self.dispatch_performer.car_number,
                self.dispatch_performer.car_model,
                self.dispatch_performer.car_color,
                self.dispatch_performer.car_color_hex,
            ],
        )

        cursor.execute(
            UPSERT_SQL,
            [
                self.order_id,
                self.eats_order_id,
                self.order_version,
                self.status,
                self.status_updated,
                self.desired_status,
                self.idempotency_token,
                self.cart_id,
                self.child_cart_id,
                self.cart_version,
                self.offer_id,
                self.taxi_user_id,
                self.eats_user_id,
                self.locale,
                self.user_info,
                self.phone_id,
                self.personal_phone_id,
                self.app_info,
                self.created,
                self.updated,
                self.due,
                self.location,
                self.place_id,
                self.country,
                self.city,
                self.street,
                self.house,
                self.floor,
                self.flat,
                self.doorcode,
                self.doorcode_extra,
                self.building_name,
                self.doorbell_name,
                self.left_at_door,
                self.meet_outside,
                self.no_door_call,
                self.postal_code,
                self.user_ip,
                self.user_agent,
                self.yandex_uid,
                self.session,
                '{{{}}}'.format(self.bound_sessions),
                self.state.wms_reserve_status,
                self.state.hold_money_status,
                self.state.close_money_status,
                self.state.assembling_status,
                self.state.tips_status,
                self.edit_status,
                self.correcting_type,
                self.depot_id,
                self.region_id,
                self.client_price,
                self.currency,
                self.cancel_reason_type,
                self.cancel_reason_message,
                self.short_order_id,
                self.grocery_flow_version,
                self.entrance,
                self.comment,
                self.promocode,
                self.promocode_valid,
                self.promocode_sum,
                self.dispatch_status_info.dispatch_id,
                self.dispatch_status_info.dispatch_status,
                self.dispatch_status_info.dispatch_cargo_status,
                self.dispatch_status_info.dispatch_delivery_eta,
                self.dispatch_status_info.dispatch_start_delivery_ts,
                self.dispatch_status_info.dispatch_courier_name,
                self.dispatch_status_info.dispatch_courier_first_name,
                self.dispatch_status_info.dispatch_courier_id,
                self.dispatch_status_info.dispatch_delivered_eta_ts,
                self.dispatch_status_info.dispatch_pickuped_eta_ts,
                self.dispatch_status_info.dispatch_track_version,
                self.dispatch_status_info.dispatch_transport_type,
                self.dispatch_status_info.dispatch_driver_id,
                self.dispatch_status_info.dispatch_car_number,
                self.dispatch_status_info.dispatch_car_model,
                self.dispatch_status_info.dispatch_car_color,
                self.dispatch_status_info.dispatch_car_color_hex,
                self.tips,
                self.finished,
                self.finish_started,
                self.feedback_status,
                self.evaluation,
                self.billing_flow,
                self.order_revision,
                self.dispatch_status_info.dispatch_cargo_revision,
                self.billing_settings_version,
                self.dispatch_flow,
                _asdict(self.dispatch_status_info.dispatch_status_meta),
                self.manual_update_enabled,
                self.informer_key,
                _asdict(self.cancel_reason_meta),
                self.vip_type,
                self.wms_logistic_tags,
                self.push_notification_enabled,
                self.personal_email_id,
            ],
        )

    def upsert(
            self,
            *,
            order_id=None,
            eats_order_id=None,
            order_version=None,
            status=None,
            cart_id=None,
            idempotency_token=None,
            taxi_user_id=None,
            eats_user_id=None,
            phone_id=None,
            personal_phone_id=None,
            personal_email_id=None,
            state=None,
            session=None,
            bound_sessions=None,
            depot_id=None,
            region_id=None,
            short_order_id=None,
            dispatch_status_info=None,
            yandex_uid=None,
            cancel_reason_type=None,
            created=None,
            feedback_status=None,
            evaluation=None,
            desired_status=None,
            tips=None,
            dispatch_performer=None,
            app_info=None,
    ):
        if order_id is not None:
            self.order_id = order_id
        if eats_order_id is not None:
            self.eats_order_id = eats_order_id
        if order_version is not None:
            self.order_version = order_version
        if status is not None:
            self.status = status
        if cart_id is not None:
            self.cart_id = cart_id
        if idempotency_token is not None:
            self.idempotency_token = idempotency_token
        if taxi_user_id is not None:
            self.taxi_user_id = taxi_user_id
        if eats_user_id is not None:
            self.eats_user_id = eats_user_id
        if phone_id is not None:
            self.phone_id = phone_id
        if personal_phone_id is not None:
            self.personal_phone_id = personal_phone_id
        if personal_email_id is not None:
            self.personal_email_id = personal_email_id
        if state is not None:
            self.state = state
        if session is not None:
            self.session = session
        if bound_sessions is not None:
            self.bound_sessions = bound_sessions
        if depot_id is not None:
            self.depot_id = depot_id
        if region_id is not None:
            self.region_id = region_id
        if short_order_id is not None:
            self.short_order_id = short_order_id
        if dispatch_status_info is not None:
            self.dispatch_status_info = dispatch_status_info
        if yandex_uid is not None:
            self.yandex_uid = yandex_uid
        if cancel_reason_type is not None:
            self.cancel_reason_type = cancel_reason_type
        if created is not None:
            self.created = created
        if feedback_status is not None:
            self.feedback_status = feedback_status
        if evaluation is not None:
            self.evaluation = evaluation
        if desired_status is not None:
            self.desired_status = desired_status
        if tips is not None:
            self.tips = tips
        if dispatch_performer is not None:
            self.dispatch_performer = dispatch_performer
        if app_info is not None:
            self.app_info = app_info
        self._update_db()

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_SQL, [self.order_id])
        result = cursor.fetchone()
        assert result
        (
            order_id,
            eats_order_id,
            order_version,
            status,
            status_updated,
            desired_status,
            idempotency_token,
            cart_id,
            child_cart_id,
            cart_version,
            offer_id,
            taxi_user_id,
            eats_user_id,
            locale,
            user_info,
            phone_id,
            personal_phone_id,
            app_info,
            created,
            updated,
            due,
            location,
            place_id,
            country,
            city,
            street,
            house,
            floor,
            flat,
            doorcode,
            doorcode_extra,
            building_name,
            doorbell_name,
            left_at_door,
            meet_outside,
            no_door_call,
            postal_code,
            user_ip,
            user_agent,
            yandex_uid,
            session,
            bound_sessions,
            wms_reserve_status,
            hold_money_status,
            close_money_status,
            assembling_status,
            tips_status,
            edit_status,
            correcting_type,
            feedback_status,
            evaluation,
            depot_id,
            region_id,
            client_price,
            currency,
            cancel_reason_type,
            cancel_reason_message,
            short_order_id,
            grocery_flow_version,
            entrance,
            comment,
            promocode,
            promocode_valid,
            promocode_sum,
            dispatch_id,
            dispatch_status,
            dispatch_cargo_status,
            dispatch_delivery_eta,
            dispatch_start_delivery_ts,
            dispatch_courier_name,
            dispatch_courier_first_name,
            dispatch_courier_id,
            dispatch_delivered_eta_ts,
            dispatch_pickuped_eta_ts,
            dispatch_track_version,
            dispatch_transport_type,
            dispatch_driver_id,
            dispatch_car_number,
            dispatch_car_model,
            dispatch_car_color,
            dispatch_car_color_hex,
            tips,
            finished,
            finish_started,
            billing_flow,
            order_revision,
            dispatch_cargo_revision,
            billing_settings_version,
            dispatch_flow,
            dispatch_status_meta,
            manual_update_enabled,
            informer_key,
            cancel_reason_meta,
            vip_type,
            wms_logistic_tags,
            push_notification_enabled,
            personal_email_id,
        ) = result

        self.order_id = order_id
        self.eats_order_id = eats_order_id
        self.order_version = order_version
        self.status = status
        self.status_updated = status_updated
        self.desired_status = desired_status
        self.idempotency_token = idempotency_token
        self.cart_id = cart_id
        self.child_cart_id = child_cart_id
        self.cart_version = cart_version
        self.offer_id = offer_id
        self.taxi_user_id = taxi_user_id
        self.eats_user_id = eats_user_id
        self.locale = locale
        self.user_info = user_info
        self.phone_id = phone_id
        self.personal_phone_id = personal_phone_id
        self.app_info = app_info
        self.created = created
        self.updated = updated
        self.due = due
        self.location = location
        self.place_id = place_id
        self.country = country
        self.city = city
        self.street = street
        self.house = house
        self.floor = floor
        self.flat = flat
        self.doorcode = doorcode
        self.doorcode_extra = doorcode_extra
        self.building_name = building_name
        self.doorbell_name = doorbell_name
        self.left_at_door = left_at_door
        self.meet_outside = meet_outside
        self.no_door_call = no_door_call
        self.postal_code = postal_code
        self.user_ip = user_ip
        self.user_agent = user_agent
        self.yandex_uid = yandex_uid
        self.session = session
        self.bound_sessions = bound_sessions
        self.state = OrderState(
            wms_reserve_status=wms_reserve_status,
            hold_money_status=hold_money_status,
            close_money_status=close_money_status,
            assembling_status=assembling_status,
            tips_status=tips_status,
        )
        self.edit_status = edit_status
        self.correcting_type = correcting_type
        self.feedback_status = feedback_status
        self.evaluation = evaluation
        self.depot_id = depot_id
        self.region_id = region_id
        self.client_price = client_price
        self.currency = currency
        self.cancel_reason_type = cancel_reason_type
        self.cancel_reason_message = cancel_reason_message
        self.short_order_id = short_order_id
        self.grocery_flow_version = grocery_flow_version
        self.entrance = entrance
        self.comment = comment
        self.promocode = promocode
        self.promocode_valid = promocode_valid
        self.promocode_sum = promocode_sum
        self.dispatch_status_info = DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status=dispatch_status,
            dispatch_cargo_status=dispatch_cargo_status,
            dispatch_delivery_eta=dispatch_delivery_eta,
            dispatch_start_delivery_ts=dispatch_start_delivery_ts,
            dispatch_courier_name=dispatch_courier_name,
            dispatch_courier_first_name=dispatch_courier_first_name,
            dispatch_courier_id=dispatch_courier_id,
            dispatch_delivered_eta_ts=dispatch_delivered_eta_ts,
            dispatch_pickuped_eta_ts=dispatch_pickuped_eta_ts,
            dispatch_track_version=dispatch_track_version,
            dispatch_transport_type=dispatch_transport_type,
            dispatch_driver_id=dispatch_driver_id,
            dispatch_cargo_revision=dispatch_cargo_revision,
            dispatch_status_meta=dispatch_status_meta,
            dispatch_car_number=dispatch_car_number,
            dispatch_car_model=dispatch_car_model,
            dispatch_car_color=dispatch_car_color,
            dispatch_car_color_hex=dispatch_car_color_hex,
            failure_reason_type=dispatch_cargo_status,
        )
        self.tips = (tips,)
        self.finished = finished
        self.finish_started = finish_started
        self.billing_flow = billing_flow
        self.order_revision = order_revision
        self.billing_settings_version = billing_settings_version
        self.dispatch_flow = dispatch_flow
        self.manual_update_enabled = manual_update_enabled
        self.informer_key = informer_key
        self.cancel_reason_meta = cancel_reason_meta
        self.vip_type = vip_type
        self.wms_logistic_tags = wms_logistic_tags
        self.push_notification_enabled = push_notification_enabled
        self.personal_email_id = personal_email_id

        cursor.execute(SELECT_CONTACTS_SQL, [self.order_id])
        result_contacts = cursor.fetchone()
        if result_contacts:
            (order_id, phone_id, name) = result_contacts

            self.gift_info = GiftInfo(phone_id=phone_id, name=name)
        else:
            self.gift_info = None

        cursor.execute(SELECT_ADDITIONAL_SQL, [self.order_id])
        result_additional = cursor.fetchone()
        if result_additional:
            (
                order_id,
                appmetrica_device_id,
                app_name,
                order_settings,
                timeslot_start,
                timeslot_end,
                timeslot_request_kind,
                is_dispatch_request_started,
            ) = result_additional

            self.appmetrica_device_id = appmetrica_device_id
            self.app_name = app_name
            self.order_settings = order_settings
            self.timeslot_start = timeslot_start
            self.timeslot_end = timeslot_end
            self.timeslot_request_kind = timeslot_request_kind
            self.is_dispatch_request_started = is_dispatch_request_started
        else:
            self.appmetrica_device_id = None
            self.app_name = None

        cursor.execute(SELECT_PERFORMER_SQL, [self.order_id])
        result_performer = cursor.fetchone()
        if result_performer:
            (
                order_id,
                self.dispatch_performer.driver_id,
                self.dispatch_performer.eats_courier_id,
                self.dispatch_performer.courier_full_name,
                self.dispatch_performer.first_name,
                self.dispatch_performer.organization_name,
                self.dispatch_performer.legal_address,
                self.dispatch_performer.ogrn,
                self.dispatch_performer.work_schedule,
                self.dispatch_performer.personal_tin_id,
                self.dispatch_performer.vat,
                self.dispatch_performer.balance_client_id,
                self.dispatch_performer.billing_type,
                self.dispatch_performer.car_number,
                self.dispatch_performer.car_model,
                self.dispatch_performer.car_color,
                self.dispatch_performer.car_color_hex,
            ) = result_performer

        cursor.execute(SELECT_PAYMENTS_SQL, [self.order_id])
        result_payments = cursor.fetchall()
        if result_payments:
            self.payment_operations = []
            for operation in result_payments:
                (
                    order_id,
                    operation_id,
                    operation_type,
                    status,
                    items,
                    errors,
                    compensation_id,
                ) = operation
                self.payment_operations += [
                    PaymentOperation(
                        order_id=order_id,
                        operation_id=operation_id,
                        operation_type=operation_type,
                        status=status,
                        items=items,
                        errors=errors,
                        compensation_id=compensation_id,
                    ),
                ]

    def remove(self):
        cursor = self.pg_db.cursor()
        cursor.execute(REMOVE_SQL, [self.order_id])

    def fetch_history(self):
        cursor = self.pg_db.cursor()
        cursor.execute(FETCH_HISTORY_SQL, [self.order_id])
        return cursor.fetchall()

    def fetch_payments(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_PAYMENTS_SQL, [self.order_id])
        return cursor.fetchall()

    def location_as_point(self):
        point = ast.literal_eval(self.location)
        return [point[0], point[1]]

    def check_order_history(self, event_type, event_data):
        history = self.fetch_history()
        assert (event_type, event_data) in history, history

    def check_payment_operation(self, payment_operation):
        payments = self.fetch_payments()
        assert payment_operation in payments


class Informer:
    def __init__(
            self,
            pgsql,
            order_id,
            informer_type='custom',
            compensation_type=None,
            situation_code=None,
            cancel_reason=None,
            raw_compensation_info=None,
            created=DEFAULT_CREATED,
            insert_in_pg=True,
    ):
        self.pg_db = pgsql['grocery_orders_tracking']

        self.order_id = order_id
        self.informer_type = informer_type
        self.compensation_type = compensation_type
        self.situation_code = situation_code
        self.cancel_reason = cancel_reason
        self.created = created

        if raw_compensation_info:
            self.raw_compensation_info = json.dumps(raw_compensation_info)
        else:
            self.raw_compensation_info = None

        if insert_in_pg:
            self._update_db()

    def _update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_INFORMER_SQL,
            [
                self.order_id,
                self.informer_type,
                self.created,
                self.compensation_type,
                self.situation_code,
                self.cancel_reason,
                self.raw_compensation_info,
            ],
        )

    def compare_with_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_INFORMER_SQL, [self.order_id])
        results = cursor.fetchmany()
        assert results

        for result in results:
            assert result
            (
                order_id,
                informer_type,
                # created
                _,
                compensation_type,
                situation_code,
                cancel_reason,
                raw_compensation_info,
            ) = result

            if informer_type == 'products_feedback':
                continue
            else:
                assert self.order_id == order_id
                assert self.informer_type == informer_type
                assert self.compensation_type == compensation_type
                assert self.situation_code == situation_code
                assert self.cancel_reason == cancel_reason

                if self.raw_compensation_info:
                    assert (
                        json.loads(self.raw_compensation_info)
                        == raw_compensation_info
                    )
                else:
                    assert not raw_compensation_info

    def check_empty_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_INFORMER_SQL, [self.order_id])
        result = cursor.fetchone()
        assert not result

    def check_no_informers_in_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_INFORMER_TYPE_SQL, [self.order_id])
        result = cursor.fetchone()
        assert not result or result[0] == 'products_feedback'


@dataclasses.dataclass
class TimeInterval:
    interval_type: str
    time_from: str
    time_to: str

    def as_object(self):
        result = {
            'type': self.interval_type,
            'from': self.time_from,
            'to': self.time_to,
        }
        return result


@dataclasses.dataclass
class CargoRoutePoint:
    point_id: int
    short_order_id: str
    visit_order: int
    type: str

    coordinates: Sequence[float]
    country: Optional[str]
    city: Optional[str]
    street: Optional[str]
    building: Optional[str]
    floor: Optional[str]
    flat: Optional[str]
    door_code: Optional[str]
    phone: str
    name: str
    comment: str
    place_id: str
    time_intervals: List[TimeInterval]
    door_code_extra: Optional[str] = None
    building_name: Optional[str] = None
    doorbell_name: Optional[str] = None
    leave_under_door: Optional[bool] = None
    visited_at_expected_ts: Optional[str] = None
    entrance: Optional[str] = None
    visit_status: str = 'pending'

    def as_object(self):
        result = {
            'point_id': self.point_id,
            'type': self.type,
            'visit_order': self.visit_order,
            'external_order_id': self.short_order_id,
            'skip_confirmation': True,
            'address': {
                'coordinates': self.coordinates,
                'comment': self.comment,
            },
            'contact': {'phone': self.phone, 'name': self.name},
        }
        if self.time_intervals:
            result['time_intervals'] = self.time_intervals
        if self.leave_under_door is not None:
            result['leave_under_door'] = self.leave_under_door
        address_parts = []
        if self.country:
            result['address']['country'] = self.country
            address_parts.append(self.country)
        if self.city:
            result['address']['city'] = self.city
            address_parts.append(self.city)
        if self.street:
            result['address']['street'] = self.street
            address_parts.append(self.street)
        if self.building:
            result['address']['building'] = self.building
            address_parts.append(self.building)
        if self.building_name:
            result['address']['building_name'] = self.building_name
        if self.floor:
            result['address']['sfloor'] = self.floor
        if self.flat:
            result['address']['sflat'] = self.flat
            address_parts.append(self.flat)
        if self.door_code:
            result['address']['door_code'] = self.door_code
        if self.door_code_extra:
            result['address']['door_code_extra'] = self.door_code_extra
        if self.doorbell_name:
            result['address']['doorbell_name'] = self.doorbell_name
        if self.place_id:
            result['address']['uri'] = self.place_id
        if self.entrance is not None:
            result['address']['porch'] = self.entrance

        full_address = ', '.join(address_parts)
        result['address']['fullname'] = full_address
        result['address']['shortname'] = full_address

        return result

    def as_response_object(self):
        result = self.as_object()
        result['id'] = result['point_id']
        del result['point_id']
        result['visit_status'] = self.visit_status
        if self.visited_at_expected_ts:
            result['visited_at'] = {'expected': self.visited_at_expected_ts}
        return result
