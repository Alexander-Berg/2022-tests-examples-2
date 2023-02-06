import copy
import json

import pytest

ENDPOINT = '/drivematics/signalq-drivematics-api/v1/events/retrieve'

EVENT1 = {
    'id': 'event1',
    'at': '2022-01-19T13:50:00+00:00',
    'type': 'type1',
    'gnss': {
        'lat': 99.0,
        'lon': 199.0,
        'speed_kmph': 4.4,
        'accuracy_m': 3.3,
        'direction_deg': 5.5,
    },
    'position_updated_at': '2022-01-19T13:50:00+00:00',
    's3_video_path': 'vp1',
    's3_external_video_path': 'evp1',
    's3_photo_path': 'pp1',
    's3_external_photo_path': 'epp1',
    'extra': 'extra',
    'signalled': False,
}

EVENT2 = {
    'id': 'event2',
    'at': '2022-01-19T13:50:00+00:00',
    'type': 'type2',
    'gnss': {
        'lat': 99.0,
        'lon': 199.0,
        'speed_kmph': 4.4,
        'accuracy_m': 3.3,
        'direction_deg': 5.5,
    },
    'position_updated_at': '2022-01-19T13:50:00+00:00',
    's3_video_path': 'vp2',
    's3_external_video_path': 'evp2',
    's3_photo_path': 'pp2',
    's3_external_photo_path': 'epp2',
    'extra': 'extra',
    'signalled': False,
    'some_new_field': 'coop',
}

EVENT2_WITHOUT_UNUSED = copy.deepcopy(EVENT2)
EVENT2_WITHOUT_UNUSED.pop('some_new_field')

# Отсутствуют required поля
EVENT3_BAD = {
    'id': 'event3',
    'at': '2022-01-19T13:50:00+00:00',
    'gnss': {
        'lat': 99.0,
        'lon': 199.0,
        'speed_kmph': 4.4,
        'accuracy_m': 3.3,
        'direction_deg': 5.5,
    },
    'position_updated_at': '2022-01-19T13:50:00+00:00',
    's3_video_path': 'vp3',
    's3_external_video_path': 'evp3',
    's3_photo_path': 'pp3',
    's3_external_photo_path': 'epp3',
    'extra': 'extra',
    'signalled': False,
}


@pytest.mark.redis_store(
    [
        'mset',
        {
            'DeviceLastEvent:sn1': json.dumps(EVENT1),
            'DeviceLastEvent:sn2': json.dumps(EVENT2),
            'DeviceLastEvent:sn_with_bad_event': json.dumps(EVENT3_BAD),
        },
    ],
)
@pytest.mark.parametrize(
    'serial_numbers, expected_code, expected_response',
    [
        (['sn1'], 200, {'items': [{'serial_number': 'sn1', 'event': EVENT1}]}),
        (
            ['sn1', 'sn2'],
            200,
            {
                'items': [
                    {'serial_number': 'sn1', 'event': EVENT1},
                    {'serial_number': 'sn2', 'event': EVENT2_WITHOUT_UNUSED},
                ],
            },
        ),
        (
            ['sn2'],
            200,
            {
                'items': [
                    {'serial_number': 'sn2', 'event': EVENT2_WITHOUT_UNUSED},
                ],
            },
        ),
        (
            ['sn1', 'sn2', 'sn3'],
            200,
            {
                'items': [
                    {'serial_number': 'sn1', 'event': EVENT1},
                    {'serial_number': 'sn2', 'event': EVENT2_WITHOUT_UNUSED},
                    {'serial_number': 'sn3'},
                ],
            },
        ),
        (['sn1', 'sn2', 'sn_with_bad_event'], 500, None),
    ],
)
async def test_drivematics_v1_events_retrieve(
        taxi_signalq_drivematics_api,
        serial_numbers,
        expected_code,
        expected_response,
):
    response = await taxi_signalq_drivematics_api.post(
        ENDPOINT, json={'serial_numbers': serial_numbers},
    )
    assert response.status_code == expected_code, response.text
    if expected_code == 500:
        return

    response_json = response.json()
    response_json['items'].sort(key=lambda x: x['serial_number'])
    expected_response['items'].sort(key=lambda x: x['serial_number'])
    assert response_json == expected_response
