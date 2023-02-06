import copy

import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/events/thread/details'


DRIVER_PROFILES_RESPONSE1 = {
    'driver_profiles': [
        {
            'driver_profile': {
                'first_name': 'Petr',
                'middle_name': 'D`',
                'last_name': 'Ivanov',
                'driver_license': {
                    'expiration_date': '2025-08-07T00:00:00+0000',
                    'issue_date': '2015-08-07T00:00:00+0000',
                    'normalized_number': '7723306794',
                    'number': '7723306794',
                },
                'id': 'd1',
                'phones': ['+79265975310'],
            },
        },
    ],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 1,
}

DRIVER_PROFILES_RESPONSE2 = {
    'driver_profiles': [
        {
            'driver_profile': {
                'first_name': 'Petr',
                'middle_name': 'D`',
                'last_name': 'Ivanov',
                'driver_license': {
                    'expiration_date': '2025-08-07T00:00:00+0000',
                    'issue_date': '2015-08-07T00:00:00+0000',
                    'normalized_number': '7723306794',
                    'number': '7723306794',
                },
                'id': 'd2',
                'phones': ['+79265975310'],
            },
        },
    ],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 1,
}

DRIVER_PROFILES_RESPONSE3 = {
    'driver_profiles': [
        {
            'driver_profile': {
                'first_name': 'Petr',
                'middle_name': 'D`',
                'last_name': 'Ivanov',
                'driver_license': {
                    'expiration_date': '2025-08-07T00:00:00+0000',
                    'issue_date': '2015-08-07T00:00:00+0000',
                    'normalized_number': '7723306794',
                    'number': '7723306794',
                },
                'id': 'd3',
                'phones': ['+79265975310'],
            },
        },
    ],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 1,
}

DRIVER_PROFILES_RESPONSE4 = {
    'driver_profiles': [
        {
            'driver_profile': {
                'first_name': 'Petr',
                'middle_name': 'D`',
                'last_name': 'Ivanov',
                'driver_license': {
                    'expiration_date': '2025-08-07T00:00:00+0000',
                    'issue_date': '2015-08-07T00:00:00+0000',
                    'normalized_number': '7723306794',
                    'number': '7723306794',
                },
                'id': 'd4',
                'phones': ['+79265975310'],
            },
        },
    ],
    'offset': 0,
    'parks': [{'id': 'p2'}],
    'total': 1,
    'limit': 1,
}

DRIVER_PROFILES_RESPONSE5 = {
    'driver_profiles': [
        {
            'driver_profile': {
                'first_name': 'Petr',
                'middle_name': 'D`',
                'last_name': 'Ivanov',
                'driver_license': {
                    'expiration_date': '2025-08-07T00:00:00+0000',
                    'issue_date': '2015-08-07T00:00:00+0000',
                    'normalized_number': '7723306794',
                    'number': '7723306794',
                },
                'id': 'd5',
                'phones': ['+79265975310'],
            },
        },
    ],
    'offset': 0,
    'parks': [{'id': 'p2'}],
    'total': 1,
    'limit': 1,
}

DRIVER_PROFILES_RESPONSE_EMPTY = {
    'driver_profiles': [],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 1,
}

FLEET_VEHICLES_RESPONSE1 = {
    'vehicles': [
        {
            'data': {
                'car_id': 'car1',
                'number': 'О122КХ777',
                'brand': 'lol',
                'model': 'kek',
            },
            'park_id_car_id': 'p1_car1',
            'revision': '0_1574328384_71',
        },
    ],
}

FLEET_VEHICLES_RESPONSE2 = {
    'vehicles': [
        {
            'data': {
                'car_id': 'car2',
                'number': 'О122КХ777',
                'brand': 'lol',
                'model': 'kek',
            },
            'park_id_car_id': 'p1_car2',
            'revision': '0_1574328384_71',
        },
    ],
}

FLEET_VEHICLES_RESPONSE3 = {
    'vehicles': [
        {
            'data': {
                'car_id': 'car3',
                'number': 'О122КХ777',
                'brand': 'lol',
                'model': 'kek',
            },
            'park_id_car_id': 'p1_car3',
            'revision': '0_1574328384_71',
        },
    ],
}

FLEET_VEHICLES_RESPONSE_EMPTY = {
    'vehicles': [{'data': {}, 'park_id_car_id': '', 'revision': ''}],
}

RESPONSE1 = {
    'driver': {
        'first_name': 'Petr',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'id': 'd1',
        'license_number': '7723306794',
        'phones': ['+79265975310'],
        'avatar_url': 'testavatar',
    },
    'work_status': 'online',
    'vehicle': {
        'id': 'car1',
        'plate_number': 'О122КХ777',
        'brand': 'lol',
        'model': 'kek',
    },
    'device': {
        'id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
        'is_online': False,
        'serial_number': 'AB1',
        'is_connection_available': True,
    },
    'device_park_profile': {'is_active': True},
}

RESPONSE2 = copy.deepcopy(RESPONSE1)
RESPONSE2['device'] = {
    'id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
    'is_online': False,
    'serial_number': 'AB1',
    'is_connection_available': True,
    'mqtt_commands_supported': {
        'com1': {'latest_version': 5, 'versions_supported': [1, 0, 5, 4]},
        'com2': {'latest_version': 12, 'versions_supported': [12]},
    },
}

RESPONSE3 = {
    'driver': {
        'first_name': 'Petr',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'id': 'd2',
        'license_number': '7723306794',
        'phones': ['+79265975310'],
        'avatar_url': 'testavatar',
    },
    'work_status': 'online',
    'vehicle': {
        'id': 'car2',
        'plate_number': 'О122КХ777',
        'brand': 'lol',
        'model': 'kek',
    },
    'device': {
        'id': 'e58e753c44e548ce9edaec0e0ef9c8c2',
        'is_online': False,
        'serial_number': 'AB2',
        'is_connection_available': True,
    },
    'device_park_profile': {'is_active': False},
}

RESPONSE4 = {
    'driver': {
        'first_name': 'Petr',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'id': 'd4',
        'license_number': '7723306794',
        'phones': ['+79265975310'],
        'avatar_url': 'testavatar',
    },
    'device': {
        'id': 'e58e753c44e548ce9edaec0e0ef9c8c4',
        'is_online': False,
        'serial_number': 'AB4',
        'is_connection_available': True,
    },
    'device_park_profile': {
        'is_active': True,
        'group': {
            'id': '635ffb7b-8c06-476d-a30a-4bc9ae65d272',
            'name': '2pac',
        },
        'subgroup': {
            'id': '3bd269aa-3aca-494b-8bbb-88f99847464a',
            'name': 'Shakur',
        },
    },
}

RESPONSE5 = {
    'driver': {
        'first_name': 'Petr',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'id': 'd5',
        'license_number': '7723306794',
        'phones': ['+79265975310'],
        'avatar_url': 'testavatar',
    },
    'vehicle': {
        'id': 'car1',
        'plate_number': 'О122КХ777',
        'brand': 'lol',
        'model': 'kek',
    },
    'device': {
        'id': 'e58e753c44e548ce9edaec0e0ef9c8c5',
        'is_online': False,
        'serial_number': 'AB5',
        'is_connection_available': False,
    },
    'device_park_profile': {'is_active': True},
}

MQTT_CONFIG1 = pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_MQTT_COMMANDS={
        '__default__': {},
        '2.31-3': {'com3': {'versions_supported': [23]}},
        '2.31-1': {'com1': {'versions_supported': [1]}},
        '2.31-2': {
            'com1': {'versions_supported': [1, 0, 5, 4]},
            'com2': {'versions_supported': [12]},
        },
    },
)


@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.parametrize(
    'driver_profile_id, car_id, device_id, park_id, '
    'code, expected_fleet_vehicles_response, '
    'expected_driver_profiles_response, expected_response',
    [
        (
            'd1',
            'car1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            'p1',
            200,
            FLEET_VEHICLES_RESPONSE1,
            DRIVER_PROFILES_RESPONSE1,
            RESPONSE1,
        ),
        pytest.param(
            'd1',
            'car1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            'p1',
            200,
            FLEET_VEHICLES_RESPONSE1,
            DRIVER_PROFILES_RESPONSE1,
            RESPONSE2,
            marks=MQTT_CONFIG1,
        ),
        (
            'd2',
            'car2',
            'e58e753c44e548ce9edaec0e0ef9c8c2',
            'p1',
            200,
            FLEET_VEHICLES_RESPONSE2,
            DRIVER_PROFILES_RESPONSE2,
            RESPONSE3,
        ),
        (
            'd4',
            '',
            'e58e753c44e548ce9edaec0e0ef9c8c4',
            'p2',
            200,
            [],
            DRIVER_PROFILES_RESPONSE4,
            RESPONSE4,
        ),
        (
            'd3',
            'car3',
            'e58e753c44e548ce9edaec0e0ef9c8c3',
            'p1',
            400,
            {},
            {},
            {},
        ),
        (
            'd100',
            'car1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            'p1',
            404,
            FLEET_VEHICLES_RESPONSE1,
            DRIVER_PROFILES_RESPONSE_EMPTY,
            {},
        ),
        (
            'd1',
            'car10',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            'p1',
            404,
            FLEET_VEHICLES_RESPONSE_EMPTY,
            {},
            {},
        ),
        ('d1', 'car1', 'xxx', 'p1', 404, {}, {}, {}),
        (
            'd5',
            'car1',
            'e58e753c44e548ce9edaec0e0ef9c8c5',
            'p1',
            200,
            FLEET_VEHICLES_RESPONSE1,
            DRIVER_PROFILES_RESPONSE5,
            RESPONSE5,
        ),
    ],
)
async def test_thread_details(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        parks,
        driver_profile_id,
        car_id,
        device_id,
        park_id,
        code,
        expected_fleet_vehicles_response,
        expected_driver_profiles_response,
        expected_response,
        mockserver,
):
    @mockserver.json_handler(
        '/udriver-photos/driver-photos/v1/last-not-rejected-photo',
    )
    def _get_photo(request):
        return {
            'actual_photo': {
                'avatar_url': 'testavatar',
                'portrait_url': 'testportrait',
            },
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        request_parsed = request.json
        if request_parsed['driver_ids'][0]['driver_id'] == 'd1':
            return {
                'statuses': [
                    {
                        'park_id': 'p1',
                        'driver_id': 'd1',
                        'status': 'online',
                        'updated_ts': 12345,
                    },
                ],
            }
        if request_parsed['driver_ids'][0]['driver_id'] == 'd2':
            return {
                'statuses': [
                    {
                        'park_id': 'p1',
                        'driver_id': 'd2',
                        'status': 'online',
                        'updated_ts': 12345,
                    },
                ],
            }
        if request_parsed['driver_ids'][0]['driver_id'] == 'd3':
            return {
                'statuses': [
                    {
                        'park_id': 'p1',
                        'driver_id': 'd3',
                        'status': 'online',
                        'updated_ts': 12345,
                    },
                ],
            }
        return {
            'statuses': [
                {
                    'park_id': 'p2',
                    'driver_id': 'd4',
                    'status': 'online',
                    'updated_ts': 12345,
                },
            ],
        }

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks(request):
        return {
            'parks': [
                {
                    'city_id': 'CITY_ID',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'p1',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN',
                    'name': 'NAME',
                    'specifications': ['taxi', 'signalq'],
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
                {
                    'city_id': 'CITY_ID2',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'p2',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN2',
                    'name': 'NAME2',
                    'specifications': ['signalq'],
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    fleet_vehicles.set_fleet_vehicles_response(
        expected_fleet_vehicles_response,
    )
    parks.set_driver_profiles_response(expected_driver_profiles_response)

    thread_id = utils.to_base64(f'{driver_profile_id}|{car_id}|{device_id}')

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'thread_id': thread_id},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id},
    )
    assert response.status_code == code, response.text
    if code == 200:
        assert response.json() == expected_response


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
        'events': web_common.DEMO_EVENTS,
        'vehicles': web_common.DEMO_VEHICLES,
        'groups': web_common.DEMO_GROUPS,
        'drivers': web_common.DEMO_DRIVERS,
    },
)
async def test_demo_events_thread_details(
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

    thread_id = utils.to_base64(f'dr1|v1|dev2')

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'thread_id': thread_id},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text

    response_json = response.json()
    assert (
        response_json['device']['serial_number']
        == web_common.DEMO_DEVICES[1]['serial_number']
        and response_json['driver']['first_name']
        == web_common.DEMO_DRIVERS[0]['first_name']
        and response_json['vehicle']['plate_number']
        == web_common.DEMO_VEHICLES[0]['plate_number']
        and response_json['device_park_profile']
        == {'is_active': True, 'group': {'id': 'g2', 'name': 'Scooters'}}
    )
