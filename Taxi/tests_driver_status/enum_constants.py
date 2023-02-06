class LegacyDriverStatus:
    Offline = 'offline'
    Online = 'free'
    Busy = 'busy'


class DriverStatus:
    Offline = 'offline'
    Online = 'online'
    Busy = 'busy'
    __values = {Offline, Online, Busy}

    @staticmethod
    def contains(value):
        return value in DriverStatus.__values

    @staticmethod
    def from_legacy(status):
        if status == 'free':
            return DriverStatus.Online
        return status


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
    __values = {
        kNone,
        kDriving,
        kWaiting,
        kTransporting,
        kComplete,
        kFailed,
        kCancelled,
        kExpired,
        kPreexpired,
        kUnknown,
    }

    @staticmethod
    def contains(value):
        return value in OrderStatus.__values


class ProcessingStatus:
    kPending = 'pending'
    kAssigned = 'assigned'
    kFinished = 'finished'
    kCancelled = 'cancelled'
    kUnknown = 'unknown'


ACTIVE_ORDER_STATUSES = {
    OrderStatus.kDriving,
    OrderStatus.kWaiting,
    OrderStatus.kTransporting,
}
