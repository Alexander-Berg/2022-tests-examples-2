import json
import math

from dateutil import parser
import pytest
import pytz


# this test is written for identification stub function
# it shall be rewritten
@pytest.mark.parametrize('add_frame', [True, False])
@pytest.mark.config(
    CCTV_WORKERS_IDENTIFICATION_THRESHOLD={
        'assume_similar': 1e-6,
        'assume_different': 1e-6,
    },
)
async def test_insert(taxi_cctv_workers, testpoint, mocked_time, add_frame):
    @testpoint('logbroker_publish')
    def _commit(msg):
        assert msg['name'] == 'identification-events-publisher'
        data = json.loads(msg['data'])
        event = data['event']
        time_expected = parser.parse(
            '2022-05-06T12:58:20.844113+00:00',
        ).astimezone(pytz.UTC)
        time_received = parser.parse(data['timestamp']).astimezone(pytz.UTC)
        assert time_received == time_expected
        assert event['processor_id'] == 'proc1'
        assert event['camera_id'] == 'camera1'
        assert event['detected_object'] == 'AbcTgJ'
        assert event['box'] == {'x': 1.2, 'y': 255.2, 'w': 34.5, 'h': 12.1}
        assert math.fabs(0.0 - event['distance']) <= 1e-6
        assert event['event_timestamp_ms'] == 12345778
        assert event['is_permanent_index']
        if add_frame:
            assert event['frame'] == 'AbcTgJ'
        else:
            assert 'frame' not in event
        assert event['person_id'] == 'person1'

    now = parser.parse('2022-05-06T15:58:20.844113+03:00').astimezone(pytz.UTC)
    mocked_time.set(now)

    message = {
        'consumer': 'events-consumer',
        'topic': '/taxi/cctv/testing/events',
        'cookie': 'cookie0',
    }
    data_json = {
        'timestamp': '2022-05-06T15:57:20.844113+03:00',
        'event': {
            'processor_id': 'proc1',
            'model_id': 'model1',
            'camera_id': 'camera1',
            'event_timestamp_ms': 12345778,
            'detected_object': 'AbcTgJ',
            'signature': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            'confidence': 0.45,
            'box': {'x': 1.2, 'y': 255.2, 'w': 34.5, 'h': 12.1},
        },
    }
    if add_frame:
        data_json['event']['frame'] = 'AbcTgJ'
    data = json.dumps(data_json)
    message['data'] = data
    response = await taxi_cctv_workers.post(
        'tests/logbroker/messages', data=json.dumps(message),
    )
    assert response.status_code == 200

    await _commit.wait_call()
