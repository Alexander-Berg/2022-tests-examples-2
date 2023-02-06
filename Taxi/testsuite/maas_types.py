import dataclasses
import datetime
from typing import List
from typing import Optional


@dataclasses.dataclass
class TariffInfo:
    tariff_id: str
    trips_count: str
    duration_days: str
    taxi_price: str
    subscription_price: str


@dataclasses.dataclass
class StatusHistory:
    updated_at: datetime.datetime
    new_status: str
    reason: str


@dataclasses.dataclass
class Subscription:
    tariff_info: TariffInfo
    sub_id: str
    status: str
    maas_user_id: str
    phone_id: str
    coupon_id: str
    coupon_series_id: str
    status_history: List[StatusHistory]
    bought_through_go: bool = False
    created_at: Optional[datetime.datetime] = None
    expired_at: Optional[datetime.datetime] = None


@dataclasses.dataclass
class Order:
    order_id: str
    external_order_id: str
    maas_user_id: str
    phone_id: str
    maas_sub_id: str
    is_maas_order: bool
    maas_trip_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
