import dataclasses
import datetime
from typing import Optional

import psycopg2


@dataclasses.dataclass
class RuleDraft:
    rule_id: str
    internal_draft_id: str
    rule_type: str
    tariff_zone: str
    tariff: str
    timezone: str
    starts_at: datetime.datetime
    ends_at: datetime.datetime
    geoarea: str
    tag: str
    branding: str
    min_activity_points: int
    rates: dict
    created_at: datetime.datetime
    currency: Optional[str]
    window_size: Optional[int]
    unique_driver_id: Optional[str]
    schedule_ref: Optional[str]
    key_attrs_hash: str
    stop_tag: Optional[str]


@dataclasses.dataclass
class ScheduleRange:
    during: psycopg2.extras.NumericRange
    value: str
