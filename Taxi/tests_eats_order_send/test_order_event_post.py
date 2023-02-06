# flake8: noqa
# pylint: disable=import-error,wildcard-import

import json
import pytz


async def test_order_event_post(taxi_eats_order_send, pgsql, load_json):
    events = load_json('events.json')
    assert len(events['events']) == 6

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    events_db = get_events(pgsql)
    assert len(events_db) == 6

    check_events_data(events, events_db)


async def test_order_event_post_without_meta(
        taxi_eats_order_send, pgsql, load_json,
):
    events = load_json('event_without_meta.json')

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 400


async def test_order_event_post_idempotency(
        taxi_eats_order_send, pgsql, load_json,
):
    add_event(
        pgsql,
        1,
        'update_courier_arrival',
        '2021-01-01T15:15:27.01+00:00',
        'update_courier_arrival_1',
        {
            'arrival_time': '2021-01-01T16:05:27.01+00:00',
            'event_type': 'update_courier_arrival',
        },
    )
    assert len(get_events(pgsql)) == 1

    events = load_json('events.json')
    assert len(events['events']) == 6

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    events_db = get_events(pgsql)
    assert len(events_db) == 6

    check_events_data(events, events_db)


def check_events_data(events, events_db):
    events['events'].sort(key=lambda event: event['idempotency_token'])
    events_db.sort(key=lambda event: event[3])
    events_size = len(events['events'])

    for i in range(0, events_size - 1):
        event_db = events_db[i]
        event_json = events['events'][i]
        # order_id
        assert event_db[0] == event_json['order_id']
        # event_type
        assert event_db[1] == event_json['payload']['event_type']
        # created_at
        assert format_datetime(event_db[2]) == event_json['created_at']
        # idempotency_token
        assert event_db[3] == event_json['idempotency_token']
        # payload
        assert json.dumps(event_db[4], sort_keys=True) == json.dumps(
            event_json['payload'], sort_keys=True,
        )


def format_datetime(stamp):
    # microseconds convert 'ffffff+' to 'ff+'
    return stamp.astimezone(pytz.utc).isoformat().replace('0000+', '+')


def add_event(
        pgsql, order_id, event_type, created_at, idempotency_token, payload,
):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        f"""INSERT INTO eats_order_send.events (order_id, type, created_at, idempotency_token, payload)
        VALUES ('{order_id}', '{event_type}', '{created_at}', '{idempotency_token}', '{json.dumps(payload)}')""",
    )


def get_events(pgsql):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        """SELECT order_id, type, created_at, idempotency_token, payload
        FROM eats_order_send.events""",
    )
    return list(cursor)
