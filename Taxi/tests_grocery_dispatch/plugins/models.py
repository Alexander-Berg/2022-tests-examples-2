# flake8: noqa IS001
# pylint: disable=import-only-modules, no-name-in-module

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import uuid
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    item_id: str = 'test_item_id'
    title: str = 'test_order_item'
    price: str = '12.99'
    currency: str = 'RUB'
    quantity: str = '1'
    item_tags: list = []
    weight: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    depth: Optional[int] = None

    class Config:
        validate_assignment = True


class TimeSlot(BaseModel):
    interval_start: datetime = datetime.fromisoformat(
        '2020-11-05T16:28:00+00:00',
    )
    interval_end: datetime = datetime.fromisoformat(
        '2020-10-01T16:28:00+00:00',
    )

    class Config:
        validate_assignment = True


class OrderInfo(BaseModel):
    order_id: str = Field(default_factory=lambda: f'test-order-{uuid.uuid4()}')
    depot_id: str = '123456'
    location: List[float] = [33.56, 55.67]
    zone_type: str = 'pedestrian'
    max_eta: int = 900
    personal_phone_id: str = 'default_personal_phone_id'
    short_order_id: str = 'short-order-id-1'
    created: datetime = datetime.fromisoformat('2020-10-05T16:28:00+00:00')
    items: List[OrderItem] = [OrderItem()]
    user_locale: str = 'ru'
    due: Optional[datetime] = None
    min_eta: Optional[int] = None
    yandex_uid: Optional[str] = None
    user_name: Optional[str] = None
    country: Optional[str] = 'country'
    city: Optional[str] = 'city'
    street: Optional[str] = 'street'
    building: Optional[str] = 'building'
    floor: Optional[str] = 'floor'
    flat: Optional[str] = 'flat'
    porch: Optional[str] = None
    door_code: Optional[str] = 'door code'
    door_code_extra: Optional[str] = 'door code extra'
    comment: Optional[str] = 'user comment'
    map_uri: Optional[str] = None
    building_name: Optional[str] = 'building name'
    doorbell_name: Optional[str] = 'doorbell_name'
    postal_code: Optional[str] = None
    additional_phone_code: Optional[str] = None
    market_slot: Optional[TimeSlot] = None

    class Config:
        validate_assignment = True


class PerformerInfo(BaseModel):
    performer_id: str = 'test_performer_id'
    eats_profile_id: str = 'test_eats_profile_id'
    name: str = 'Тестовый Курьер Иванович'
    first_name: Optional[str] = None
    legal_name: Optional[str] = None
    transport_type: Optional[str] = None
    driver_id: Optional[str] = 'test_driver_id'
    park_id: Optional[str] = 'test_park_id'
    taxi_alias_id: Optional[str] = None

    class Config:
        validate_assignment = True


class StatusMeta(BaseModel):
    cargo_dispatch: Optional[Dict] = None
    is_order_assembled: Optional[bool] = False

    class Config:
        validate_assignment = True


class Status(str, Enum):
    idle = 'idle'
    scheduled = 'scheduled'
    rescheduling = 'rescheduling'
    matching = 'matching'
    offered = 'offered'
    matched = 'matched'
    delivering = 'delivering'
    delivery_arrived = 'delivery_arrived'
    ready_for_delivery_confirmation = 'ready_for_delivery_confirmation'
    delivered = 'delivered'
    canceling = 'canceling'
    canceled = 'canceled'
    revoked = 'revoked'
    finished = 'finished'


class DispatchInfo(BaseModel):
    dispatch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dispatch_name: str = 'test'
    version: int = 0
    status: Optional[Status] = Status.idle  # None when deleted in history
    status_updated: datetime = datetime.now(timezone.utc)
    order: OrderInfo = OrderInfo()
    status_meta: StatusMeta = StatusMeta()
    performer: Optional[PerformerInfo] = None
    wave: int = 0
    failure_reason_type: Optional[str] = ''

    class Config:
        validate_assignment = True


@dataclass
class Point:
    lon: float = 0.0
    lat: float = 0.0


class DispatchExtraInfo(BaseModel):
    dispatch_id: str
    eta_timestamp: Optional[datetime] = None
    smoothed_eta_timestamp: Optional[datetime] = None
    smoothed_eta_eval_time: Optional[datetime] = None
    result_eta_timestamp: Optional[datetime] = None
    heuristic_polyline_eta_ts: Optional[datetime] = None
    performer_position: Optional[Point] = None
    pickup_eta_seconds: Optional[timedelta] = None
    deliver_prev_eta_seconds: Optional[timedelta] = None
    deliver_current_eta_seconds: Optional[timedelta] = None
    smoothed_heuristic_eval_time: Optional[datetime] = None
    smoothed_heuristic_eta_ts: Optional[datetime] = None

    class Config:
        validate_assignment = True


class CargoClaim(BaseModel):
    claim_id: str = 'test_claim_id'
    dispatch_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    claim_status: str = 'new'
    claim_version: int = 0
    is_current_claim: bool = True
    auth_token_key: Optional[str] = 'test_auth_token'
    wave: int = 0
    order_location: Optional[Point] = None

    class Config:
        validate_assignment = True


class RescheduleState(BaseModel):
    dispatch_id: str = ''
    idempotency_token: str = ''
    wave: int = 0
    options: Optional[Dict] = None
    status: str = ''

    class Config:
        validate_assignment = True
