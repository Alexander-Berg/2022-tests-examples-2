import datetime

from . import consts


def skip_minutes_dt(minutes):
    return consts.NOW_DT + datetime.timedelta(minutes=minutes)


def retry_processing(handle, mocked_time, taxi_grocery_orders):
    async def _do(
            order,
            compensation_id,
            after_minutes,
            event_policy,
            expected_code,
            payload=None,
            compensation_source=None,
            compensation_value=None,
            items=None,
    ):
        mocked_time.set(skip_minutes_dt(after_minutes))

        request_json = {
            'order_id': order.order_id,
            'compensation_id': compensation_id,
            'times_called': 1,
            'event_policy': event_policy,
            'order_version': order.order_version,
            'payload': {},
        }

        if items is not None:
            request_json['items'] = items
        if payload is not None:
            request_json['payload'] = payload
        if compensation_source is not None:
            request_json['compensation_source'] = compensation_source
        if compensation_value is not None:
            request_json['compensation_value'] = compensation_value

        response = await taxi_grocery_orders.post(handle, json=request_json)

        assert response.status_code == expected_code

    return _do
