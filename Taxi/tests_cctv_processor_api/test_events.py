import json

from dateutil import parser
import pytest
import pytz


@pytest.mark.parametrize(
    'req,expected',
    [
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'frame': 'AbcTgJ',
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            200,
            id='full request',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'frame': 'AbcTgJ',
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_2',
                        'model_id': 'model_1',
                        'detected_object': 'AbcTgJ',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            200,
            id='camera not found',
        ),
        pytest.param({'events': []}, 400, id='empty events'),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [],
                        'detected_object': 'AbcTgJ',
                        'frame': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'detected_object': 'AbcTgJ',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            200,
            id='empty signature',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'detected_object': 'AbcTgJ',
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'detected_object': 'AbcTgJ',
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='camera_id missing',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'detected_object': 'AbcTgJ',
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'timestamp_ms': 1620000000000,
                        'detected_object': 'AbcTgJ',
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='model_id missing',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='detected_object missing',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'detected_object': 'AbcTgJ',
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'detected_object': 'AbcTgJ',
                        'timestamp_ms': 1620000000000,
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='signature missing',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'detected_object': 'AbcTgJ',
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'detected_object': 'AbcTgJ',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='box missing',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'detected_object': 'AbcTgJ',
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'detected_object': 'AbcTgJ',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'box': {'x': 1.2, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='box malformed',
        ),
    ],
)
async def test_post_event_schema_validation(
        taxi_cctv_processor_api, mongodb, load_json, req, expected,
):

    mongodb.cctv_processors.remove({})
    initial_value = load_json('test_events.json')
    if initial_value:
        initial_value['ticket'] = initial_value['ticket'].encode('utf-8')
        mongodb.cctv_processors.insert(initial_value)

    response = await taxi_cctv_processor_api.post(
        '/v1/events',
        json=req,
        headers={
            'X-YaCctv-Processor-Ticket': 'cHJvY2Vzc29yX3RpY2tldA==',
            'X-YaCctv-Processor-ID': 'processor_01',
        },
    )
    assert response.status_code == expected
    # without processor_id
    response = await taxi_cctv_processor_api.post(
        '/v1/events',
        json=req,
        headers={'X-YaCctv-Processor-Ticket': 'cHJvY2Vzc29yX3RpY2tldA=='},
    )
    assert response.status_code == 400
    # without processor ticket
    response = await taxi_cctv_processor_api.post(
        '/v1/events',
        json=req,
        headers={'X-YaCctv-Processor-ID': 'processor_01'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'req,expected',
    [
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'detected_object': 'AbcTgJ',
                        'frame': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            403,
            id='full request - wrong ticket',
        ),
        pytest.param({'events': []}, 400, id='empty events'),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [],
                        'detected_object': 'AbcTgJ',
                        'frame': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            403,
            id='empty signature - wrong ticket',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='camera_id missing',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='model_id missing',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='signature missing',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'detected_object': 'AbcTgJ',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='box missing',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='detected_object missing',
        ),
        pytest.param(
            {
                'events': [
                    {
                        'camera_id': 'camera_5',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [1.2, 3.4, 5.6, 7.8],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                    {
                        'camera_id': 'camera_6',
                        'model_id': 'model_1',
                        'timestamp_ms': 1620000000000,
                        'signature': [9.0, 1.2, 3.4, 5.6],
                        'detected_object': 'AbcTgJ',
                        'box': {'x': 1.2, 'w': 5.6, 'h': 7.8},
                        'confidence': 0.86,
                    },
                ],
            },
            400,
            id='box malformed',
        ),
    ],
)
async def test_post_wrong_ticket(
        taxi_cctv_processor_api, mongodb, load_json, req, expected,
):
    mongodb.cctv_processors.remove({})
    initial_value = load_json('test_events.json')
    if initial_value:
        initial_value['ticket'] = initial_value['ticket'].encode('utf-8')
        mongodb.cctv_processors.insert(initial_value)
    response = await taxi_cctv_processor_api.post(
        '/v1/events',
        json=req,
        headers={
            'X-YaCctv-Processor-Ticket': 'ticket2',
            'X-YaCctv-Processor-ID': 'processor_01',
        },
    )
    assert response.status_code == expected


@pytest.mark.config(
    CCTV_PROCESSOR_CONFIG={
        'processor1': {
            'cameras': [
                {
                    'url': 'https://admin@password:localhost:8080',
                    'id': 'camera_5',
                },
                {
                    'url': 'https://admin@password:localhost2:8080',
                    'id': 'camera_6',
                },
            ],
            'event_sender': {},
            'storage': {},
            'updated_ts': 0,
            'ticket': 'ticket',
        },
    },
)
async def test_insert(
        taxi_cctv_processor_api, mongodb, load_json, testpoint, mocked_time,
):
    req = {
        'events': [
            {
                'camera_id': 'camera_5',
                'model_id': 'model_1',
                'timestamp_ms': 1620000000000,
                'signature': [1.2, 3.4, 5.6, 7.8],
                'frame': 'AbcTgJ',
                'detected_object': 'AbcTgJ',
                'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                'confidence': 0.86,
            },
            {
                'camera_id': 'camera_5',
                'model_id': 'model_1',
                'timestamp_ms': 1620000000000,
                'signature': [1.2, 3.4, 5.6, 7.8],
                'detected_object': 'AbcTgJ',
                'box': {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8},
                'confidence': 0.96,
            },
        ],
    }

    mongodb.cctv_processors.remove({})
    initial_value = load_json('test_events.json')
    if initial_value:
        initial_value['ticket'] = initial_value['ticket'].encode('utf-8')
        mongodb.cctv_processors.insert(initial_value)

    @testpoint('logbroker_publish')
    def _commit(msg):
        assert msg['name'] == 'detection-event-publisher'
        data = json.loads(msg['data'])
        event = data['event']
        time_expected = parser.parse(
            '2022-05-06T12:58:20.844113+00:00',
        ).astimezone(pytz.UTC)
        time_received = parser.parse(data['timestamp']).astimezone(pytz.UTC)
        assert time_received == time_expected
        assert event['processor_id'] == 'processor_01'
        assert event['camera_id'] == 'camera_5'
        assert event['model_id'] == 'model_1'
        assert event['detected_object'] == 'AbcTgJ'

        assert event['signature'] == [1.2, 3.4, 5.6, 7.8]
        assert event['box'] == {'x': 1.2, 'y': 3.4, 'w': 5.6, 'h': 7.8}
        assert event['event_timestamp_ms'] == 1620000000000
        if event['confidence'] == 0.86:
            assert event['frame'] == 'AbcTgJ'
        elif event['confidence'] == 0.96:
            assert 'frame' not in event
        else:
            assert False

    now = parser.parse('2022-05-06T15:58:20.844113+03:00').astimezone(pytz.UTC)
    mocked_time.set(now)

    response = await taxi_cctv_processor_api.post(
        '/v1/events',
        json=req,
        headers={
            'X-YaCctv-Processor-Ticket': 'cHJvY2Vzc29yX3RpY2tldA==',
            'X-YaCctv-Processor-ID': 'processor_01',
        },
    )
    assert response.status_code == 200

    await _commit.wait_call()
