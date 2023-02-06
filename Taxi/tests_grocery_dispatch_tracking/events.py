# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json
from dataclasses import asdict, dataclass  # noqa: IS001 pylint: disable=C5521

from tests_grocery_dispatch_tracking import constants as const


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
class Event(BaseEvent):
    test_key: str = 'test_value'

    @property
    def consumer(self) -> str:
        return 'test-event'


@dataclass
class BulkEvent(BaseEvent):
    test_key: str = 'test_value'

    @property
    def consumer(self) -> str:
        return 'test-bulk-event'


@dataclass
class BadEvent(BaseEvent):
    bad_key: str = 'test_bad_value'

    @property
    def consumer(self) -> str:
        return 'test-event'


@dataclass
class BadBulkEvent(BaseEvent):
    bad_key: str = 'test_bad_value'

    @property
    def consumer(self) -> str:
        return 'test-bulk-event'


@dataclass
class GroceryOrderDeliveredEvent(BaseEvent):
    depot_id: str = const.DEPOT_ID_LEGACY
    order_id: str = const.ORDER_ID
    timestamp: str = const.NOW
    performer_id: str = const.PERFORMER_ID

    @property
    def consumer(self) -> str:
        return 'grocery-order-delivered'


@dataclass
class GroceryOrderDispatchReadyEvent(BaseEvent):
    depot_id: str
    order_id: str
    order_version: int = 0
    timestamp: str = const.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-order-dispatch-ready'


@dataclass
class GroceryOrderDispatchRequestEvent(BaseEvent):
    depot_id: str
    order_id: str
    timestamp: str = const.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-order-dispatch-request'


@dataclass
class GroceryOrderClosedEvent(BaseEvent):
    depot_id: str = const.DEPOT_ID_LEGACY
    order_id: str = const.ORDER_ID
    is_canceled: bool = False
    cancel_reason_type: str = 'timeout'
    cancel_reason_message: str = 'Order timed out'
    timestamp: str = const.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-order-closed'


@dataclass
class GroceryOrderCreatedEvent(BaseEvent):
    depot_id: str
    order_id: str
    max_eta: int = 55
    delivery_type: str = 'dispatch'
    timestamp: str = const.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-order-created'


@dataclass
class GroceryOrderAssembledEvent(BaseEvent):
    depot_id: str
    order_id: str
    order_version: int = 0
    timestamp: str = const.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-order-assembled'


@dataclass
class GroceryOrderAssembleReadyEvent(BaseEvent):
    depot_id: str
    order_id: str
    timestamp: str = const.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-order-assemble-ready'


@dataclass
class GroceryPerformerPickupOrderEvent(BaseEvent):
    depot_id: str
    order_id: str
    timestamp: str = const.NOW
    performer_id: str = const.PERFORMER_ID

    @property
    def consumer(self) -> str:
        return 'grocery-performer-pickup-order'


@dataclass
class GroceryPerformerShiftUpdated(BaseEvent):
    depot_id: str
    performer_id: str = const.PERFORMER_ID
    shift_id: str = const.SHIFT_ID
    status: const.ShiftStatus = const.ShiftStatus.open
    timestamp: str = const.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-performer-shift-update'


@dataclass
class GroceryPerformerReturnDepot(BaseEvent):
    depot_id: str = const.DEPOT_ID_LEGACY
    performer_id: str = const.PERFORMER_ID
    timestamp: str = const.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-performer-return-depot'


@dataclass
class GroceryOrderMatchedEvent(BaseEvent):
    depot_id: str = const.DEPOT_ID_LEGACY
    order_id: str = const.ORDER_ID
    performer_id: str = const.PERFORMER_ID
    delivery_type: str = 'courier'
    timestamp: str = const.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-order-matched'


@dataclass
class GroceryPerformerDeliveringArrived(BaseEvent):
    depot_id: str = const.DEPOT_ID_LEGACY
    order_id: str = const.ORDER_ID
    performer_id: str = const.PERFORMER_ID
    timestamp: str = const.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-performer-delivering-arrived'


@dataclass
class GroceryOrderDeliveryCanceled(BaseEvent):
    depot_id: str = const.DEPOT_ID_LEGACY
    order_id: str = const.ORDER_ID
    performer_id: str = const.PERFORMER_ID
    timestamp: str = const.NOW

    @property
    def consumer(self) -> str:
        return 'grocery-order-delivery-canceled'
