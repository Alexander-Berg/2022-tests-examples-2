import pytest

import tests_client_events.pull_helpers as helpers


async def test_sample(taxi_client_events, push_events):
    await push_events(
        [
            {
                'service': 'service',
                'channel': 'channel_1',
                'event': 'event_1',
                'event_id': 'event_id',
                'payload': {'some': 'data'},
            },
            {'service': 'service', 'channel': 'channel_2', 'event': 'event_2'},
        ],
    )

    pull_request_body = {
        'service': 'service',
        'channels': ['channel_1', 'channel_2'],
        'events': [],
    }

    response = await taxi_client_events.post('pull', json=pull_request_body)
    assert response.status_code == 200

    assert helpers.prepare_response(response.json()) == {
        'polling_delay': 30,
        'events': {
            'updated': [
                {
                    'event': 'event_1',
                    'event_id': 'event_id',
                    'payload': {'some': 'data'},
                },
                {'event': 'event_2'},
            ],
            'expired': [],
        },
    }


async def test_expired(taxi_client_events, push_events):
    await push_events(
        [{'service': 'service', 'channel': 'channel_1', 'event': 'event_1'}],
    )

    pull_request_body = {
        'service': 'service',
        'channels': ['channel_1', 'channel_2'],
        'events': [
            {'event': 'event_2', 'version': '0.0'},
            {'event': 'event_3', 'event_id': 'event_id', 'version': '0.0'},
        ],
    }

    response = await taxi_client_events.post('pull', json=pull_request_body)
    assert response.status_code == 200

    assert helpers.prepare_response(response.json()) == {
        'polling_delay': 30,
        'events': {
            'updated': [{'event': 'event_1'}],
            'expired': [
                {'event': 'event_2'},
                {'event': 'event_3', 'event_id': 'event_id'},
            ],
        },
    }


async def test_updated(taxi_client_events, push_events):
    await push_events(
        [
            {'service': 'service', 'channel': 'channel_1', 'event': 'event_1'},
            {'service': 'service', 'channel': 'channel_1', 'event': 'event_2'},
            {
                'service': 'service',
                'channel': 'channel_2',
                'event': 'event_2',
                'event_id': 'event_id',
            },
        ],
    )

    pull_request_body = {
        'service': 'service',
        'channels': ['channel_1', 'channel_2'],
        'events': [
            {'event': 'event_1', 'version': '0.0'},
            {'event': 'event_2', 'version': '9.0'},
            {'event': 'event_2', 'event_id': 'event_id', 'version': '0.0'},
        ],
    }

    response = await taxi_client_events.post('pull', json=pull_request_body)
    assert response.status_code == 200

    assert helpers.prepare_response(response.json()) == {
        'polling_delay': 30,
        'events': {
            'updated': [
                {'event': 'event_1'},
                {'event': 'event_2', 'event_id': 'event_id'},
            ],
            'expired': [],
        },
    }


async def test_no_version(taxi_client_events, push_events):
    await push_events(
        [{'service': 'service', 'channel': 'channel_1', 'event': 'event_1'}],
    )

    pull_request_body = {
        'service': 'service',
        'channels': ['channel_1'],
        'events': [{'event': 'event_1'}, {'event': 'event_2'}],
    }

    response = await taxi_client_events.post('pull', json=pull_request_body)
    assert response.status_code == 200

    assert helpers.prepare_response(response.json()) == {
        'polling_delay': 30,
        'events': {'updated': [], 'expired': []},
    }


@pytest.mark.parametrize('is_master,probability', [(True, 100), (False, 0)])
async def test_read_from_master(
        taxi_client_events,
        push_events,
        testpoint,
        taxi_config,
        is_master,
        probability,
):
    await push_events(
        [
            {
                'service': 'service',
                'channel': 'channel_1',
                'event': 'event_1',
                'event_id': 'event_id',
                'payload': {'some': 'data'},
            },
        ],
    )

    pull_request_body = {
        'service': 'service',
        'channels': ['channel_1'],
        'events': [],
    }

    @testpoint('is_mongo_read_preference_master')
    def _is_mongo_read_preference_master(value):
        assert value == is_master

    taxi_config.set_values(
        {
            'CLIENT_EVENTS_MONGO_SETTINGS': {
                'master_read_probability': probability,
            },
        },
    )
    await taxi_client_events.invalidate_caches()

    await taxi_client_events.post('pull', json=pull_request_body)
