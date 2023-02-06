import copy
import json
import typing

import pytest

ENDPOINT = '/drivematics/signalq-drivematics-api/v1/statuses/retrieve'

STATUS1 = {
    'status_at': '2022-01-19T13:50:00+00:00',
    'cpu_temperature': 66,
    'disk_bytes_free_space': 100929567296,
    'disk_bytes_total_space': 100929567297,
    'root_bytes_free_space': 100929567290,
    'root_bytes_total_space': 100929567291,
    'ram_bytes_free_space': 578150656,
    'software_version': '1.1-1',
    'uptime_ms': 12638176,
    'position_updated_at': '2021-11-21T12:44:22+00:00',
    'sim_iccid': '00310410106543789301',
    'sim_imsi': '987654321000',
    'sim_phone_number': '+7 (955) 123-45-67',
    'upload_queue': {'photo': 2, 'video': 1, 'log': 4, 'event': 44},
    'gnss': {
        'lat': 99,
        'lon': 199,
        'speed_kmph': 4.4,
        'accuracy_m': 3.3,
        'direction_deg': 5.5,
    },
    'gps_position': {'lat': 89, 'lon': 44},
    'states': {
        'dms.xxx': {'some': 'thing', 'more': {}},
        'dms.yyy': 2,
        'some.sxs': True,
        'some.ggg': 4.22,
    },
}

STATUS2 = {
    'status_at': '2022-01-10T13:50:00+00:00',
    'cpu_temperature': 669,
    'disk_bytes_free_space': 100929567296,
    'disk_bytes_total_space': 100929567297,
    'root_bytes_free_space': 100929567290,
    'root_bytes_total_space': 100929567291,
    'ram_bytes_free_space': 578150656,
    'software_version': '1.2-1',
    'uptime_ms': 21258176,
    'position_updated_at': '2021-11-21T12:44:22+00:00',
    'sim_phone_number': '+7 (999) 123-45-67',
    'gnss': {},
    'gps_position': {'lat': 89, 'lon': 44},
    'states': {
        'dms.xxx': {'some': 'thing', 'more': {}},
        'dms.yyy': 2,
        'some.sxs': True,
        'some.ggg': 4.22,
    },
    'some_new_field': {'s1': 'ss'},
}

STATUS2_WITHOUT_UNUSED = copy.deepcopy(STATUS2)
STATUS2_WITHOUT_UNUSED.pop('some_new_field')

# Отсутствуют required поля
STATUS3_BAD = {
    'status_at': '2022-01-10T13:50:00+00:00',
    'cpu_temperature': 669,
    'disk_bytes_free_space': 100929567296,
    'disk_bytes_total_space': 100929567297,
    'ram_bytes_free_space': 578150656,
    'software_version': '1.2-1',
    'uptime_ms': 21258176,
    'position_updated_at': '2021-11-21T12:44:22+00:00',
    'sim_phone_number': '+7 (999) 123-45-67',
    'gnss': {},
    'gps_position': {'lat': 89, 'lon': 44},
    'states': {
        'dms.xxx': {'some': 'thing', 'more': {}},
        'dms.yyy': 2,
        'some.sxs': True,
        'some.ggg': 4.22,
    },
    'some_new_field': {'s1': 'ss'},
}

LAST_LOCATION1 = {
    'lat': 52.14214,
    'lon': 100.14214,
    'accuracy_m': 1.2424,
    'speed_kmph': 124.14214,
    'direction_deg': 1244.555,
    'updated_at': '1990-01-01T00:00:00+00:00',
}

BAD_LAST_LOCATION1 = {
    'lat': 100.14214,
    'lon': 0.14214,
    'accuracy_m': 1.2424,
    'speed_kmph': 124.14214,
    'direction_deg': 1244.555,
    'updated_at': '1990-01-01T00:00:00+00:00',
}

BAD_LAST_LOCATION2 = {
    'lat': 100.14214,
    'lon': 0.14214,
    'accuracy_m': 1.2424,
    'speed_kmph': 124.14214,
    'direction_deg': 1244.555,
    'updated_at': '2500-01-01T00:00:00+00:00',
}

BAD_LAST_LOCATION3 = {
    'lat': 100.14214,
    'accuracy_m': 1.2424,
    'speed_kmph': 124.14214,
    'direction_deg': 1244.555,
    'updated_at': '2500-01-01T00:00:00+00:00',
}

BAD_LAST_LOCATION4: typing.Dict[str, typing.Any] = {}


@pytest.mark.config(
    SIGNALQ_DRIVEMATICS_API_BAD_REDIS_STATUSES_THROW_ENABLED=True,
)
@pytest.mark.redis_store(
    [
        'mset',
        {
            'DeviceStatuses:sn1': json.dumps(STATUS1),
            'DeviceStatuses:sn2': json.dumps(STATUS2),
            'DeviceStatuses:sn_with_bad_status': json.dumps(STATUS3_BAD),
            'DeviceLastLocation:sn1': json.dumps(LAST_LOCATION1),
            'DeviceLastLocation:sn_bad_loc1': json.dumps(BAD_LAST_LOCATION1),
            'DeviceLastLocation:sn_bad_loc2': json.dumps(BAD_LAST_LOCATION2),
            'DeviceLastLocation:sn_bad_loc3': json.dumps(BAD_LAST_LOCATION3),
            'DeviceLastLocation:sn_bad_loc4': json.dumps(BAD_LAST_LOCATION4),
        },
    ],
)
@pytest.mark.parametrize(
    'serial_numbers, expected_code, expected_response',
    [
        (
            ['sn1'],
            200,
            {
                'items': [
                    {
                        'serial_number': 'sn1',
                        'status': STATUS1,
                        'last_location': LAST_LOCATION1,
                    },
                ],
            },
        ),
        (
            ['sn1', 'sn2'],
            200,
            {
                'items': [
                    {
                        'serial_number': 'sn1',
                        'status': STATUS1,
                        'last_location': LAST_LOCATION1,
                    },
                    {'serial_number': 'sn2', 'status': STATUS2_WITHOUT_UNUSED},
                ],
            },
        ),
        (
            ['sn2'],
            200,
            {
                'items': [
                    {'serial_number': 'sn2', 'status': STATUS2_WITHOUT_UNUSED},
                ],
            },
        ),
        (['sn24444'], 200, {'items': [{'serial_number': 'sn24444'}]}),
        (
            ['sn2', 'sn3', 'sn4'],
            200,
            {
                'items': [
                    {'serial_number': 'sn2', 'status': STATUS2_WITHOUT_UNUSED},
                    {'serial_number': 'sn3'},
                    {'serial_number': 'sn4'},
                ],
            },
        ),
        pytest.param(
            ['sn1', 'sn_with_bad_status'],
            200,
            {
                'items': [
                    {
                        'serial_number': 'sn1',
                        'status': STATUS1,
                        'last_location': LAST_LOCATION1,
                    },
                    {'serial_number': 'sn_with_bad_status'},
                ],
            },
            marks=pytest.mark.config(
                SIGNALQ_DRIVEMATICS_API_BAD_REDIS_STATUSES_THROW_ENABLED=False,
            ),
        ),
        (['sn1', 'sn2', 'sn_with_bad_status'], 500, None),
        (['sn1', 'sn2', 'sn_bad_loc1'], 500, None),
        (['sn1', 'sn2', 'sn_bad_loc2'], 500, None),
        (['sn1', 'sn2', 'sn_bad_loc3'], 500, None),
        (['sn1', 'sn2', 'sn_bad_loc4'], 500, None),
    ],
)
async def test_drivematics_v1_statuses_retrieve(
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
    assert response.json() == expected_response
