import json
import math

import pytest

import tests_cctv_workers.pgsql_helpers as pgsql_helpers


async def test_message(taxi_cctv_workers, testpoint):
    expected_event_count = 0

    @testpoint('process-events')
    def count_events(data):
        assert data['processed_events_count'] == expected_event_count

    message_count = 10
    for i in range(message_count):
        expected_event_count = i + 1
        message = {
            'consumer': 'events-consumer',
            'topic': '/taxi/cctv/testing/events',
            'cookie': 'cookie{}'.format(i),
        }
        data = json.dumps(
            {
                'timestamp': '2022-05-06T15:57:20.844113+03:00',
                'event': {
                    'processor_id': 'proc1',
                    'model_id': 'model1',
                    'camera_id': 'camera1',
                    'detected_object': 'AbcTgJ',
                    'event_timestamp_ms': 12345778,
                    'signature': [1.2, 3.4, 5.6],
                    'confidence': 0.45,
                    'box': {'x': 1.2, 'y': 255.2, 'w': 34.5, 'h': 12.1},
                },
            },
        )
        message['data'] = '{}'.format(data) + '\n{}'.format(data) * i
        response = await taxi_cctv_workers.post(
            'tests/logbroker/messages', data=json.dumps(message),
        )
        assert response.status_code == 200
        await count_events.wait_call()


@pytest.mark.config(
    CCTV_WORKERS_IDENTIFICATION_THRESHOLD={
        'assume_similar': 1e-6,
        'assume_different': 2.0,
    },
)
async def test_identify_without_guests(
        taxi_cctv_workers, testpoint, load_json, pgsql,
):
    test_cases = load_json('test_identify_without_guests.json')

    # clean database with signatures and corresponding indexes
    pgsql_helpers.clear_face_signatures_table(pgsql)
    await taxi_cctv_workers.invalidate_caches(
        clean_update=True,
        cache_names=['guest-fast-search-index', 'guest-fast-append-index'],
    )

    expected_person = None
    expected_is_permanent = None

    @testpoint('identification-events')
    def identify_person(data):
        assert data['person'] == expected_person
        assert data['is_permanent'] == expected_is_permanent
        if expected_is_permanent:
            assert math.fabs(0.0 - data['distance']) < 1e-6

    for test_case in test_cases:
        expected_person = test_case['expected_person']
        expected_is_permanent = test_case['expected_is_permanent']
        data = json.dumps(
            {'timestamp': test_case['timestamp'], 'event': test_case['event']},
        )
        message = {
            'consumer': 'events-consumer',
            'topic': '/taxi/cctv/testing/events',
            'cookie': 'cookie',
        }
        message['data'] = '{}\n'.format(data)
        response = await taxi_cctv_workers.post(
            'tests/logbroker/messages', data=json.dumps(message),
        )
        assert response.status_code == 200
        await identify_person.wait_call()


@pytest.mark.config(
    CCTV_WORKERS_IDENTIFICATION_THRESHOLD={
        'assume_similar': 1e-6,
        'assume_different': 1e-6,
    },
)
async def test_identify_with_guests(
        taxi_cctv_workers, testpoint, load_json, pgsql,
):
    test_cases = load_json('test_identify_with_guests.json')

    # clean database with signatures and corresponding indexes
    pgsql_helpers.clear_face_signatures_table(pgsql)
    await taxi_cctv_workers.invalidate_caches(
        clean_update=True,
        cache_names=['guest-fast-search-index', 'guest-fast-append-index'],
    )

    expected_person = None
    expected_is_permanent = None

    @testpoint('identification-events')
    def identify_person(data):
        assert data['person'] == expected_person
        assert data['is_permanent'] == expected_is_permanent
        assert math.fabs(0.0 - data['distance']) < 1e-6
        if not expected_is_permanent:
            signatures = pgsql_helpers.get_face_signatures(pgsql)
            assert int(data['person']) in signatures

    for test_case in test_cases:
        expected_person = test_case['expected_person']
        expected_is_permanent = test_case['expected_is_permanent']
        data = json.dumps(
            {'timestamp': test_case['timestamp'], 'event': test_case['event']},
        )
        message = {
            'consumer': 'events-consumer',
            'topic': '/taxi/cctv/testing/events',
            'cookie': 'cookie',
        }
        message['data'] = '{}\n'.format(data)
        response = await taxi_cctv_workers.post(
            'tests/logbroker/messages', data=json.dumps(message),
        )
        assert response.status_code == 200
        await identify_person.wait_call()
