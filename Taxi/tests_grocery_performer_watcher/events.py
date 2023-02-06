# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json
from dataclasses import asdict, dataclass  # noqa: IS001 pylint: disable=C5521


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
class GroceryOrderMatchedEvent(BaseEvent):
    performer_id: str
    order_id: str
    depot_id: str
    delivery_type: str
    claim_id: str
    timestamp: str

    @property
    def consumer(self) -> str:
        return 'grocery-order-matched'
