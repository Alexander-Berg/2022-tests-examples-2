# pylint: disable=too-many-lines
import pytest

from testsuite.utils import ordered_object

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/devices/list'

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

DRIVER_PROFILE_2 = {
    'car': {'id': 'car1', 'number': 'О122КХ777'},
    'driver_profile': {
        'first_name': 'Vtoroi',
        'last_name': 'Voditel',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306794',
            'number': '7723306794',
        },
        'id': 'd100500',
        'phones': ['+79265975310'],
    },
}

DRIVER_PROFILE_CAR2 = {
    'car': {'id': 'car2', 'number': '2222КХ777'},
    'driver_profile': {
        'first_name': 'Vtoroi',
        'last_name': 'Voditel',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306794',
            'number': '7723306794',
        },
        'id': 'd100500',
        'phones': ['+79265975310'],
    },
}

DRIVER_PROFILES_LIST_DUPLICATE_CAR_BINDING = {
    'driver_profiles': [DRIVER_PROFILE_1, DRIVER_PROFILE_2],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 2,
    'limit': 300,
}

DRIVER_PROFILES_LIST_SINGLE_RESPONSE = {
    'driver_profiles': [DRIVER_PROFILE_1],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 300,
}

FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'data': {'car_id': 'car1', 'number': 'О122КХ777'},
            'park_id_car_id': 'p1_car1',
            'revision': '0_1574328384_71',
        },
        {
            'data': {'car_id': 'car2', 'number': 'О122КХ178'},
            'park_id_car_id': 'p1_car2',
            'revision': '0_1574328384_71',
        },
    ],
}

EMPTY_CARS_LIST_RESPONSE = {'cars': [], 'offset': 0, 'limit': 100, 'total': 0}
NOT_EMPTY_CARS_LIST_RESPONSE = {
    'cars': [
        {
            'brand': 'AC',
            'color': 'Желтый',
            'id': '32123',
            'model': '378 GT Zagato',
            'normalized_number': '123',
            'number': '123',
            'year': 2019,
        },
    ],
    'offset': 0,
    'limit': 100,
    'total': 1,
}

EMPTY_DRIVER_PROFILES_LIST_RESPONSE = {
    'driver_profiles': [],
    'parks': [],
    'offset': 0,
    'limit': 100,
    'total': 0,
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.parametrize('text_filter', [None, ''])
async def test_return_all(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        parks,
        text_filter,
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

    request_body = {'limit': 100}
    if text_filter:
        request_body['query'] = {'text': text_filter}

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=request_body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'devices': [
            {
                'device': {
                    'id': 'has_everything',
                    'imei': '990000862471854',
                    'mac_wlan0': '07:f2:74:af:8b:b1',
                    'serial_number': 'AB1',
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
            {
                'device': {
                    'id': 'without_driver',
                    'imei': '351756051523999',
                    'mac_wlan0': 'a5:90:c5:98:95:48',
                    'serial_number': 'AB12FE45DD',
                    'software_version': '2.31.32-3',
                    'is_connection_available': True,
                },
                'device_park_profile': {'is_active': True},
                'thread_id': utils.to_base64('||without_driver').rstrip('='),
                'status': {
                    'gnss': {
                        'lat': 73.3242,
                        'lon': 54.9885,
                        'updated_at': '2020-08-11T14:00:00+00:00',
                    },
                    'iccid': '89310410106543789300',
                    'is_online': False,
                    'updated_at': '2020-08-11T14:50:00+00:00',
                },
                'vehicle': {'id': 'car2', 'plate_number': 'О122КХ178'},
            },
            {
                'device': {
                    'id': 'just_device',
                    'mac_wlan0': 'ca:ff:4d:64:f2:79',
                    'serial_number': 'FFEE33',
                    'is_connection_available': False,
                },
                'device_park_profile': {'is_active': True},
                'thread_id': utils.to_base64('||just_device').rstrip('='),
                'status': {'is_online': False},
            },
            {
                'device': {
                    'id': 'move_to_other_park',
                    'mac_wlan0': '32:41:27:d5:fb:ed',
                    'serial_number': 'FFFDEAD4',
                    'is_connection_available': False,
                },
                'device_park_profile': {'is_active': False},
                'thread_id': utils.to_base64('||move_to_other_park').rstrip(
                    '=',
                ),
            },
        ],
        'limit': 100,
        'offset': 0,
    }

    assert fleet_vehicles.fleet_vehicles.times_called == 1
    fleet_vehicles_request = fleet_vehicles.fleet_vehicles.next_call()[
        'request'
    ].json
    assert fleet_vehicles_request == {'id_in_set': ['p1_car1', 'p1_car2']}

    assert parks.driver_profiles_list.times_called == 1
    parks_request = parks.driver_profiles_list.next_call()['request'].json
    assert parks_request == {
        'query': {'park': {'id': 'p1', 'car': {'id': ['car1', 'car2']}}},
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
        'limit': 200,
        'offset': 0,
    }


def make_devices_with_is_connection_availables(  # pylint: disable=invalid-name
        is_first_available, is_second_available,
):
    return [
        {
            'device': {
                'id': 'has_everything',
                'imei': '990000862471854',
                'mac_wlan0': '07:f2:74:af:8b:b1',
                'serial_number': 'AB1',
                'software_version': '2.31-2',
                'is_connection_available': is_first_available,
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
        {
            'device': {
                'id': 'without_driver',
                'imei': '351756051523999',
                'mac_wlan0': 'a5:90:c5:98:95:48',
                'serial_number': 'AB12FE45DD',
                'software_version': '2.31.32-3',
                'is_connection_available': is_second_available,
            },
            'device_park_profile': {'is_active': True},
            'thread_id': utils.to_base64('||without_driver').rstrip('='),
            'status': {
                'gnss': {
                    'lat': 73.3242,
                    'lon': 54.9885,
                    'updated_at': '2020-08-11T14:00:00+00:00',
                },
                'iccid': '89310410106543789300',
                'is_online': False,
                'updated_at': '2020-08-11T14:50:00+00:00',
            },
            'vehicle': {'id': 'car2', 'plate_number': 'О122КХ178'},
        },
    ]


def make_device_flag_rules_config(min_software_version):
    return pytest.mark.config(
        SIGNAL_DEVICE_API_ADMIN_DEVICE_FLAG_RULES={
            'min_software_version': min_software_version,
        },
    )


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.parametrize(
    'is_first_available, is_second_available',
    [
        pytest.param(
            True, True, marks=make_device_flag_rules_config('2.31.0-2'),
        ),
        pytest.param(
            False, False, marks=make_device_flag_rules_config('3.0.0-0'),
        ),
        pytest.param(
            False, True, marks=make_device_flag_rules_config('2.31.1-1'),
        ),
        pytest.param(
            False, False, marks=make_device_flag_rules_config('2.31.32-4'),
        ),
        pytest.param(
            False, True, marks=make_device_flag_rules_config('2.31.32-3'),
        ),
        pytest.param(
            False, False, marks=make_device_flag_rules_config('2.31.33-0'),
        ),
        pytest.param(
            True, True, marks=make_device_flag_rules_config('2.30.33-5'),
        ),
        pytest.param(
            True, True, marks=make_device_flag_rules_config('1.321.323-133'),
        ),
    ],
)
async def test_is_connection_available(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        parks,
        is_first_available,
        is_second_available,
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

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 2},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'devices': make_devices_with_is_connection_availables(
            is_first_available, is_second_available,
        ),
        'limit': 2,
        'offset': 0,
    }


@pytest.mark.parametrize(
    'text, park_id, park_cars_list_respone',
    [
        ('FEE3', 'p1', EMPTY_CARS_LIST_RESPONSE),
        (
            '123',
            'p10',
            NOT_EMPTY_CARS_LIST_RESPONSE,
        ),  # запрос в паркс с пустым фильтром по кар айди
        # (который не должен происходить)
    ],
)
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.now('2020-08-11 15:00:03 +00:00')
async def test_serial_filter(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        parks,
        mockserver,
        text,
        park_id,
        park_cars_list_respone,
):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {'statuses': []}

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
    parks.set_driver_profiles_response(EMPTY_DRIVER_PROFILES_LIST_RESPONSE)
    parks.set_cars_list_response(park_cars_list_respone)
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'query': {'text': text}, 'limit': 100},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id},
    )
    assert response.status_code == 200, response.text
    if text == 'FEE3':
        assert response.json() == {
            'devices': [
                {
                    'device': {
                        'id': 'just_device',
                        'mac_wlan0': 'ca:ff:4d:64:f2:79',
                        'serial_number': 'FFEE33',
                        'is_connection_available': False,
                    },
                    'device_park_profile': {'is_active': True},
                    'thread_id': utils.to_base64('||just_device').rstrip('='),
                    'status': {'is_online': False},
                },
            ],
            'limit': 100,
            'offset': 0,
        }
        assert fleet_vehicles.fleet_vehicles.times_called == 0
        assert parks.driver_profiles_list.times_called == 1
        assert parks.cars_list.times_called == 1
    else:
        assert response.json() == {'devices': [], 'limit': 100, 'offset': 0}
        assert fleet_vehicles.fleet_vehicles.times_called == 0
        assert parks.driver_profiles_list.times_called == 0
        assert parks.cars_list.times_called == 0


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.now('2020-08-11 15:00:03 +00:00')
async def test_driver_profiles_filter(
        taxi_signal_device_api_admin, fleet_vehicles, parks, mockserver,
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
    parks.set_cars_list_response(EMPTY_CARS_LIST_RESPONSE)
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'query': {'text': 'Petr'}, 'limit': 100},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'devices': [
            {
                'device': {
                    'id': 'has_everything',
                    'imei': '990000862471854',
                    'mac_wlan0': '07:f2:74:af:8b:b1',
                    'serial_number': 'AB1',
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
                    'updated_at': '2020-08-11T15:00:00+00:00',
                    'is_online': True,
                    'uptime_ms': 300000,
                },
                'vehicle': {'id': 'car1', 'plate_number': 'О122КХ777'},
            },
        ],
        'limit': 100,
        'offset': 0,
    }
    assert (
        fleet_vehicles.fleet_vehicles.times_called == 0
    )  # plate numbers found in parks
    assert parks.driver_profiles_list.times_called == 1
    assert parks.cars_list.times_called == 1


DEV1 = {
    'id': 'dev1',
    'imei': '990000862471854',
    'mac_wlan0': '07:f2:74:af:8b:b1',
    'serial_number': 'ABCD11',
    'is_connection_available': False,
}
DEV2 = {
    'id': 'dev2',
    'imei': '351756051523999',
    'mac_wlan0': 'a5:90:c5:98:95:48',
    'serial_number': 'ABCD12',
    'is_connection_available': False,
}
DEV3 = {
    'id': 'dev3',
    'mac_wlan0': 'ca:ff:4d:64:f2:79',
    'serial_number': 'ABCD13',
    'is_connection_available': False,
}

DRIVER1 = {
    'first_name': 'Petr',
    'id': 'd1',
    'middle_name': 'D`',
    'last_name': 'Ivanov',
    'license_number': '7723306794',
    'phones': ['+79265975310'],
}

CAR1 = {'id': 'car1', 'plate_number': 'О122КХ777'}
CAR2 = {'id': 'car2', 'plate_number': 'О122КХ178'}
CAR3 = {'id': 'car3', 'plate_number': 'AAAA'}

THREAD_ID1 = utils.to_base64('||dev1').rstrip('=')
THREAD_ID2 = utils.to_base64('||dev2').rstrip('=')
THREAD_ID3 = utils.to_base64('||dev3').rstrip('=')

EXTRA_CARS_FIELDS = {
    'brand': '',
    'model': '',
    'color': '',
    'normalized_number': '',
}


@pytest.mark.parametrize(
    'text_filter, offset, limit, '
    'drivers_list, cars_list, fleet_vehicles_response,'
    'exp_req_drivers_list, exp_req_cars_list, exp_req_fleet_vehicles,'
    'expected_response',
    [
        pytest.param(
            ' abCD ',
            0,
            2,
            [DRIVER_PROFILES_LIST_SINGLE_RESPONSE],
            None,
            FLEET_VEHICLES_RESPONSE,
            None,
            None,
            None,
            {
                'devices': [
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
                        'driver': DRIVER1,
                        'status': {'is_online': False},
                        'vehicle': CAR1,
                    },
                    {
                        'device': DEV2,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID2,
                        'status': {'is_online': False},
                        'vehicle': CAR2,
                    },
                ],
                'limit': 2,
                'offset': 0,
            },
            id='serial_enough_wo_offset',
        ),
        pytest.param(
            'ABCD',
            1,
            1,
            [EMPTY_DRIVER_PROFILES_LIST_RESPONSE],
            None,
            FLEET_VEHICLES_RESPONSE,
            None,
            None,
            None,
            {
                'devices': [
                    {
                        'device': DEV2,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID2,
                        'status': {'is_online': False},
                        'vehicle': CAR2,
                    },
                ],
                'limit': 1,
                'offset': 1,
            },
            id='serial_enough_with_offset',
        ),
        pytest.param(
            'ABCD12',
            0,
            2,
            [
                EMPTY_DRIVER_PROFILES_LIST_RESPONSE,
                DRIVER_PROFILES_LIST_SINGLE_RESPONSE,
            ],
            None,
            FLEET_VEHICLES_RESPONSE,
            None,
            None,
            None,
            {
                'devices': [
                    {
                        'device': DEV2,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID2,
                        'status': {'is_online': False},
                        'vehicle': CAR2,
                    },
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
                        'driver': DRIVER1,
                        'status': {'is_online': False},
                        'vehicle': CAR1,
                    },
                ],
                'limit': 2,
                'offset': 0,
            },
            id='serial_and_driver_wo_offset',
        ),
        pytest.param(
            'ABCD12',
            1,
            1,
            [DRIVER_PROFILES_LIST_SINGLE_RESPONSE],
            None,
            None,
            [
                {
                    'limit': 1,
                    'offset': 0,
                    'car_ids': ['car1', 'car3', 'car4', 'car5'],
                },
            ],
            None,
            None,
            {
                'devices': [
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
                        'driver': DRIVER1,
                        'status': {'is_online': False},
                        'vehicle': CAR1,
                    },
                ],
                'limit': 1,
                'offset': 1,
            },
            id='serial_and_driver_w_offset',
        ),
        pytest.param(
            '10000',
            1,
            2,
            [
                {
                    'driver_profiles': [DRIVER_PROFILE_CAR2, DRIVER_PROFILE_1],
                    'offset': 0,
                    'parks': [{'id': 'p1'}],
                    'total': 1,
                    'limit': 300,
                },
            ],
            {'cars': [], 'offset': 0, 'total': 1},
            None,
            [
                {
                    'limit': 3,
                    'offset': 0,
                    'car_ids': ['car1', 'car2', 'car3', 'car4', 'car5'],
                },
            ],
            {'limit': 1, 'offset': 0, 'car_ids': ['car3', 'car4', 'car5']},
            None,
            {
                'devices': [
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
                        'driver': DRIVER1,
                        'status': {'is_online': False},
                        'vehicle': CAR1,
                    },
                ],
                'limit': 2,
                'offset': 1,
            },
            id='offset_in_the_middle_of_drivers',
        ),
        pytest.param(
            '10000',
            0,
            1,
            [DRIVER_PROFILES_LIST_SINGLE_RESPONSE],
            None,
            None,
            None,
            None,
            None,
            {
                'devices': [
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
                        'driver': DRIVER1,
                        'status': {'is_online': False},
                        'vehicle': CAR1,
                    },
                ],
                'limit': 1,
                'offset': 0,
            },
            id='only_drivers',
        ),
        pytest.param(
            'ABCD12',
            0,
            4,
            [
                EMPTY_DRIVER_PROFILES_LIST_RESPONSE,
                DRIVER_PROFILES_LIST_SINGLE_RESPONSE,
            ],
            {
                'cars': [
                    {
                        'id': 'car3',
                        'number': 'AAAA',
                        'year': 2000,
                        **EXTRA_CARS_FIELDS,
                    },
                ],
                'offset': 0,
                'total': 1,
            },
            FLEET_VEHICLES_RESPONSE,
            [
                {
                    'limit': (
                        100
                    ),  # because we have to send limit to get it back
                    'offset': 0,
                    'car_ids': ['car2'],
                },
                {
                    'limit': 3,
                    'offset': 0,
                    'car_ids': ['car1', 'car3', 'car4', 'car5'],
                },
            ],
            {'limit': 2, 'offset': 0, 'car_ids': ['car3', 'car4', 'car5']},
            {'id_in_set': ['p1_car2']},
            {
                'devices': [
                    {
                        'device': DEV2,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID2,
                        'status': {'is_online': False},
                        'vehicle': CAR2,
                    },
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
                        'driver': DRIVER1,
                        'status': {'is_online': False},
                        'vehicle': CAR1,
                    },
                    {
                        'device': DEV3,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID3,
                        'status': {'is_online': False},
                        'vehicle': CAR3,
                    },
                ],
                'limit': 4,
                'offset': 0,
            },
            id='serial_drivers_cars',
        ),
        pytest.param(
            '10000',
            0,
            1,
            [EMPTY_DRIVER_PROFILES_LIST_RESPONSE],
            {
                'cars': [
                    {
                        'id': 'car3',
                        'number': 'AAAA',
                        'year': 2000,
                        **EXTRA_CARS_FIELDS,
                    },
                ],
                'offset': 0,
                'total': 1,
            },
            None,
            None,
            None,
            None,
            {
                'devices': [
                    {
                        'device': DEV3,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID3,
                        'status': {'is_online': False},
                        'vehicle': CAR3,
                    },
                ],
                'limit': 1,
                'offset': 0,
            },
            id='just_cars',
        ),
        pytest.param(
            '10000',
            1,
            1,
            [EMPTY_DRIVER_PROFILES_LIST_RESPONSE],
            {
                'cars': [
                    {
                        'id': 'car3',
                        'number': 'AAAA',
                        'year': 2000,
                        **EXTRA_CARS_FIELDS,
                    },
                ],
                'offset': 1,
                'total': 1,
            },
            None,
            [
                {
                    'limit': 2,
                    'offset': 0,
                    'car_ids': ['car1', 'car2', 'car3', 'car4', 'car5'],
                },
            ],
            {
                'limit': 1,
                'offset': 1,
                'car_ids': ['car1', 'car2', 'car3', 'car4', 'car5'],
            },
            None,
            {
                'devices': [
                    {
                        'device': DEV3,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID3,
                        'status': {'is_online': False},
                        'vehicle': CAR3,
                    },
                ],
                'limit': 1,
                'offset': 1,
            },
            id='total_satisfied_less_then_offset',
        ),
        pytest.param(
            'ABCD12',
            1,
            4,
            [DRIVER_PROFILES_LIST_SINGLE_RESPONSE],
            {
                'cars': [
                    {
                        'id': 'car3',
                        'number': 'AAAA',
                        'year': 2000,
                        **EXTRA_CARS_FIELDS,
                    },
                ],
                'offset': 0,
                'total': 1,
            },
            None,
            [
                {
                    'limit': 4,
                    'offset': 0,
                    'car_ids': ['car1', 'car3', 'car4', 'car5'],
                },
            ],
            {'limit': 3, 'offset': 0, 'car_ids': ['car3', 'car4', 'car5']},
            None,
            {
                'devices': [
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
                        'driver': DRIVER1,
                        'status': {'is_online': False},
                        'vehicle': CAR1,
                    },
                    {
                        'device': DEV3,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID3,
                        'status': {'is_online': False},
                        'vehicle': CAR3,
                    },
                ],
                'limit': 4,
                'offset': 1,
            },
            id='total_satisfied_greater_than_offset',
        ),
        pytest.param(
            ' abCD ',
            0,
            2,
            [DRIVER_PROFILES_LIST_DUPLICATE_CAR_BINDING],
            None,
            FLEET_VEHICLES_RESPONSE,
            None,
            None,
            None,
            {
                'devices': [
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
                        'status': {'is_online': False},
                        'vehicle': CAR1,
                    },
                    {
                        'device': DEV2,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID2,
                        'status': {'is_online': False},
                        'vehicle': CAR2,
                    },
                ],
                'limit': 2,
                'offset': 0,
            },
            id='duplicate_driver_excluded',
        ),
        pytest.param(
            '10000',
            0,
            1,
            [DRIVER_PROFILES_LIST_DUPLICATE_CAR_BINDING],
            {
                'cars': [
                    {
                        'id': 'car1',
                        'number': 'О122КХ777',
                        'year': 2000,
                        **EXTRA_CARS_FIELDS,
                    },
                ],
                'offset': 0,
                'total': 1,
            },
            None,
            None,
            {
                'limit': 1,
                'offset': 0,
                'car_ids': ['car1', 'car2', 'car3', 'car4', 'car5'],
            },
            None,
            {
                'devices': [
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
                        'status': {'is_online': False},
                        'vehicle': CAR1,
                    },
                ],
                'limit': 1,
                'offset': 0,
            },
            id='duplicate_driver_all_row_excluded',
        ),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['text_search.sql'])
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.now('2020-08-11 15:00:03 +00:00')
async def test_text_search(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        parks,
        text_filter,
        offset,
        limit,
        drivers_list,
        cars_list,
        fleet_vehicles_response,
        exp_req_drivers_list,
        exp_req_cars_list,
        exp_req_fleet_vehicles,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'park_id': 'p1',
                    'driver_id': 'd1',
                    'status': 'online',
                    'updated_ts': 12345,
                },
                {
                    'park_id': 'p1',
                    'driver_id': 'd100500',
                    'status': 'online',
                    'updated_ts': 12345,
                },
            ],
        }

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

    fleet_vehicles.set_fleet_vehicles_response(fleet_vehicles_response)
    parks.set_driver_profiles_response(drivers_list)
    parks.set_cars_list_response(cars_list)
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'query': {'text': text_filter},
            'offset': offset,
            'limit': limit,
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response
    assert fleet_vehicles.fleet_vehicles.times_called == (
        1 if fleet_vehicles_response else 0
    )

    if exp_req_fleet_vehicles:
        req = fleet_vehicles.fleet_vehicles.next_call()['request'].json
        ordered_object.assert_eq(req, exp_req_fleet_vehicles, ['id_in_set'])

    assert parks.driver_profiles_list.times_called == len(drivers_list)
    if exp_req_drivers_list:
        for exp_req in exp_req_drivers_list:
            req = parks.driver_profiles_list.next_call()['request'].json
            ordered_object.assert_eq(
                {
                    'limit': req['limit'],
                    'offset': req['offset'],
                    'car_ids': req['query']['park']['car']['id'],
                },
                exp_req,
                ['car_ids'],
            )

    assert parks.cars_list.times_called == (1 if cars_list else 0)
    if exp_req_cars_list:
        req = parks.cars_list.next_call()['request'].json
        ordered_object.assert_eq(
            {
                'limit': req['limit'],
                'offset': req['offset'],
                'car_ids': req['query']['park']['car']['id'],
            },
            exp_req_cars_list,
            ['car_ids'],
        )


DRIVER_PROFILE_1 = {
    'car': {'id': 'car1'},
    'driver_profile': {
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

DRIVER_PROFILE_2 = {
    'car': {'id': 'car2', 'number': 'E112KX750'},
    'driver_profile': {
        'first_name': 'Sergey',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306796',
            'number': '7723306796',
        },
        'id': 'd2',
        'phones': ['+79265975311'],
    },
}

DRIVER_PROFILE_3 = {
    'car': {'id': 'car3', 'number': 'X432HA777'},
    'driver_profile': {
        'first_name': 'Alexey',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306790',
            'number': '7723306790',
        },
        'id': 'd3',
        'phones': ['+79265975510'],
    },
}

DRIVER_PROFILE_4 = {
    'car': {'id': 'car4'},
    'driver_profile': {
        'last_name': 'Petrov',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723396794',
            'number': '7713306794',
        },
        'id': 'd4',
        'phones': ['+79266975310'],
    },
}

DRIVER_PROFILES_LIST_2 = {
    'driver_profiles': [
        DRIVER_PROFILE_1,
        DRIVER_PROFILE_2,
        DRIVER_PROFILE_3,
        DRIVER_PROFILE_4,
    ],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 4,
    'limit': 300,
}

FLEET_VEHICLES_RESPONSE_2 = {
    'vehicles': [
        {
            'data': {'car_id': 'car1'},
            'park_id_car_id': 'p1_car1',
            'revision': '0_1574328384_71',
        },
        {
            'data': {'car_id': 'car2', 'number': 'E112KX750'},
            'park_id_car_id': 'p1_car2',
            'revision': '0_1574328384_71',
        },
        {
            'data': {'car_id': 'car3', 'number': 'X432HA777'},
            'park_id_car_id': 'p1_car3',
            'revision': '0_1574328384_71',
        },
        {
            'data': {'car_id': 'car4'},
            'park_id_car_id': 'p1_car4',
            'revision': '0_1574328384_71',
        },
    ],
}

RESPONSE_DEVICES_ELEM_1 = {
    'device': {
        'id': 'has_everything',
        'imei': '990000862471854',
        'mac_wlan0': '07:f2:74:af:8b:b1',
        'serial_number': 'AB1',
        'software_version': '02.0031-3',
        'is_connection_available': True,
        'mqtt_commands_supported': {
            'com3': {'versions_supported': [23], 'latest_version': 23},
        },
    },
    'device_park_profile': {
        'is_active': True,
        'group': {
            'id': '635ffb7b-8c06-476d-a30a-4bc9ae65d272',
            'name': '2pac',
        },
    },
    'thread_id': utils.to_base64('||has_everything').rstrip('='),
    'status': {
        'gnss': {
            'accuracy_m': 3.0,
            'direction_deg': 100.0,
            'lat': 53.3242,
            'lon': 34.9885,
            'speed_kmph': 10.0,
        },
        'iccid': '89310410106543789301',
        'is_online': False,
        'updated_at': '2020-08-11T11:50:03+00:00',
    },
}

RESPONSE_DEVICES_ELEM_2 = {
    'device': {
        'id': 'without_driver',
        'imei': '351756051523999',
        'mac_wlan0': 'a5:90:c5:98:95:48',
        'serial_number': 'AB2',
        'is_connection_available': False,
    },
    'device_park_profile': {'is_active': False},
    'thread_id': utils.to_base64('||without_driver').rstrip('='),
}

RESPONSE_DEVICES_ELEM_3 = {
    'device': {
        'id': 'just_device',
        'mac_wlan0': 'ca:ff:4d:64:f2:79',
        'serial_number': 'AB1',
        'is_connection_available': False,
    },
    'device_park_profile': {'is_active': False},
    'thread_id': utils.to_base64('||just_device').rstrip('='),
    'driver': {
        'id': 'd1',
        'last_name': 'Ivanov',
        'license_number': '7723306794',
        'phones': ['+79265975310'],
    },
    'vehicle': {'id': 'car1'},
}

RESPONSE_DEVICES_ELEM_4 = {
    'device': {
        'id': 'move_to_other_park',
        'mac_wlan0': '32:41:27:d5:fb:ed',
        'serial_number': 'AB3',
        'software_version': '2.031-1',
        'is_connection_available': True,
        'mqtt_commands_supported': {
            'com5': {'versions_supported': [228], 'latest_version': 228},
            'com6': {
                'versions_supported': [0, 1, 3, 5, 4],
                'latest_version': 5,
            },
        },
    },
    'device_park_profile': {
        'is_active': True,
        'subgroup': {
            'id': '3bd269aa-3aca-494b-8bbb-88f99847464a',
            'name': 'Shakur',
        },
        'group': {
            'id': '635ffb7b-8c06-476d-a30a-4bc9ae65d272',
            'name': '2pac',
        },
    },
    'thread_id': utils.to_base64('||move_to_other_park').rstrip('='),
    'driver': {
        'first_name': 'Sergey',
        'id': 'd2',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'license_number': '7723306796',
        'phones': ['+79265975311'],
    },
    'status': {
        'iccid': '89310410106543789300',
        'is_online': False,
        'updated_at': '2020-08-11T13:50:03+00:00',
    },
    'vehicle': {'id': 'car2', 'plate_number': 'E112KX750'},
}

RESPONSE_DEVICES_ELEM_5 = {
    'device': {
        'id': 'another_park',
        'mac_wlan0': '11:11:11:22:22:ff',
        'serial_number': 'AB4',
        'software_version': '2.0031-002',
        'is_connection_available': True,
        'mqtt_commands_supported': {
            'com1': {'versions_supported': [1, 0, 5, 4], 'latest_version': 5},
            'com2': {'versions_supported': [12], 'latest_version': 12},
        },
    },
    'device_park_profile': {
        'is_active': True,
        'subgroup': {
            'id': '1db9bcc6-982c-46ff-a161-78fa1817be01',
            'name': 'SouthWestHam',
        },
        'group': {
            'id': '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            'name': 'South',
        },
    },
    'thread_id': utils.to_base64('||another_park').rstrip('='),
    'driver': {
        'first_name': 'Alexey',
        'id': 'd3',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'license_number': '7723306790',
        'phones': ['+79265975510'],
    },
    'status': {
        'iccid': '89310410106543789300',
        'is_online': True,
        'uptime_ms': 300000,
        'updated_at': '2020-08-11T14:58:03+00:00',
    },
    'vehicle': {'id': 'car3', 'plate_number': 'X432HA777'},
}

RESPONSE_DEVICES_ELEM_6 = {
    'device': {
        'id': 'another_park_again',
        'mac_wlan0': '11:11:11:22:22:ff',
        'serial_number': 'AB5',
        'software_version': '000002.31-00002',
        'is_connection_available': True,
        'mqtt_commands_supported': {
            'com1': {'versions_supported': [1, 0, 5, 4], 'latest_version': 5},
            'com2': {'versions_supported': [12], 'latest_version': 12},
        },
    },
    'device_park_profile': {'is_active': True},
    'thread_id': utils.to_base64('||another_park_again').rstrip('='),
    'driver': {
        'id': 'd4',
        'last_name': 'Petrov',
        'license_number': '7723396794',
        'phones': ['+79266975310'],
    },
    'status': {
        'iccid': '89310410106543789300',
        'is_online': True,
        'uptime_ms': 300000,
        'updated_at': '2020-08-11T14:59:03+00:00',
    },
    'vehicle': {'id': 'car4'},
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db',
    files=['pg_signal_device_api_meta_db_testing_sort.sql'],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    SIGNAL_DEVICE_API_ADMIN_MQTT_COMMANDS={
        '__default__': {
            'com5': {'versions_supported': [228]},
            'com6': {'versions_supported': [0, 1, 3, 5, 4]},
        },
        '2.31-3': {'com3': {'versions_supported': [23]}},
        '2.31-2': {
            'com1': {'versions_supported': [1, 0, 5, 4]},
            'com2': {'versions_supported': [12]},
        },
    },
)
@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.parametrize(
    'sort, ignored_order_slices, expected_devices',
    [
        (
            {'by': 'plate_number', 'direction': 'asc'},
            [slice(0, 2), slice(2, 4)],
            [
                RESPONSE_DEVICES_ELEM_1,
                RESPONSE_DEVICES_ELEM_2,
                RESPONSE_DEVICES_ELEM_3,
                RESPONSE_DEVICES_ELEM_6,
                RESPONSE_DEVICES_ELEM_4,
                RESPONSE_DEVICES_ELEM_5,
            ],
        ),
        (
            {'by': 'plate_number', 'direction': 'desc'},
            [slice(2, 4), slice(4, 6)],
            [
                RESPONSE_DEVICES_ELEM_5,
                RESPONSE_DEVICES_ELEM_4,
                RESPONSE_DEVICES_ELEM_3,
                RESPONSE_DEVICES_ELEM_6,
                RESPONSE_DEVICES_ELEM_2,
                RESPONSE_DEVICES_ELEM_1,
            ],
        ),
        (
            {'by': 'drivers', 'direction': 'asc'},
            [slice(0, 2)],
            [
                RESPONSE_DEVICES_ELEM_1,
                RESPONSE_DEVICES_ELEM_2,
                RESPONSE_DEVICES_ELEM_3,
                RESPONSE_DEVICES_ELEM_5,
                RESPONSE_DEVICES_ELEM_4,
                RESPONSE_DEVICES_ELEM_6,
            ],
        ),
        (
            {'by': 'drivers', 'direction': 'desc'},
            [slice(4, 6)],
            [
                RESPONSE_DEVICES_ELEM_6,
                RESPONSE_DEVICES_ELEM_4,
                RESPONSE_DEVICES_ELEM_5,
                RESPONSE_DEVICES_ELEM_3,
                RESPONSE_DEVICES_ELEM_1,
                RESPONSE_DEVICES_ELEM_2,
            ],
        ),
        (
            {'by': 'serial_number', 'direction': 'asc'},
            [slice(0, 2)],
            [
                RESPONSE_DEVICES_ELEM_3,
                RESPONSE_DEVICES_ELEM_1,
                RESPONSE_DEVICES_ELEM_2,
                RESPONSE_DEVICES_ELEM_4,
                RESPONSE_DEVICES_ELEM_5,
                RESPONSE_DEVICES_ELEM_6,
            ],
        ),
        (
            {'by': 'serial_number', 'direction': 'desc'},
            [slice(4, 6)],
            [
                RESPONSE_DEVICES_ELEM_6,
                RESPONSE_DEVICES_ELEM_5,
                RESPONSE_DEVICES_ELEM_4,
                RESPONSE_DEVICES_ELEM_2,
                RESPONSE_DEVICES_ELEM_3,
                RESPONSE_DEVICES_ELEM_1,
            ],
        ),
        (
            {'by': 'software_version', 'direction': 'asc'},
            [slice(0, 2), slice(3, 5)],
            [
                RESPONSE_DEVICES_ELEM_3,
                RESPONSE_DEVICES_ELEM_2,
                RESPONSE_DEVICES_ELEM_4,
                RESPONSE_DEVICES_ELEM_6,
                RESPONSE_DEVICES_ELEM_5,
                RESPONSE_DEVICES_ELEM_1,
            ],
        ),
        (
            {'by': 'software_version', 'direction': 'desc'},
            [slice(1, 3), slice(4, 6)],
            [
                RESPONSE_DEVICES_ELEM_1,
                RESPONSE_DEVICES_ELEM_6,
                RESPONSE_DEVICES_ELEM_5,
                RESPONSE_DEVICES_ELEM_4,
                RESPONSE_DEVICES_ELEM_3,
                RESPONSE_DEVICES_ELEM_2,
            ],
        ),
        (
            {'by': 'status', 'direction': 'asc'},
            [slice(0, 2)],
            [
                RESPONSE_DEVICES_ELEM_3,
                RESPONSE_DEVICES_ELEM_2,
                RESPONSE_DEVICES_ELEM_1,
                RESPONSE_DEVICES_ELEM_4,
                RESPONSE_DEVICES_ELEM_5,
                RESPONSE_DEVICES_ELEM_6,
            ],
        ),
        (
            {'by': 'status', 'direction': 'desc'},
            [slice(4, 6)],
            [
                RESPONSE_DEVICES_ELEM_6,
                RESPONSE_DEVICES_ELEM_5,
                RESPONSE_DEVICES_ELEM_4,
                RESPONSE_DEVICES_ELEM_1,
                RESPONSE_DEVICES_ELEM_3,
                RESPONSE_DEVICES_ELEM_2,
            ],
        ),
    ],
)
async def test_devices_sort(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        parks,
        sort,
        ignored_order_slices,
        expected_devices,
        mockserver,
):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'park_id': 'p1',
                    'driver_id': 'd1',
                    'status': 'online',
                    'updated_ts': 12345,
                },
                {
                    'park_id': 'p1',
                    'driver_id': 'd2',
                    'status': 'online',
                    'updated_ts': 12345,
                },
                {
                    'park_id': 'p1',
                    'driver_id': 'd3',
                    'status': 'online',
                    'updated_ts': 12345,
                },
                {
                    'park_id': 'p1',
                    'driver_id': 'd4',
                    'status': 'online',
                    'updated_ts': 12345,
                },
            ],
        }

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

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE_2)
    parks.set_driver_profiles_response(DRIVER_PROFILES_LIST_2)

    request_body = {'limit': 100, 'sort': sort}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=request_body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json['limit'] == 100
    assert response_json['offset'] == 0

    assert utils.lists_are_equal_ignore_order_in_slices(
        response_json['devices'],
        expected_devices,
        ignored_slices=ignored_order_slices,
        key=lambda x: x['device']['id'],
    )


@pytest.mark.parametrize(
    'text_filter, offset, limit, '
    'drivers_list, cars_list, fleet_vehicles_response,'
    'exp_req_drivers_list, exp_req_cars_list, exp_req_fleet_vehicles,'
    'expected_response',
    [
        pytest.param(
            '',
            0,
            2,
            [DRIVER_PROFILES_LIST_DUPLICATE_CAR_BINDING],
            None,
            FLEET_VEHICLES_RESPONSE,
            None,
            None,
            None,
            {
                'devices': [
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
                        'driver': {
                            'first_name': 'Petr',
                            'id': 'd1',
                            'middle_name': 'D`',
                            'last_name': 'Ivanov',
                            'license_number': '7723306794',
                            'phones': ['+79265975310'],
                        },
                        'status': {'is_online': False},
                        'vehicle': CAR1,
                    },
                    {
                        'device': DEV2,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID2,
                        'status': {'is_online': False},
                        'vehicle': CAR2,
                    },
                ],
                'limit': 2,
                'offset': 0,
            },
            id='multi_no_text_query',
        ),
        pytest.param(
            'ABCD11',
            0,
            1,
            [DRIVER_PROFILES_LIST_DUPLICATE_CAR_BINDING],
            None,
            FLEET_VEHICLES_RESPONSE,
            None,
            None,
            None,
            {
                'devices': [
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
                        'driver': {
                            'first_name': 'Petr',
                            'id': 'd1',
                            'middle_name': 'D`',
                            'last_name': 'Ivanov',
                            'license_number': '7723306794',
                            'phones': ['+79265975310'],
                        },
                        'status': {'is_online': False},
                        'vehicle': CAR1,
                    },
                ],
                'limit': 1,
                'offset': 0,
            },
            id='multi_with_text_query',
        ),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['text_search.sql'])
@pytest.mark.now('2020-08-11 15:00:03 +00:00')
async def test_multiple_bond(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        parks,
        text_filter,
        offset,
        limit,
        drivers_list,
        cars_list,
        fleet_vehicles_response,
        exp_req_drivers_list,
        exp_req_cars_list,
        exp_req_fleet_vehicles,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'park_id': 'p1',
                    'driver_id': 'd1',
                    'status': 'online',
                    'updated_ts': 12345,
                },
                {
                    'park_id': 'p1',
                    'driver_id': 'd100500',
                    'status': 'offline',
                    'updated_ts': 12345,
                },
            ],
        }

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

    fleet_vehicles.set_fleet_vehicles_response(fleet_vehicles_response)
    parks.set_driver_profiles_response(drivers_list)
    parks.set_cars_list_response(cars_list)
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'query': {'text': text_filter},
            'offset': offset,
            'limit': limit,
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response
    assert fleet_vehicles.fleet_vehicles.times_called == (
        1 if fleet_vehicles_response else 0
    )

    if exp_req_fleet_vehicles:
        req = fleet_vehicles.fleet_vehicles.next_call()['request'].json
        ordered_object.assert_eq(req, exp_req_fleet_vehicles, ['id_in_set'])

    assert parks.driver_profiles_list.times_called == len(drivers_list)
    if exp_req_drivers_list:
        for exp_req in exp_req_drivers_list:
            req = parks.driver_profiles_list.next_call()['request'].json
            ordered_object.assert_eq(
                {
                    'limit': req['limit'],
                    'offset': req['offset'],
                    'car_ids': req['query']['park']['car']['id'],
                },
                exp_req,
                ['car_ids'],
            )

    assert parks.cars_list.times_called == (1 if cars_list else 0)
    if exp_req_cars_list:
        req = parks.cars_list.next_call()['request'].json
        ordered_object.assert_eq(
            {
                'limit': req['limit'],
                'offset': req['offset'],
                'car_ids': req['query']['park']['car']['id'],
            },
            exp_req_cars_list,
            ['car_ids'],
        )


@pytest.mark.parametrize(
    'offset, limit, '
    'drivers_list, cars_list, fleet_vehicles_response,'
    'exp_req_drivers_list, exp_req_cars_list, exp_req_fleet_vehicles,'
    'expected_response',
    [
        pytest.param(
            0,
            1,
            [DRIVER_PROFILES_LIST_DUPLICATE_CAR_BINDING],
            None,
            {
                'vehicles': [
                    {
                        'data': {'car_id': 'car1', 'number': 'О122КХ777'},
                        'park_id_car_id': 'p1_car1',
                        'revision': '0_1574328384_71',
                    },
                ],
            },
            None,
            None,
            None,
            {
                'devices': [
                    {
                        'device': DEV1,
                        'device_park_profile': {'is_active': True},
                        'thread_id': THREAD_ID1,
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
                                'updated_at': '2020-08-11T15:00:00+00:00',
                            },
                            'iccid': '89310410106543789301',
                            'is_online': False,
                            'updated_at': '2020-08-11T15:00:00+00:00',
                        },
                        'vehicle': CAR1,
                    },
                ],
                'limit': 1,
                'offset': 0,
            },
            id='driver_detected',
        ),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['driver_detected.sql'])
@pytest.mark.now('2020-08-11 16:00:03 +00:00')
async def test_driver_detected(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        parks,
        offset,
        limit,
        drivers_list,
        cars_list,
        fleet_vehicles_response,
        exp_req_drivers_list,
        exp_req_cars_list,
        exp_req_fleet_vehicles,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {
                    'park_id': 'p1',
                    'driver_id': 'd1',
                    'status': 'online',
                    'updated_ts': 12345,
                },
                {
                    'park_id': 'p1',
                    'driver_id': 'd100500',
                    'status': 'online',
                    'updated_ts': 12345,
                },
            ],
        }

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

    fleet_vehicles.set_fleet_vehicles_response(fleet_vehicles_response)
    parks.set_driver_profiles_response(drivers_list)
    parks.set_cars_list_response(cars_list)
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'offset': offset, 'limit': limit},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response
    assert fleet_vehicles.fleet_vehicles.times_called == (
        1 if fleet_vehicles_response else 0
    )

    if exp_req_fleet_vehicles:
        req = fleet_vehicles.fleet_vehicles.next_call()['request'].json
        ordered_object.assert_eq(req, exp_req_fleet_vehicles, ['id_in_set'])

    assert parks.driver_profiles_list.times_called == len(drivers_list)
    if exp_req_drivers_list:
        for exp_req in exp_req_drivers_list:
            req = parks.driver_profiles_list.next_call()['request'].json
            ordered_object.assert_eq(
                {
                    'limit': req['limit'],
                    'offset': req['offset'],
                    'car_ids': req['query']['park']['car']['id'],
                },
                exp_req,
                ['car_ids'],
            )

    assert parks.cars_list.times_called == (1 if cars_list else 0)
    if exp_req_cars_list:
        req = parks.cars_list.next_call()['request'].json
        ordered_object.assert_eq(
            {
                'limit': req['limit'],
                'offset': req['offset'],
                'car_ids': req['query']['park']['car']['id'],
            },
            exp_req_cars_list,
            ['car_ids'],
        )


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.now('2020-08-11 15:00:03 +00:00')
async def test_return_active(
        taxi_signal_device_api_admin, fleet_vehicles, parks, mockserver,
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

    request_body = {'limit': 100, 'include_deleted_devices': False}

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=request_body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'devices': [
            {
                'device': {
                    'id': 'has_everything',
                    'imei': '990000862471854',
                    'mac_wlan0': '07:f2:74:af:8b:b1',
                    'serial_number': 'AB1',
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
            {
                'device': {
                    'id': 'without_driver',
                    'imei': '351756051523999',
                    'mac_wlan0': 'a5:90:c5:98:95:48',
                    'serial_number': 'AB12FE45DD',
                    'software_version': '2.31.32-3',
                    'is_connection_available': True,
                },
                'device_park_profile': {'is_active': True},
                'thread_id': utils.to_base64('||without_driver').rstrip('='),
                'status': {
                    'gnss': {
                        'lat': 73.3242,
                        'lon': 54.9885,
                        'updated_at': '2020-08-11T14:00:00+00:00',
                    },
                    'iccid': '89310410106543789300',
                    'is_online': False,
                    'updated_at': '2020-08-11T14:50:00+00:00',
                },
                'vehicle': {'id': 'car2', 'plate_number': 'О122КХ178'},
            },
            {
                'device': {
                    'id': 'just_device',
                    'mac_wlan0': 'ca:ff:4d:64:f2:79',
                    'serial_number': 'FFEE33',
                    'is_connection_available': False,
                },
                'device_park_profile': {'is_active': True},
                'thread_id': utils.to_base64('||just_device').rstrip('='),
                'status': {'is_online': False},
            },
        ],
        'limit': 100,
        'offset': 0,
    }

    assert fleet_vehicles.fleet_vehicles.times_called == 1
    fleet_vehicles_request = fleet_vehicles.fleet_vehicles.next_call()[
        'request'
    ].json
    assert fleet_vehicles_request == {'id_in_set': ['p1_car1', 'p1_car2']}

    assert parks.driver_profiles_list.times_called == 1
    parks_request = parks.driver_profiles_list.next_call()['request'].json
    assert parks_request == {
        'query': {'park': {'id': 'p1', 'car': {'id': ['car1', 'car2']}}},
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
        'limit': 200,
        'offset': 0,
    }


DEMO_DEVICES_RESPONSE = [
    {
        'device': {
            'id': 'dev1',
            'mac_wlan0': '11111',
            'serial_number': '11111',
            'is_connection_available': False,
        },
        'device_park_profile': {
            'is_active': True,
            'group': {'id': 'g1', 'name': 'SuperWeb'},
            'subgroup': {'id': 'sg1', 'name': 'SignalQ'},
        },
        'thread_id': utils.to_base64('||dev1').rstrip('='),
        'driver': {
            'first_name': 'Roman',
            'id': 'dr1',
            'last_name': 'Maresov',
            'phones': ['+77777777777'],
        },
        'status': {'is_online': True},
        'vehicle': {'id': 'v1', 'plate_number': 'Y777RM'},
    },
    {
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
    {
        'device': {
            'id': 'dev3',
            'mac_wlan0': '33333',
            'serial_number': '33333',
            'is_connection_available': False,
        },
        'device_park_profile': {'is_active': False},
        'thread_id': utils.to_base64('||dev3').rstrip('='),
        'status': {'is_online': True},
    },
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
        'vehicles': web_common.DEMO_VEHICLES,
        'groups': web_common.DEMO_GROUPS,
        'drivers': web_common.DEMO_DRIVERS,
    },
)
@pytest.mark.parametrize('text_filter', [None, '', ' Ro ', ' 11  '])
async def test_demo_devices_list_all(
        taxi_signal_device_api_admin, text_filter, mockserver,
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

    request_body = {'limit': 100}
    if text_filter:
        request_body['query'] = {'text': text_filter}

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=request_body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no_such_park'},
    )
    assert response.status_code == 200, response.text

    response_json = response.json()
    for device in response_json['devices']:
        assert 'status' in device
        assert 'gnss' in device['status']
        del device['status']['gnss']

    assert response_json == {
        'devices': DEMO_DEVICES_RESPONSE,
        'limit': 100,
        'offset': 0,
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
    'text_filter, group_id, expected_response',
    [
        pytest.param(
            ' Roman ', 'sg1', DEMO_DEVICES_RESPONSE[0:1], id='Maresov device',
        ),
        pytest.param(
            ' 7777 ',
            None,
            DEMO_DEVICES_RESPONSE[0:2],
            id='phone and serial search',
        ),
        pytest.param(None, 'g2', DEMO_DEVICES_RESPONSE[1:2], id='one group'),
        pytest.param(' Shuleyko ', None, [], id='no device'),
    ],
)
async def test_demo_devices_list_filter(
        taxi_signal_device_api_admin,
        text_filter,
        group_id,
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

    request_body = {'limit': 100}
    if text_filter:
        request_body['query'] = {'text': text_filter}
    if group_id:
        request_body['filter'] = {'group_id': group_id}

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=request_body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no_such_park'},
    )
    assert response.status_code == 200, response.text

    response_json = response.json()
    for device in response_json['devices']:
        assert 'status' in device
        assert 'gnss' in device['status']
        del device['status']['gnss']

    assert response_json == {
        'devices': expected_response,
        'limit': 100,
        'offset': 0,
    }
