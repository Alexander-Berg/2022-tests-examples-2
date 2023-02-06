import dataclasses
import datetime
import decimal
import enum
import typing
from typing import Dict


class PromocodeSource(enum.Enum):
    taxi = 'taxi'
    eats = 'eats'


@dataclasses.dataclass
class CartPromocode:
    cart_id: str
    promocode: str
    currency: str
    source: PromocodeSource
    valid: bool
    discount: decimal.Decimal
    error_code: str
    properties: Dict


@dataclasses.dataclass
class Cart:
    user_type: str
    user_id: str
    session: str
    cart_id: str
    cart_version: typing.Optional[int]
    updated: datetime.datetime
    idempotency_token: typing.Optional[str]
    promocode: typing.Optional[str]
    payment_method_type: typing.Optional[str]
    payment_method_id: typing.Optional[str]
    payment_method_meta: typing.Optional[typing.Dict]
    status: str
    delivery_type: str
    cashback_flow: typing.Optional[str]
    delivery_cost: typing.Optional[str]
    child_cart_id: typing.Optional[str]
    bound_uids: typing.List[str]
    bound_sessions: typing.List[str]
    promocode_discount: typing.Optional[str] = None
    cashback_to_pay: typing.Optional[str] = None
    calculation_log: typing.Optional[typing.Dict] = None
    items_pricing: typing.Optional[typing.Dict] = None
    tips_amount: typing.Optional[str] = None
    tips_amount_type: typing.Optional[str] = None
    depot_id: typing.Optional[str] = None
    timeslot_start: typing.Optional[datetime.datetime] = None
    timeslot_end: typing.Optional[datetime.datetime] = None
    timeslot_request_kind: typing.Optional[str] = None
    service_fee: typing.Optional[decimal.Decimal] = None
    personal_phone_id: typing.Optional[str] = None
    yandex_uid: typing.Optional[str] = None
    anonym_id: typing.Optional[str] = None


@dataclasses.dataclass
class CartItem:
    item_id: str
    price: str
    quantity: str
    status: str = 'in_cart'
    reserved: typing.Optional[str] = None
    vat: typing.Optional[str] = None
    currency: str = 'RUB'
    refunded_quantity: str = '0'
    cashback: typing.Optional[str] = None
    is_expiring: typing.Optional[bool] = None
    supplier_tin: typing.Optional[str] = None
