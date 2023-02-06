import typing

import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/ungrouped/devices/list'

FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'data': {
                'car_id': 'car1',
                'number': 'О121КХ777',
                'brand': 'Toyota',
                'model': 'Prius',
            },
            'park_id_car_id': 'p2_car1',
            'revision': '0_1574328384_71',
        },
        {
            'data': {
                'car_id': 'car2',
                'number': 'О122КХ777',
                'brand': 'Kia',
                'model': 'Rio',
            },
            'park_id_car_id': 'p2_car2',
            'revision': '0_1574328384_71',
        },
        {
            'data': {'car_id': 'car3', 'number': 'О123КХ777'},
            'park_id_car_id': 'p3_car3',
            'revision': '0_1574328384_71',
        },
        {
            'data': {
                'car_id': 'car4',
                'brand': 'Volkswagen',
                'model': 'Tuareg',
            },
            'park_id_car_id': 'p3_car4',
            'revision': '0_1574328384_71',
        },
    ],
}

RESPONSE1: typing.Dict[str, typing.List[typing.Dict]] = {'devices': []}

RESPONSE2 = {
    'devices': [
        {
            'serial_number': 'FFF9F4666',
            'device_id': '1444922d4c7760578456c4a123456789',
        },
        {
            'serial_number': 'FFF2F4666',
            'device_id': '11449fbd4c7760578456c4a123456789',
            'plate_number': 'О121КХ777',
            'brand': 'Toyota',
            'model': 'Prius',
        },
    ],
}

RESPONSE3 = {
    'devices': [
        {
            'serial_number': 'AB12FE45DD',
            'device_id': '4306de3dfd82406d81ea3c098c80e9ba',
            'brand': 'Volkswagen',
            'model': 'Tuareg',
        },
    ],
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, expected_response',
    [('p1', RESPONSE1), ('p2', RESPONSE2), ('p3', RESPONSE3)],
)
async def test_ungrouped_devices_list_without_cursor(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        park_id,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': ['signalq'],
                },
            ],
        }

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE)
    headers = {**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id}

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json={}, headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response


RESPONSE2_WITH_CURSOR1 = {
    'devices': [
        {
            'serial_number': 'FFF9F4666',
            'device_id': '1444922d4c7760578456c4a123456789',
        },
    ],
    'cursor': utils.get_encoded_group_devices_list_cursor(
        updated_at='2020-02-26T02:00:00.000001+00:00',
        public_id='1444922d4c7760578456c4a123456789',
    ),
}

RESPONSE2_WITH_CURSOR2 = {
    'devices': [
        {
            'serial_number': 'FFF2F4666',
            'device_id': '11449fbd4c7760578456c4a123456789',
            'plate_number': 'О121КХ777',
            'brand': 'Toyota',
            'model': 'Prius',
        },
    ],
    'cursor': utils.get_encoded_group_devices_list_cursor(
        updated_at='2020-02-26T02:00:00.120001+00:00',
        public_id='11449fbd4c7760578456c4a123456789',
    ),
}

RESPONSE2_WITH_CURSOR3: typing.Dict[str, typing.List[typing.Dict]] = {
    'devices': [],
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEVICE_GROUPS_LIMITS_V2={
        'groups_list_limit': 20,
        'group_devices_list_limit': 2,
        'ungrouped_devices_list_limit': 1,
    },
)
async def test_ungrouped_devices_list_with_cursor(
        taxi_signal_device_api_admin, fleet_vehicles, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('p2'),
                    'specifications': ['signalq'],
                },
            ],
        }

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE)
    headers = {**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p2'}
    body = {}

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json == RESPONSE2_WITH_CURSOR1

    for expected_response in (RESPONSE2_WITH_CURSOR2, RESPONSE2_WITH_CURSOR3):
        body['cursor'] = response_json.pop('cursor')
        response = await taxi_signal_device_api_admin.post(
            ENDPOINT, json=body, headers=headers,
        )
        response_json = response.json()
        assert response.status_code == 200, response.text
        assert response_json == expected_response


DEMO_DEVICES = [
    {
        'id': 'dev1',
        'serial_number': '11111',
        'mac_wlan0': '11111',
        'is_online': True,
    },
    {
        'id': 'dev2',
        'serial_number': '77777',
        'mac_wlan0': '77777',
        'group_id': 'g2',
    },
    {'id': 'dev3', 'serial_number': '33333', 'mac_wlan0': '33333'},
]

DEVICES_LIST = [
    {'device_id': 'dev1', 'serial_number': '11111'},
    {'device_id': 'dev3', 'serial_number': '33333'},
]


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': DEMO_DEVICES,
        'events': [],
        'vehicles': [],
        'groups': [],
        'drivers': [],
    },
    SIGNAL_DEVICE_API_ADMIN_DEVICE_GROUPS_LIMITS_V2={
        'groups_list_limit': 1,
        'group_devices_list_limit': 1,
        'ungrouped_devices_list_limit': 1,
    },
)
async def test_demo_group_ungrouped_devices_list(
        taxi_signal_device_api_admin, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('no such park'),
                    'specifications': ['taxi'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json['devices'][0] == DEVICES_LIST[0]

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'cursor': response_json['cursor']},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json['devices'][0] == DEVICES_LIST[1]

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'cursor': response_json['cursor']},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json['devices'] == []
