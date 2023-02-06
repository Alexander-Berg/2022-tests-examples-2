import json
import math

import pytest


def _cmp_event(event, expected):
    assert event['processor_id'] == expected['processor_id']
    assert event['camera_id'] == expected['camera_id']
    assert event['box'] == expected['box']
    assert event['event_timestamp_ms'] == expected['event_timestamp_ms']
    assert event['person_id'] == expected['person_id']
    assert event['is_permanent_index'] == expected['is_permanent_index']
    assert math.fabs(expected['distance'] - event['distance']) <= 3e-7
    assert event['detected_object'] == expected['detected_object']
    if 'frame' in event:
        assert 'frame' in expected
        assert event['frame'] == expected['frame']
    else:
        assert 'frame' not in expected


def _make_id(event):
    return (event['person_id'], event['camera_id'], event['processor_id'])


@pytest.fixture
def _identification_event_storage():
    class IdentificationEventStorage:
        def __init__(self):
            self._storage = dict()

        def insert(self, event):
            event_gr_id = _make_id(event)
            events = self._storage.get(event_gr_id)
            if not events:
                self._storage[event_gr_id] = [event]
                return
            events.append(event)

        def get_all(self):
            return self._storage

        def clean(self):
            self._storage = dict()

    return IdentificationEventStorage()


async def test_consumer_basic(taxi_cctv_admin, testpoint):
    reset_aggregator = True

    @testpoint('identification_event_storage_tp')
    def _tune_storage(data):
        nonlocal reset_aggregator
        result = {'reset_aggregator': reset_aggregator}
        reset_aggregator = False
        return result

    @testpoint('logbroker_commit')
    def _commit(cookie):
        assert cookie == 'cookie'

    @testpoint('identification_event_raw_message_tp')
    def _raw_message_getter(data):
        pass

    await taxi_cctv_admin.enable_testpoints()
    _raw_message_getter.flush()
    _commit.flush()

    messages = ['message1', 'message2']
    messages.sort()

    msg_count = len(messages)
    for idx in range(0, msg_count):
        response = await taxi_cctv_admin.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'identification-event-consumer',
                    'data': messages[idx],
                    'topic': '/taxi/cctv/testing/identification-events',
                    'cookie': 'cookie',
                },
            ),
        )
        assert response.status_code == 200
        await _commit.wait_call()

    result_messages = []
    for idx in range(0, len(messages)):
        result = await _raw_message_getter.wait_call()
        result_messages.append(result['data']['message'])
    result_messages.sort()

    assert result_messages == messages


async def test_upsert(
        taxi_cctv_admin, testpoint, _identification_event_storage,
):
    input_event1 = {
        'timestamp': '2022-05-06T15:57:20.844113+03:00',
        'event': {
            'processor_id': 'processor1',
            'camera_id': 'camera1',
            'box': {'x': 1.2, 'y': 255.2, 'w': 34.5, 'h': 12.1},
            'distance': 1.1,
            'event_timestamp_ms': 12345778,
            'detected_object': 'AbcTgJ',
            'frame': 'AbcTgJ',
            'is_permanent_index': True,
            'person_id': 'person_1',
        },
    }
    reset_aggregator = True

    @testpoint('identification_event_storage_tp')
    def _tune_storage(data):
        nonlocal reset_aggregator
        result = {'reset_aggregator': reset_aggregator}
        reset_aggregator = False
        return result

    @testpoint('logbroker_commit')
    def _commit(cookie):
        assert cookie == 'cookie'

    @testpoint('identification_event_raw_message_tp')
    def _raw_message_getter(data):
        pass

    @testpoint('identification_event_store_to_storage_tp')
    def _store_to_persistence(data):
        _identification_event_storage.insert(data)

    async def _expect_all():
        await _raw_message_getter.wait_call()
        await _store_to_persistence.wait_call()
        await _commit.wait_call()

    def _flush_all_tps():
        _commit.flush()
        _raw_message_getter.flush()
        _store_to_persistence.flush()

    await taxi_cctv_admin.enable_testpoints()
    _flush_all_tps()

    _identification_event_storage.clean()

    await taxi_cctv_admin.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'identification-event-consumer',
                'data': json.dumps(input_event1),
                'topic': '/taxi/cctv/testing/identification-events',
                'cookie': 'cookie',
            },
        ),
    )
    await _expect_all()
    items = _identification_event_storage.get_all()
    assert items
    event_gr_id_1 = _make_id(input_event1['event'])
    _cmp_event(items[event_gr_id_1][0], input_event1['event'])


async def test_double_upsert(
        taxi_cctv_admin, testpoint, _identification_event_storage,
):
    reset_aggregator = True

    @testpoint('identification_event_storage_tp')
    def _tune_storage(data):
        nonlocal reset_aggregator
        result = {'reset_aggregator': reset_aggregator}
        reset_aggregator = False
        return result

    input_event1 = {
        'timestamp': '2022-05-06T15:57:20.844113+03:00',
        'event': {
            'processor_id': 'processor1',
            'camera_id': 'camera1',
            'box': {'x': 1.2, 'y': 255.2, 'w': 34.5, 'h': 12.1},
            'distance': 1.1,
            'event_timestamp_ms': 12345778,
            'detected_object': 'AbcTgJ',
            'frame': 'AbcTgJ',
            'is_permanent_index': True,
            'person_id': 'person_1',
        },
    }
    input_event2 = {
        'timestamp': '2022-05-06T15:57:20.844113+03:00',
        'event': {
            'processor_id': 'processor1',
            'camera_id': 'camera1',
            'box': {'x': 1.2, 'y': 255.2, 'w': 34.5, 'h': 12.1},
            'distance': 1.1,
            'event_timestamp_ms': 12345778,
            'detected_object': 'AbcTgJ',
            'is_permanent_index': True,
            'person_id': 'afasffafb',
        },
    }

    @testpoint('logbroker_commit')
    def _commit(cookie):
        assert cookie == 'cookie'

    @testpoint('identification_event_raw_message_tp')
    def _raw_message_getter(data):
        pass

    @testpoint('identification_event_store_to_storage_tp')
    def _store_to_persistence(data):
        _identification_event_storage.insert(data)

    async def _expect_all():
        await _raw_message_getter.wait_call()
        await _store_to_persistence.wait_call()
        await _commit.wait_call()

    def _flush_all_tps():
        _commit.flush()
        _raw_message_getter.flush()
        _store_to_persistence.flush()

    await taxi_cctv_admin.enable_testpoints()
    _flush_all_tps()

    _identification_event_storage.clean()

    await taxi_cctv_admin.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'identification-event-consumer',
                'data': '{}\n{}'.format(
                    json.dumps(input_event1), json.dumps(input_event2),
                ),
                'topic': '/taxi/cctv/testing/identification-events',
                'cookie': 'cookie',
            },
        ),
    )
    await _expect_all()

    items = _identification_event_storage.get_all()
    assert items
    event_gr_id_1 = _make_id(input_event1['event'])
    event_gr_id_2 = _make_id(input_event2['event'])
    _cmp_event(items[event_gr_id_1][0], input_event1['event'])
    _cmp_event(items[event_gr_id_2][0], input_event2['event'])
