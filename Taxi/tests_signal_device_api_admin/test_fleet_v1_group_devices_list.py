import typing

import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/group/devices/list'

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
            'park_id_car_id': 'p2_car3',
            'revision': '0_1574328384_71',
        },
        {
            'data': {
                'car_id': 'car4',
                'brand': 'Volkswagen',
                'model': 'Tuareg',
            },
            'park_id_car_id': 'p2_car4',
            'revision': '0_1574328384_71',
        },
    ],
}

RESPONSE1 = {
    'devices': [
        {
            'serial_number': 'AB12FE45DD',
            'device_id': '4306de3dfd82406d81ea3c098c80e9ba',
        },
        {
            'serial_number': 'FFFDEAD4',
            'device_id': '77748dae0a3244ebb9e1b8d244982c28',
            'plate_number': 'О122КХ777',
            'brand': 'Kia',
            'model': 'Rio',
        },
        {
            'serial_number': 'FFF2F4666',
            'device_id': '11449fbd4c7760578456c4a123456789',
        },
        {
            'serial_number': 'FFFFF4666',
            'device_id': '12349fbd4c7760578456c4a123456789',
            'brand': 'Volkswagen',
            'model': 'Tuareg',
        },
    ],
}

RESPONSE2 = {
    'devices': [
        {
            'serial_number': 'AB12FE45DD',
            'device_id': '4306de3dfd82406d81ea3c098c80e9ba',
        },
    ],
}

RESPONSE3 = {
    'devices': [
        {
            'serial_number': 'FFF9F4666',
            'device_id': '1444922d4c7760578456c4a123456789',
        },
        {
            'serial_number': 'AB1',
            'device_id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
            'plate_number': 'О121КХ777',
            'brand': 'Toyota',
            'model': 'Prius',
        },
    ],
}

RESPONSE4: typing.Dict[str, typing.List[typing.Dict]] = {'devices': []}

RESPONSE5 = {
    'devices': [
        {
            'serial_number': 'FFFDEAD4',
            'device_id': '77748dae0a3244ebb9e1b8d244982c28',
            'plate_number': 'О122КХ777',
            'brand': 'Kia',
            'model': 'Rio',
        },
        {
            'serial_number': 'FFF2F4666',
            'device_id': '11449fbd4c7760578456c4a123456789',
        },
        {
            'serial_number': 'FFFFF4666',
            'device_id': '12349fbd4c7760578456c4a123456789',
            'brand': 'Volkswagen',
            'model': 'Tuareg',
        },
    ],
}

ERROR_RESPONSE = {'code': 'bad_group', 'message': 'Incorrect group provided'}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, group_id, is_including_subgroups_devices, '
    'expected_code, expected_response',
    [
        ('p2', '29a168a6-2fe3-401d-9959-ba1b14fd4862', True, 200, RESPONSE1),
        ('p2', '29a168a6-2fe3-401d-9959-ba1b14fd4862', False, 200, RESPONSE2),
        ('p2', '09a1d1ab-6e60-4d7b-9144-dfad7fcf9000', True, 200, RESPONSE3),
        ('p2', '4552f39f-e868-46c1-8139-b5bf2dcda760', True, 200, RESPONSE4),
        ('p2', '1db9bcc6-982c-46ff-a161-78fa1817be01', False, 200, RESPONSE5),
        (
            'p3',
            '4552f39f-e868-46c1-8139-b5bf2dcda760',
            False,
            400,
            ERROR_RESPONSE,
        ),
    ],
)
async def test_group_devices_list_without_cursor(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        park_id,
        group_id,
        is_including_subgroups_devices,
        expected_code,
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
    body = {
        'group_id': group_id,
        'is_including_subgroups_devices': is_including_subgroups_devices,
    }

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response


RESPONSE2_WITH_CURSOR1 = {
    'devices': [
        {
            'serial_number': 'FFF9F4666',
            'device_id': '1444922d4c7760578456c4a123456789',
        },
        {
            'serial_number': 'AB1',
            'device_id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
            'plate_number': 'О121КХ777',
            'brand': 'Toyota',
            'model': 'Prius',
        },
    ],
    'cursor': utils.get_encoded_group_devices_list_cursor(
        updated_at='2020-02-27T02:00:00.000001+00:00',
        public_id='e58e753c44e548ce9edaec0e0ef9c8c1',
    ),
}
RESPONSE2_WITH_CURSOR2: typing.Dict[str, typing.List[typing.Dict]] = {
    'devices': [],
}

RESPONSE4_WITH_CURSOR1 = {
    'devices': [
        {
            'serial_number': 'FFFDEAD4',
            'device_id': '77748dae0a3244ebb9e1b8d244982c28',
            'plate_number': 'О122КХ777',
            'brand': 'Kia',
            'model': 'Rio',
        },
        {
            'serial_number': 'FFF2F4666',
            'device_id': '11449fbd4c7760578456c4a123456789',
        },
    ],
    'cursor': utils.get_encoded_group_devices_list_cursor(
        updated_at='2020-02-26T02:00:00.120001+00:00',
        public_id='11449fbd4c7760578456c4a123456789',
    ),
}
RESPONSE4_WITH_CURSOR2 = {
    'devices': [
        {
            'serial_number': 'FFFFF4666',
            'device_id': '12349fbd4c7760578456c4a123456789',
            'brand': 'Volkswagen',
            'model': 'Tuareg',
        },
    ],
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
@pytest.mark.parametrize(
    'park_id, group_id, is_including_subgroups_devices, '
    'expected_response1, expected_response2',
    [
        (
            'p2',
            '09a1d1ab-6e60-4d7b-9144-dfad7fcf9000',
            True,
            RESPONSE2_WITH_CURSOR1,
            RESPONSE2_WITH_CURSOR2,
        ),
        (
            'p2',
            '1db9bcc6-982c-46ff-a161-78fa1817be01',
            False,
            RESPONSE4_WITH_CURSOR1,
            RESPONSE4_WITH_CURSOR2,
        ),
    ],
)
async def test_group_devices_list_with_cursor(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        park_id,
        group_id,
        is_including_subgroups_devices,
        expected_response1,
        expected_response2,
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
    body = {
        'group_id': group_id,
        'is_including_subgroups_devices': is_including_subgroups_devices,
    }

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json == expected_response1

    body['cursor'] = response_json.pop('cursor')
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response2


RESPONSE1_WITHOUT_VEHICLES = {
    'devices': [
        {
            'serial_number': 'AB12FE45DD',
            'device_id': '4306de3dfd82406d81ea3c098c80e9ba',
        },
        {
            'serial_number': 'FFFDEAD4',
            'device_id': '77748dae0a3244ebb9e1b8d244982c28',
        },
        {
            'serial_number': 'FFF2F4666',
            'device_id': '11449fbd4c7760578456c4a123456789',
        },
        {
            'serial_number': 'FFFFF4666',
            'device_id': '12349fbd4c7760578456c4a123456789',
        },
    ],
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, group_id, is_including_subgroups_devices, '
    'expected_code, expected_response',
    [
        (
            'p2',
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            True,
            200,
            RESPONSE1_WITHOUT_VEHICLES,
        ),
    ],
)
async def test_group_devices_list_fleet_vehicles_error(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        park_id,
        group_id,
        is_including_subgroups_devices,
        expected_code,
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

    fleet_vehicles.set_fleet_vehicles_err_response(500)

    headers = {**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id}
    body = {
        'group_id': group_id,
        'is_including_subgroups_devices': is_including_subgroups_devices,
    }

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response


ALL_DEVICES_RESPONSE = [
    {'device_id': 'dev1', 'serial_number': '11111'},
    {'device_id': 'dev2', 'serial_number': '77777'},
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
        'devices': web_common.DEMO_DEVICES,
        'events': [],
        'vehicles': [],
        'groups': web_common.DEMO_GROUPS,
        'drivers': [],
    },
    SIGNAL_DEVICE_API_ADMIN_DEVICE_GROUPS_LIMITS_V2={
        'groups_list_limit': 2,
        'group_devices_list_limit': 2,
        'ungrouped_devices_list_limit': 2,
    },
)
@pytest.mark.parametrize(
    'group_id, is_including_subgroups_devices, expected_response',
    [
        pytest.param(
            'g1', True, ALL_DEVICES_RESPONSE[0:1], id='with subgroups',
        ),
        pytest.param('g1', False, [], id='no subgroups'),
    ],
)
async def test_demo_group_devices_list(
        taxi_signal_device_api_admin,
        group_id,
        is_including_subgroups_devices,
        expected_response,
        mockserver,
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
        json={
            'group_id': 'g1',
            'is_including_subgroups_devices': is_including_subgroups_devices,
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    assert response.json()['devices'] == expected_response
