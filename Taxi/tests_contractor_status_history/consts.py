# pylint: disable=import-error
# pylint: disable=import-only-modules
from models.status_history.OrderStatus import OrderStatus as FbsOrderStatus
from models.status_history.Status import Status as FbsStatus
# pylint: enable=import-error
# pylint: enable=import-only-modules


class Status:
    Offline = 'offline'
    Online = 'online'
    Busy = 'busy'


class OrderStatus:
    kNone = 'none'
    kDriving = 'driving'
    kWaiting = 'waiting'
    kTransporting = 'transporting'
    kComplete = 'complete'
    kFailed = 'failed'
    kCancelled = 'cancelled'
    kExpired = 'expired'
    kPreexpired = 'preexpired'
    kUnknown = 'unknown'


FBS_TO_CONTRACTOR_STATUS = {
    FbsStatus.Offline: Status.Offline,
    FbsStatus.Online: Status.Online,
    FbsStatus.Busy: Status.Busy,
}

FBS_TO_ORDER_STATUS = {
    FbsOrderStatus.None_: OrderStatus.kNone,
    FbsOrderStatus.Driving: OrderStatus.kDriving,
    FbsOrderStatus.Waiting: OrderStatus.kWaiting,
    FbsOrderStatus.Transporting: OrderStatus.kTransporting,
    FbsOrderStatus.Complete: OrderStatus.kComplete,
    FbsOrderStatus.Failed: OrderStatus.kFailed,
    FbsOrderStatus.Cancelled: OrderStatus.kCancelled,
    FbsOrderStatus.Preexpired: OrderStatus.kPreexpired,
    FbsOrderStatus.Expired: OrderStatus.kExpired,
    FbsOrderStatus.Unknown: OrderStatus.kUnknown,
}

CONTRACTOR_STATUS_TO_FBS = {
    Status.Offline: FbsStatus.Offline,
    Status.Online: FbsStatus.Online,
    Status.Busy: FbsStatus.Busy,
}

ORDER_STATUS_TO_FBS = {
    OrderStatus.kNone: FbsOrderStatus.None_,
    OrderStatus.kDriving: FbsOrderStatus.Driving,
    OrderStatus.kWaiting: FbsOrderStatus.Waiting,
    OrderStatus.kTransporting: FbsOrderStatus.Transporting,
    OrderStatus.kComplete: FbsOrderStatus.Complete,
    OrderStatus.kFailed: FbsOrderStatus.Failed,
    OrderStatus.kCancelled: FbsOrderStatus.Cancelled,
    OrderStatus.kPreexpired: FbsOrderStatus.Preexpired,
    OrderStatus.kExpired: FbsOrderStatus.Expired,
    OrderStatus.kUnknown: FbsOrderStatus.Unknown,
}
