# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json
from dataclasses import asdict, dataclass  # noqa: IS001 pylint: disable=C5521

from . import models


@dataclass
class BaseEvent:
    def dict(self):
        return asdict(self)

    def json(self):
        return json.dumps(self.dict(), separators=(',', ':'))

    @property
    def consumer(self) -> str:
        return 'base-event-consumer'


@dataclass
class GroceryOrderStatusChangedEvent(BaseEvent):
    order_id: str = 'test_order_id'
    order_status: str = 'assembled'
    timestamp: str = models.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-order-status-changed-event'
