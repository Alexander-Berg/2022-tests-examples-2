import datetime
import typing

from . import consts

DEFAULT_SKIPPED_KEYS = ('order_info',)
ALL_EVENTS = 0


def skip_minutes_dt(minutes):
    return consts.NOW_DT + datetime.timedelta(minutes=minutes)


def skip_minutes(minutes):
    return (skip_minutes_dt(minutes)).isoformat()


def retry_processing(handle, mocked_time, taxi_grocery_orders):
    async def _do(
            order,
            after_minutes,
            event_policy,
            expected_code,
            to_revert=None,
            items=None,
    ):
        mocked_time.set(skip_minutes_dt(after_minutes))

        request_json = {
            'order_id': order.order_id,
            'times_called': 1,
            'event_policy': event_policy,
            'order_version': order.order_version,
            'order_revision': order.order_revision,
            'to_revert': to_revert,
            'payload': {},
        }
        if items is not None:
            request_json['items'] = items

        response = await taxi_grocery_orders.post(handle, json=request_json)

        assert response.status_code == expected_code

    return _do


def get_last_processing_events(
        processing,
        order_id,
        queue,
        count=ALL_EVENTS,
        skip_keys=DEFAULT_SKIPPED_KEYS,
):
    events = list(processing.events(scope='grocery', queue=queue))
    order_events = events[-count:]

    for event in order_events:
        assert event.item_id == order_id
        for key in skip_keys:
            event.payload.pop(key, None)

    return order_events


def get_last_processing_payloads(
        processing,
        order_id,
        queue,
        count=ALL_EVENTS,
        skip_keys=DEFAULT_SKIPPED_KEYS,
):
    events = get_last_processing_events(
        processing, order_id, queue, count, skip_keys,
    )
    return [event.payload for event in events]


def make_set_state_payload(
        success: bool, operation_id: str = '1', operation_type: str = None,
) -> dict:
    payload: typing.Dict[str, typing.Any] = {
        'operation_id': operation_id,
        'operation_type': operation_type,
    }
    if not success:
        payload['errors'] = [
            {
                'payment_type': 'applepay',
                'error_reason_code': 'not_enough_funds',
            },
        ]
    return payload


def check_set_state_event(processing, order_id, compensation_id, is_success):
    events_compensations = list(
        processing.events(scope='grocery', queue='compensations'),
    )

    assert len(events_compensations) == 1
    event = events_compensations[0]
    assert event.payload['compensation_id'] == compensation_id
    assert event.payload['order_id'] == order_id
    assert event.payload['reason'] == 'set_compensation_state'
    assert event.payload['state'] == is_success
