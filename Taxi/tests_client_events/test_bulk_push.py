import datetime

import pytest


@pytest.mark.now('2021-02-20T00:00:00Z')
async def test_mongo_event_storage(taxi_client_events, mongodb):
    request_body = {
        'service': 'service',
        'channels': ['channel1', 'channel2'],
        'event': 'event',
        'event_id': 'event_id',
        'payload': {'some': 'data'},
        'ttl': 600,
    }
    n_events = len(request_body['channels'])

    response = await taxi_client_events.post('bulk-push', json=request_body)
    assert response.status_code == 200

    statuses = [item['status'] for item in response.json()['items']]
    assert len(statuses) == n_events
    assert set(statuses) == {'ok'}

    events = list(mongodb.client_events_events.find({}))
    assert len(events) == n_events

    for idx in range(1, n_events + 1):
        service_channel = f'service/channel{idx}'
        event = mongodb.client_events_events.find_one(
            {'service_channel': service_channel},
        )
        assert event is not None, f'Event not found: {service_channel}'

        expected_event = {
            'service_channel': service_channel,
            'service': 'service',
            'channel': f'channel{idx}',
            'event': 'event',
            'event_id': 'event_id',
            'payload': '{"some":"data"}',
            'expires': datetime.datetime(2021, 2, 20, 0, 10),
        }
        for key, value in expected_event.items():
            assert event[key] == value


async def test_duplicate_channels(taxi_client_events):

    channels = [
        {'name': 'unique1', 'for_the_first_time': True},
        {'name': 'duplicate1', 'for_the_first_time': True},
        {'name': 'unique2', 'for_the_first_time': True},
        {'name': 'unique3', 'for_the_first_time': True},
        {'name': 'duplicate1', 'for_the_first_time': False},
        {'name': 'unique4', 'for_the_first_time': True},
        {'name': 'unique5', 'for_the_first_time': True},
        {'name': 'duplicate2', 'for_the_first_time': True},
        {'name': 'duplicate2', 'for_the_first_time': False},
        {'name': 'unique6', 'for_the_first_time': True},
    ]

    request_body = {
        'service': 'service',
        'channels': [channel['name'] for channel in channels],
        'event': 'event',
        'event_id': 'event_id',
        'payload': {'some': 'data'},
        'ttl': 600,
    }

    response = await taxi_client_events.post('bulk-push', json=request_body)
    assert response.status_code == 200

    response_result_is_ok = [
        (item['status'] == 'ok') for item in response.json()['items']
    ]
    assert response_result_is_ok == [
        channel['for_the_first_time'] for channel in channels
    ]
