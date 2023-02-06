# pylint: disable=import-error
# pylint: disable=import-only-modules
import flatbuffers
from models.status_history import Event as FbsStatusHistoryEvent
from models.status_history import History as FbsStatusHistory

from tests_contractor_status_history.consts import CONTRACTOR_STATUS_TO_FBS
from tests_contractor_status_history.consts import FBS_TO_CONTRACTOR_STATUS
from tests_contractor_status_history.consts import FBS_TO_ORDER_STATUS
from tests_contractor_status_history.consts import ORDER_STATUS_TO_FBS
import tests_contractor_status_history.utils as utils
# pylint: enable=import-only-modules


def _build_status_event_fbs_item(builder, event):
    FbsStatusHistoryEvent.EventStartOrderStatusesVector(
        builder, len(event['orders']),
    )
    for order in reversed(event['orders']):
        builder.PrependUint8(ORDER_STATUS_TO_FBS[order])
    items = builder.EndVector(len(event['orders']))
    FbsStatusHistoryEvent.EventStart(builder)
    FbsStatusHistoryEvent.EventAddEventTs(
        builder, int(event['ts'].timestamp() * 1000.0),
    )
    FbsStatusHistoryEvent.EventAddStatus(
        builder, CONTRACTOR_STATUS_TO_FBS[event['status']],
    )
    FbsStatusHistoryEvent.EventAddOrderStatuses(builder, items)
    return FbsStatusHistoryEvent.EventEnd(builder)


def unpack_status_history(data):
    history = {'events': []}
    fb_root = FbsStatusHistory.History.GetRootAsHistory(data, 0)
    for i in range(0, fb_root.EventsLength()):
        fb_event = fb_root.Events(i)
        event = {}
        event['ts'] = utils.date_from_ms(fb_event.EventTs())
        event['status'] = FBS_TO_CONTRACTOR_STATUS[fb_event.Status()]
        event['orders'] = []
        for j in range(0, fb_event.OrderStatusesLength()):
            order_status = FBS_TO_ORDER_STATUS[fb_event.OrderStatuses(j)]
            event['orders'].append(order_status)
        history['events'].append(event)
    return history


def pack_status_history(history):
    builder = flatbuffers.Builder(initialSize=1024)
    events_fb = []
    for event in reversed(history['events']):
        events_fb.append(_build_status_event_fbs_item(builder, event))
    FbsStatusHistory.HistoryStartEventsVector(builder, len(events_fb))
    for event_fb in events_fb:
        builder.PrependUOffsetTRelative(event_fb)
    items = builder.EndVector(len(events_fb))
    FbsStatusHistory.HistoryStart(builder)
    FbsStatusHistory.HistoryAddEvents(builder, items)
    events_history = FbsStatusHistory.HistoryEnd(builder)
    builder.Finish(events_history)
    return builder.Output()
