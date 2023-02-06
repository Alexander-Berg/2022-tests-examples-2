# flake8: noqa
# pylint: disable=import-error,wildcard-import

import json


SENDING_TASK = {
    'order_id': '1',
    'created_at': '2021-01-01T15:30:27.01+00:00',
    'planned_on': '2021-01-01T17:30:27.01+00:00',
    'sent_at': '2021-01-01T17:33:27.01+00:00',
    'is_canceled': False,
    'reasons': {
        'events': [
            'create_order_1',
            'update_courier_arrival_1',
            'update_courier_departure_1',
        ],
        'features': {
            'max_send_time_feature': {
                'enabled': True,
                'delta': 1320,
                'applied': False,
            },
            'min_send_time_feature': {'enabled': False, 'applied': False},
        },
    },
}


async def test_order_info_get(taxi_eats_order_send, load_json, add_sending):
    # fill events table
    events = load_json('events.json')
    response_post = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response_post.status == 204

    # fill sending tables
    add_sending(True, SENDING_TASK)

    response_get = await taxi_eats_order_send.get(
        '/internal/eats-order-send/v1/order/info?order_id=1',
    )
    assert response_get.status == 200

    # check events
    response_events = response_get.json()['events']
    compare_events(events, response_events, '1', 4)

    # check sending
    response_sending_log = response_get.json()['sending_tasks']
    assert len(response_sending_log) == 1
    assert response_sending_log[0] == SENDING_TASK


async def test_order_info_get_without_sending(
        taxi_eats_order_send, load_json, add_sending,
):
    # fill events table
    events = load_json('events.json')
    response_post = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response_post.status == 204

    # fill sending tables
    add_sending(True, SENDING_TASK)

    response_get = await taxi_eats_order_send.get(
        '/internal/eats-order-send/v1/order/info?order_id=2',
    )
    assert response_get.status == 200

    # check events
    response_events = response_get.json()['events']
    compare_events(events, response_events, '2', 2)

    # check sending
    assert 'sending_tasks' not in response_get.json()['events']


async def test_order_info_get_not_found(taxi_eats_order_send, load_json):
    events = load_json('events.json')
    response_post = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response_post.status == 204

    response_get = await taxi_eats_order_send.get(
        '/internal/eats-order-send/v1/order/info?order_id=3',
    )
    assert response_get.status == 404


def compare_events(events, response_events, order_id, size):
    events_cut = [
        event for event in events['events'] if event['order_id'] == order_id
    ]
    assert len(events_cut) == size
    assert len(response_events) == size
    assert json.dumps(response_events, sort_keys=True) == json.dumps(
        events_cut, sort_keys=True,
    )


async def test_order_info_get_bad_request(taxi_eats_order_send):
    response_get = await taxi_eats_order_send.get(
        '/internal/eats-order-send/v1/order/info?%',
    )
    assert response_get.status == 400
