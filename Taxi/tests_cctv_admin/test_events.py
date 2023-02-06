# pylint: disable=import-only-modules, consider-using-enumerate
import json

import pytest

import tests_cctv_admin.utils as utils

CAMERA = {'_id': 'camera_01'}

PROCESSOR = {
    '_id': 'processor1',
    'cameras': ['camera_01'],
    'hostname': 'processor.one.com',
    'updated_ts': utils.date_to_ms(
        utils.parse_date_str('2022-04-07 01:01:06.0+00'),
    ),
}

mapping = {
    '11111111111111111111111111111111': 'person_1@yandex-team.ru',
    '22222222222222222222222222222222': 'person_2@yandex-team.ru',
    '33333333333333333333333333333333': 'person_3@yandex-team.ru',
    '44444444444444444444444444444444': '@yandex-team.ru',
}

unregistered = ['gen_id0', 'gen_id1']

tags = {
    '11111111111111111111111111111111': [{'id': 1}, {'id': 2}],
    '33333333333333333333333333333333': [{'id': 3}],
    'gen_id0': [{'id': 2}],
}


@pytest.fixture(name='personal', autouse=True)
def personal_service(mockserver):
    @mockserver.json_handler('/personal/v1/yandex_logins/bulk_retrieve')
    def retrieve_handler(request):
        data = request.json
        assert data is not None
        ids = data['items']
        results = []
        for id in ids:
            if id['id'] in mapping:
                results.append({'id': id['id'], 'value': mapping[id['id']]})
        response = {'items': results}
        return mockserver.make_response(json.dumps(response), status=200)


@pytest.fixture(name='cctv-workers', autouse=True)
def cctv_workers_service(mockserver):
    @mockserver.json_handler('/cctv-workers/v1/person/tags')
    def tags_handler(request):
        data = request.json
        assert data is not None
        ids = data['person_ids']
        tag_info = []
        for id in ids:
            if id in tags:
                tag_info.append({'person_id': id, 'tags': tags[id]})
            else:
                tag_info.append({'person_id': id, 'tags': []})
        response = {'tag_info': tag_info}
        return mockserver.make_response(json.dumps(response), status=200)


def _generate_events(events_count, begin_date_str):
    persons = [
        '11111111111111111111111111111111',
        '22222222222222222222222222222222',
        '33333333333333333333333333333333',
        '44444444444444444444444444444444',
        '55555555555555555555555555555555',
        'gen_id0',
        'gen_id1',
    ]
    persons_count = len(persons)

    event_ts = utils.date_to_ms(begin_date_str)
    events = []
    for i in range(0, events_count):
        remainder = i % persons_count
        event = {
            'processor_id': 'processor1',
            'camera_id': 'camera1',
            'box': {'x': 1.2, 'y': 255.2, 'w': 34.5, 'h': 12.1},
            'distance': 1.1,
            'event_timestamp_ms': event_ts,
            'detected_object': 'AbcTgJ',
            'is_permanent_index': True,
            'person_id': persons[remainder],
        }
        if remainder == 5 or remainder == 6:
            event['is_permanent_index'] = False
        events.append(event)
        event_ts += 1000
    return events


async def _upsert_events(taxi_cctv_admin, testpoint, events):
    reset_aggregator = True

    @testpoint('identification_event_storage_tp')
    def _tune_storage(data):
        nonlocal reset_aggregator
        result = {'reset_aggregator': reset_aggregator}
        reset_aggregator = False
        return result

    @testpoint('identification_event_store_to_storage_tp')
    def _store_to_persistence(data):
        pass

    await taxi_cctv_admin.enable_testpoints()
    _store_to_persistence.flush()

    for event in events:
        await taxi_cctv_admin.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'identification-event-consumer',
                    'data': json.dumps(
                        {
                            'timestamp': '2022-04-07 01:01:07.0+00',
                            'event': event,
                        },
                    ),
                    'topic': '/taxi/cctv/testing/identification-events',
                    'cookie': 'cookie',
                },
            ),
        )
    await _store_to_persistence.wait_call()


def _create_video_url(generated_event):
    event_ts = utils.date_from_ms(generated_event['event_timestamp_ms'])
    return 'https://{}/media/{}/{}'.format(
        PROCESSOR['hostname'],
        generated_event['camera_id'],
        event_ts.strftime('%Y-%m-%d_%H%%3A%M%%3A00.mp4'),
    )


def _check_equal(handle, generated):
    assert len(handle) == len(generated)
    for i in range(0, len(handle)):
        hevent = handle[i]
        gevent = generated[i]
        assert hevent['timestamp'] == gevent['event_timestamp_ms'] // 1000
        assert hevent['person_id'] == gevent['person_id']
        assert hevent['processor_id'] == gevent['processor_id']
        assert hevent['camera_id'] == gevent['camera_id']
        assert hevent['confidence'] == gevent['distance']
        assert hevent['detected_object'] == gevent['detected_object']
        assert hevent['alerts'] == gevent['alerts']
        assert hevent['video_url'] == _create_video_url(gevent)


async def test_intervals(taxi_cctv_admin, mongodb, mocked_time):
    mocked_time.set(utils.parse_date_str('2022-04-07 01:01:07.0+00'))
    await taxi_cctv_admin.invalidate_caches(clean_update=True)

    request_body = {'interval': {'duration': 3600}}
    response = await taxi_cctv_admin.post('/v1/events', json=request_body)
    assert response.status_code == 200

    # too long response
    request_body = {'interval': {'duration': 3601}}
    response = await taxi_cctv_admin.post('/v1/events', json=request_body)
    assert response.status_code == 413

    # interval is out of range - 'from' is from the future
    from_request = utils.parse_date_str('2022-04-07 01:01:08.0+00').timestamp()
    to_request = utils.parse_date_str('2022-04-07 01:01:09.0+00').timestamp()
    request_body = {
        'interval': {'from': int(from_request), 'to': int(to_request)},
    }
    response = await taxi_cctv_admin.post('/v1/events', json=request_body)
    assert response.status_code == 400

    # invalid interval - 'to' is earlier than 'from'
    from_request = utils.parse_date_str('2022-04-07 01:01:05.0+00').timestamp()
    to_request = utils.parse_date_str('2022-04-07 01:01:04.0+00').timestamp()
    request_body = {
        'interval': {'from': int(from_request), 'to': int(to_request)},
    }
    response = await taxi_cctv_admin.post('/v1/events', json=request_body)
    assert response.status_code == 400

    # invalid interval - 'to' is out of history bounds
    from_request = utils.parse_date_str('2022-04-07 00:00:02.0+00').timestamp()
    to_request = utils.parse_date_str('2022-04-07 00:00:04.0+00').timestamp()
    request_body = {
        'interval': {'from': int(from_request), 'to': int(to_request)},
    }
    response = await taxi_cctv_admin.post('/v1/events', json=request_body)
    assert response.status_code == 400


@pytest.mark.config(
    CCTV_WORKERS_CLIENT_QOS={
        '__default__': {'attempts': 2, 'timeout-ms': 5000},
    },
)
@pytest.mark.parametrize('personal_use', [True, False])
async def test_events(
        taxi_cctv_admin,
        mongodb,
        mocked_time,
        testpoint,
        personal,
        personal_use,
        taxi_config,
):
    taxi_config.set_values({'CCTV_ADMIN_USE_PERSONAL': personal_use})
    suffix_len = len('@yandex-team.ru')

    mongodb.cctv_event_history.remove({})
    mongodb.cctv_cameras.insert(CAMERA)
    mongodb.cctv_processors.insert(PROCESSOR)

    mocked_time.set(utils.parse_date_str('2022-04-07 01:02:07.0+00'))
    await taxi_cctv_admin.invalidate_caches(clean_update=True)

    generated_events = _generate_events(
        3600, utils.parse_date_str('2022-04-07 00:02:07.0+00'),
    )
    await _upsert_events(taxi_cctv_admin, testpoint, generated_events)
    generated_events.reverse()
    for event in generated_events:
        person_id = event['person_id']
        if person_id in tags:
            event['alerts'] = []
            tag_list = tags[person_id]
            for item in tag_list:
                tag_id = item['id']
                event['alerts'].append(f'tag_{tag_id}')
        else:
            event['alerts'] = []
    if personal_use:
        for event in generated_events:
            if event['person_id'] in mapping:
                login_without_suffix = mapping[event['person_id']][
                    0:-suffix_len
                ]
                if login_without_suffix == '':
                    event['person_id'] = 'UNKNOWN'
                else:
                    event['person_id'] = login_without_suffix
            elif event['person_id'] in unregistered:
                pass
            else:
                event['person_id'] = 'UNKNOWN'

    request_body = {'interval': {'duration': 3600}}
    response = await taxi_cctv_admin.post('/v1/events', json=request_body)
    assert response.status_code == 200
    history_acquired = response.json()['events']

    _check_equal(history_acquired, generated_events)

    full_history_0 = history_acquired

    request_body = {'interval': {'duration': (3600 - 120)}}
    response = await taxi_cctv_admin.post('/v1/events', json=request_body)
    assert response.status_code == 200
    part_of_history_0 = response.json()['events']

    assert part_of_history_0
    assert part_of_history_0[0] == full_history_0[0]

    mocked_time.set(utils.parse_date_str('2022-04-07 01:04:07.0+00'))
    await taxi_cctv_admin.invalidate_caches(clean_update=False)

    from_request = part_of_history_0[-1]['timestamp']
    to_request = part_of_history_0[0]['timestamp']
    request_body = {
        'interval': {'from': int(from_request), 'to': int(to_request)},
    }
    response = await taxi_cctv_admin.post('/v1/events', json=request_body)
    assert response.status_code == 200
    part_of_history_1 = response.json()['events']

    assert part_of_history_1
    assert part_of_history_0[-1] == part_of_history_1[-1]
    assert part_of_history_0[0] == part_of_history_1[0]
