import datetime
import json

import pytest

from tests_client_events import helpers


async def test_bad_ttl(taxi_client_events):
    request_body = {
        'service': 'service',
        'channel': 'channel',
        'event': 'event',
        'ttl': 9999999,
    }
    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 400


async def test_bad_payload(taxi_client_events):
    request_body = {
        'service': 'service',
        'channel': 'channel',
        'event': 'event',
        'payload': [1, 2, 3],
    }

    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 400


@pytest.mark.config(
    CLIENT_EVENTS_STORAGE_SETTINGS={'max_ttl': 600, 'max_payload_size': 15},
)
async def test_large_payload(taxi_client_events):
    request_body = {
        'service': 'service',
        'channel': 'channel',
        'event': 'event',
        'payload': {'some': 'data'},
    }
    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 200

    request_body['payload'] = {'some': 'too large data'}
    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 413


@pytest.mark.now('2021-02-20T00:00:00Z')
async def test_mongo_event_storage(taxi_client_events, mongodb):
    request_body = {
        'service': 'service',
        'channel': 'channel',
        'event': 'event',
        'event_id': 'event_id',
        'payload': {'some': 'data'},
        'ttl': 600,
    }
    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 200
    assert 'version' in response.json()

    events = list(mongodb.client_events_events.find({}))
    assert len(events) == 1

    expected_event = {
        'service_channel': 'service/channel',
        'service': 'service',
        'channel': 'channel',
        'event': 'event',
        'event_id': 'event_id',
        'payload': '{"some":"data"}',
        'expires': datetime.datetime(2021, 2, 20, 0, 10),
    }
    for key, value in expected_event.items():
        assert events[0][key] == value

    updated_ts = events[0]['updated_ts']

    # push again and check that event was updated correctly

    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 200

    events = list(mongodb.client_events_events.find({}))
    assert len(events) == 1

    for key, value in expected_event.items():
        assert events[0][key] == value

    assert updated_ts < events[0]['updated_ts']


@helpers.TRANSLATIONS
@pytest.mark.config(
    CLIENT_EVENTS_SERVICES={
        '__default__': {
            'polling_delay': 30,
            'events': {
                '__default__': {'notification': {'enabled': True}, 'ttl': 600},
            },
        },
    },
)
@pytest.mark.parametrize(
    'locale,text,cost,cost_text',
    [
        ('ru', 'Добрый день!', 100, '100 руб.'),
        ('en', 'Hello!', 200, '200 dollars.'),
    ],
    ids=['ru', 'en'],
)
async def test_localization_locale_from_event(
        taxi_client_events, mongodb, locale, text, cost, cost_text,
):
    request_body = {
        'service': 'service',
        'channel': 'channel',
        'event': 'event',
        'locale': locale,
        'payload': {
            'text': {'key': 'hello_key', 'keyset': 'taximeter_messages'},
            'some_struct': {
                'some_key': 'some_value',
                'some_sub_struct': {
                    'is_not_the_key': 'hello_key',
                    'keyset': 'taximeter_messages',
                },
                'text': {
                    'key': 'key1',
                    'keyset': 'taximeter_messages',
                    'params': {'cost': cost},
                },
            },
            'some_array': [
                {'key': 'hello_key', 'keyset': 'taximeter_messages'},
                {
                    'is_not_the_key': 'hello_key',
                    'keyset': 'taximeter_messages',
                },
                {'key': 'hello_key', 'keyset': 'taximeter_messages'},
            ],
        },
    }
    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 200

    events = list(mongodb.client_events_events.find({}))
    assert len(events) == 1
    assert 'payload' in events[0]

    event_payload = json.loads(events[0]['payload'])
    assert event_payload == {
        'text': text,
        'some_struct': {
            'some_key': 'some_value',
            'some_sub_struct': {
                'is_not_the_key': 'hello_key',
                'keyset': 'taximeter_messages',
            },
            'text': cost_text,
        },
        'some_array': [
            text,
            {'is_not_the_key': 'hello_key', 'keyset': 'taximeter_messages'},
            text,
        ],
    }


@helpers.TRANSLATIONS
@pytest.mark.config(
    CLIENT_EVENTS_SERVICES={
        '__default__': {
            'polling_delay': 30,
            'localization': {'default_locale': 'en'},
            'events': {
                '__default__': {'notification': {'enabled': True}, 'ttl': 600},
            },
        },
    },
)
async def test_localization_locale_from_service(taxi_client_events, mongodb):
    request_body = {
        'service': 'service',
        'channel': 'channel',
        'event': 'event',
        'payload': {
            'text': {'key': 'hello_key', 'keyset': 'taximeter_messages'},
        },
    }
    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 200

    events = list(mongodb.client_events_events.find({}))
    assert len(events) == 1
    assert 'payload' in events[0]

    event_payload = json.loads(events[0]['payload'])
    assert event_payload == {'text': 'Hello!'}


@helpers.TRANSLATIONS
@pytest.mark.config(
    CLIENT_EVENTS_SERVICES={
        '__default__': {
            'polling_delay': 30,
            'localization': {'default_locale': 'ru'},
            'events': {
                '__default__': {'notification': {'enabled': True}, 'ttl': 600},
            },
        },
    },
)
async def test_localization_locale_overwrite(taxi_client_events, mongodb):
    request_body = {
        'service': 'service',
        'channel': 'channel',
        'event': 'event',
        'locale': 'en',
        'payload': {
            'text': {'key': 'hello_key', 'keyset': 'taximeter_messages'},
        },
    }
    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 200

    events = list(mongodb.client_events_events.find({}))
    assert len(events) == 1
    assert 'payload' in events[0]

    event_payload = json.loads(events[0]['payload'])
    assert event_payload == {'text': 'Hello!'}


@helpers.TRANSLATIONS
@pytest.mark.config(
    CLIENT_EVENTS_SERVICES={
        '__default__': {
            'polling_delay': 30,
            'events': {
                '__default__': {'notification': {'enabled': True}, 'ttl': 600},
            },
        },
    },
)
async def test_localization_locale_not_found(taxi_client_events, mongodb):
    request_body = {
        'service': 'service',
        'channel': 'channel',
        'event': 'event',
        'payload': {
            'text': {'key': 'hello_key', 'keyset': 'taximeter_messages'},
        },
    }
    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 400
