import dataclasses
import datetime
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union


@dataclasses.dataclass
class Priority:
    name: str
    description: str
    tanker_keys_prefix: str
    status: str


@dataclasses.dataclass
class Preset:
    name: str
    description: str


@dataclasses.dataclass
class MatchedPreset:
    name: str
    description: str
    agglomeration: Optional[str]


@dataclasses.dataclass
class Version:
    sort_order: int
    created_at: datetime.datetime
    starts_at: datetime.datetime
    stops_at: Optional[datetime.datetime]


@dataclasses.dataclass
class Conditions:
    temporary: Optional[Dict[str, Any]]
    disabled: Optional[Dict[str, Any]]
    achievable: Optional[Dict[str, Any]]


@dataclasses.dataclass
class Item:
    priority: Priority
    preset: Union[MatchedPreset, Preset]
    version: Version
    rule: Dict[str, Any]
    payloads: Dict[str, Any]
    conditions: Conditions
    max_value: int = 0
