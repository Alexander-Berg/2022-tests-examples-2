import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/device'

DRIVER_PROFILE_1 = {
    'car': {'id': 'car1', 'number': 'О122КХ777'},
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
}

FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'data': {'car_id': 'car1', 'number': 'О122КХ777'},
            'park_id_car_id': 'p1_car1',
            'revision': '0_1574328384_71',
        },
    ],
}

DRIVER_PROFILES_LIST_SINGLE_RESPONSE = {
    'driver_profiles': [DRIVER_PROFILE_1],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 300,
}

EXPECTED_RESPONSE1 = {
    'device': {
        'device': {
            'id': 'has_everything',
            'imei': '990000862471854',
            'mac_wlan0': '07:f2:74:af:8b:b1',
            'serial_number': 'ABC1',
            'software_version': '2.31-2',
            'is_connection_available': True,
        },
        'device_park_profile': {'is_active': True},
        'thread_id': utils.to_base64('||has_everything').rstrip('='),
        'driver': {
            'first_name': 'Petr',
            'id': 'd1',
            'middle_name': 'D`',
            'last_name': 'Ivanov',
            'license_number': '7723306794',
            'phones': ['+79265975310'],
        },
        'status': {
            'gnss': {
                'accuracy_m': 3.0,
                'direction_deg': 100.0,
                'lat': 53.3242,
                'lon': 34.9885,
                'speed_kmph': 10.0,
            },
            'iccid': '89310410106543789301',
            'is_online': True,
            'uptime_ms': 300000,
            'updated_at': '2020-08-11T15:00:00+00:00',
        },
        'vehicle': {'id': 'car1', 'plate_number': 'О122КХ777'},
    },
}

EXPECTED_RESPONSE2 = {
    'device': {
        'device': {
            'id': 'has_everything1337',
            'imei': '990000862471855',
            'mac_wlan0': '07:f2:74:af:8b:b1',
            'serial_number': 'ABC3',
            'is_connection_available': False,
        },
        'device_park_profile': {
            'is_active': True,
            'group': {
                'id': '635ffb7b-8c06-476d-a30a-4bc9ae65d272',
                'name': '2pac',
            },
        },
        'thread_id': utils.to_base64('||has_everything1337').rstrip('='),
        'status': {'is_online': False},
    },
}

EXPECTED_RESPONSE3 = {
    'device': {
        'device': {
            'id': 'ah_sama_lama_duma',
            'imei': '110000862471855',
            'mac_wlan0': '07:f3:74:af:8b:b1',
            'serial_number': 'ABC4',
            'is_connection_available': False,
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
        'thread_id': utils.to_base64('||ah_sama_lama_duma').rstrip('='),
        'status': {'is_online': False},
    },
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.parametrize(
    'serial_number, expected_code, expected_response',
    [
        ('  ABC1 ', 200, EXPECTED_RESPONSE1),
        ('abc2', 404, None),
        ('!@#<&^*', 400, None),
        ('ABC3', 200, EXPECTED_RESPONSE2),
        ('ABC4', 200, EXPECTED_RESPONSE3),
    ],
)
async def test_search_by_serial_number(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        parks,
        serial_number,
        expected_code,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {'statuses': []}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE)
    parks.set_driver_profiles_response(DRIVER_PROFILES_LIST_SINGLE_RESPONSE)

    response = await taxi_signal_device_api_admin.get(
        ENDPOINT,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        params={'serial_number': serial_number},
    )
    assert response.status_code == expected_code, response.text
    if expected_code != 200:
        assert fleet_vehicles.fleet_vehicles.times_called == 0
        assert parks.driver_profiles_list.times_called == 0
        return

    assert response.json() == expected_response
    if 'vehicle' not in expected_response['device']:
        return

    assert fleet_vehicles.fleet_vehicles.times_called == 1
    fleet_vehicles_request = fleet_vehicles.fleet_vehicles.next_call()[
        'request'
    ].json
    assert fleet_vehicles_request == {'id_in_set': ['p1_car1']}

    assert parks.driver_profiles_list.times_called == 1
    parks_request = parks.driver_profiles_list.next_call()['request'].json
    assert parks_request == {
        'query': {'park': {'id': 'p1', 'car': {'id': ['car1']}}},
        'fields': {
            'driver_profile': [
                'id',
                'first_name',
                'middle_name',
                'last_name',
                'driver_license',
                'phones',
            ],
            'car': ['id'],
        },
        'limit': 100,
        'offset': 0,
    }


DEMO_EXPECTED_RESPONSE = {
    'device': {
        'device': {
            'id': 'dev2',
            'mac_wlan0': '77777',
            'serial_number': '77777',
            'is_connection_available': False,
        },
        'device_park_profile': {
            'is_active': True,
            'group': {'id': 'g2', 'name': 'Scooters'},
        },
        'thread_id': utils.to_base64('||dev2').rstrip('='),
        'driver': {
            'first_name': 'Grisha',
            'id': 'dr2',
            'last_name': 'Dergachev',
        },
        'status': {'is_online': True},
    },
}


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
        'vehicles': web_common.DEMO_VEHICLES,
        'groups': web_common.DEMO_GROUPS,
        'drivers': web_common.DEMO_DRIVERS,
    },
)
@pytest.mark.parametrize(
    'serial_number, expected_code, expected_response',
    [('77777', 200, DEMO_EXPECTED_RESPONSE), ('no such serial', 404, None)],
)
async def test_demo_device_get(
        taxi_signal_device_api_admin,
        serial_number,
        expected_code,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('no_such_park'),
                    'specifications': ['taxi'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.get(
        ENDPOINT,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no_such_park'},
        params={'serial_number': serial_number},
    )
    assert response.status_code == expected_code, response.text
    if expected_code == 200:
        response_json = response.json()
        assert 'status' in response_json['device']
        assert 'gnss' in response_json['device']['status']
        del response_json['device']['status']['gnss']
        assert response_json == expected_response, response.text
